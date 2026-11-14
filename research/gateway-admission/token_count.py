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
