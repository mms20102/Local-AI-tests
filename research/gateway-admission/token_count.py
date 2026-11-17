"""Real prompt-token count for a text chat request, as the installed engine renders it.

Optional. The gateway works without this module's dependency: when the `tokenizers` package or
the pinned tokenizer file is missing, `load_counter` returns None and the gateway keeps its
conservative byte rule (chat_contract.validate_chat).

The rendering mirrors Colibri 2.0.0 `render_chat_qwen` for a text-only request with thinking
off, read from the installed source:

    <|im_start|>system\\n{text}<|im_end|>\\n            only when the first message is a system message
    <|im_start|>user\\n{text}<|im_end|>\\n
    <|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n{text}<|im_end|>\\n     a past assistant turn
    <|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n                       the generation prompt

Every text is stripped, as the engine does. Past assistant turns are rendered with their empty
think block. That is the engine's default when thinking is off, and it is also the longer of the
two forms the engine can use, so the count is never below the engine's for this reason.

Evidence: for 24 system-plus-user requests the engine's reported prompt count equalled this
render counted with the same tokenizer file (difference 0 in all 24). Multi-turn history and
Arabic text are rendered from source and are NOT yet confirmed against engine usage, which is
why the gateway adds a margin.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Callable, Optional

DEFAULT_TOKENIZER = Path(r"C:\Users\User\colibri-models\qwen36-35b\tokenizer.json")
# SHA-256 of the tokenizer file the 24-row comparison used. Another file means another
# vocabulary, so the counter refuses to load and the gateway falls back to bytes.
PINNED_SHA256 = "5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42"
GENERATION_PROMPT = "<|im_start|>assistant\n<think>\n\n</think>\n\n"

# The one served profile this module's render and counts were checked against. The launcher
# reports what it actually started (TRYOUT_SERVED_PROFILE); real counting is used only when
# every field matches. Anything else, for example the 2.1.0 launcher, a different context or
# thinking switched on, leaves the gateway on the byte rule.
PROFILE = {
    "engine": "2.0.0",
    # SHA-256 of the installed openai_server.py that holds render_chat_qwen, the renderer mirrored above.
    "renderer_sha256": "67817219f7e7bb649eaae4f3570e7e43e9d4f388a7de1ea4b9031ad15bd7e43d",
    "thinking": "off",
    "context": 2048,
    "tokenizer_sha256": PINNED_SHA256,
}
REASONS = ("ok", "no-profile-reported", "profile-unreadable", "profile-mismatch", "context-mismatch",
           "tokenizer-unavailable")


def load_bound_counter(served_json: Optional[str], limits: dict, path: Optional[Path] = None
                       ) -> tuple[Optional[Callable[[list[dict]], int]], str]:
    """Return (counter or None, reason). The reason is always one of REASONS, a fixed word that is
    safe to log. The counter is returned only when the launcher's report of what it started
    equals PROFILE field by field, the gateway's own context setting equals PROFILE's, and the
    pinned tokenizer loads."""
    if not served_json:
        return None, "no-profile-reported"
    try:
        import json
        served = json.loads(served_json)
        if not isinstance(served, dict):
            raise ValueError
    except Exception:
        return None, "profile-unreadable"
    if served != PROFILE:
        return None, "profile-mismatch"
    if limits.get("context_tokens") != PROFILE["context"]:
        return None, "context-mismatch"
    counter = load_counter(path, PROFILE["tokenizer_sha256"])
    return (counter, "ok") if counter else (None, "tokenizer-unavailable")


def served_profile(engine_version: str, command: list, runtime_folder: Path, tokenizer: Path = DEFAULT_TOKENIZER) -> str:
    """What the launcher is about to start, as JSON, read from the real command line and files.
    Called by the launcher; never raises: a field it cannot establish is reported as "unknown",
    which cannot match PROFILE."""
    def file_hash(p):
        try:
            return hashlib.sha256(Path(p).read_bytes()).hexdigest()
        except Exception:
            return "unknown"
    try:
        context = int(command[command.index("--ctx") + 1])
    except Exception:
        context = "unknown"
    import json
    return json.dumps({
        "engine": engine_version,
        "renderer_sha256": file_hash(Path(runtime_folder) / "openai_server.py"),
        "thinking": "off" if "--no-think" in command else "on",
        "context": context,
        "tokenizer_sha256": file_hash(tokenizer),
    }, sort_keys=True)


def render(messages: list[dict]) -> str:
    """The prompt text for already validated messages (role and string content only)."""
    parts = []
    for index, message in enumerate(messages):
        role, text = message["role"], message["content"].strip()
        if role == "assistant":
            parts.append(f"<|im_start|>assistant\n<think>\n\n</think>\n\n{text}<|im_end|>\n")
        else:
            # A system message that is not first is refused by the engine itself; it is still
            # counted here so the number is never too small.
            parts.append(f"<|im_start|>{role}\n{text}<|im_end|>\n")
    parts.append(GENERATION_PROMPT)
    return "".join(parts)


def load_counter(path: Optional[Path] = None, pinned: Optional[str] = PINNED_SHA256
                 ) -> Optional[Callable[[list[dict]], int]]:
    """Return count(messages) -> prompt tokens, or None when real counting is unavailable."""
    path = Path(path) if path else DEFAULT_TOKENIZER
    try:
        data = path.read_bytes()
        if pinned is not None and hashlib.sha256(data).hexdigest() != pinned:
            return None
        from tokenizers import Tokenizer
        tokenizer = Tokenizer.from_str(data.decode("utf-8"))
    except Exception:
        return None

    def count(messages: list[dict]) -> int:
        return len(tokenizer.encode(render(messages), add_special_tokens=False).ids)

    return count
