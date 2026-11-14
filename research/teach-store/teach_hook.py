"""Gateway hook that adds the owner's reviewed notes to chat requests.

The gateway loads this only if its configuration lists the callback:

    "litellm_settings": { ..., "callbacks": ["teach_hook.teach"] }

Adding or removing that line changes what the model receives and needs a gateway restart.
TEACH.md records whether it is currently enabled.

Behaviour: runs after the gateway's own request check has passed. Applying it twice to the
same request adds nothing the second time. It re-reads the store on
every request, so a new rule applies without a restart. If anything goes wrong it leaves the
request exactly as it was: teaching can never block a chat. It writes only entry ids and a
store fingerprint (never note text) to the gateway log, and a failure to write that line is
ignored. The ids and the fingerprint come from the same single read of the store.
"""
from __future__ import annotations

from pathlib import Path

from teach_store import DEFAULT_BUDGET_UNITS, DEFAULT_DIR, apply_to_messages, snapshot

ROOT = Path(__file__).resolve().parent


def inject_with_evidence(data: dict, limits: dict, folder: Path = DEFAULT_DIR,
                         budget_units: int = DEFAULT_BUDGET_UNITS) -> tuple[dict, list[str], str]:
    """Return (request data, ids used, store fingerprint). Never raises.

    The ids and the fingerprint come from the same single read of the store that the injected
    notes were selected from, so they always describe one and the same version. On any problem
    the request is returned unchanged with no ids and the fingerprint "unknown".
    """
    try:
        messages = data.get("messages")
        if not isinstance(messages, list) or not all(
                isinstance(m, dict) and set(m) == {"role", "content"} and isinstance(m["content"], str)
                for m in messages):
            return data, [], "not-read"
        output = data.get("max_tokens", limits["default_output_tokens"])
        if type(output) is not int:
            return data, [], "not-read"
        entries, fingerprint = snapshot(folder)
        if not entries:
            return data, [], fingerprint
        new_messages, used = apply_to_messages(messages, entries, limits, output, budget_units)
        if not used:
            return data, [], fingerprint
        changed = dict(data)
        changed["messages"] = new_messages
        return changed, used, fingerprint
    except Exception:          # deliberate: a broken store must not break chat
        return data, [], "unknown"


def inject(data: dict, limits: dict, folder: Path = DEFAULT_DIR,
           budget_units: int = DEFAULT_BUDGET_UNITS) -> tuple[dict, list[str]]:
    """Return (request data, ids used). Never raises; on any problem returns data unchanged."""
    changed, used, _ = inject_with_evidence(data, limits, folder, budget_units)
    return changed, used


def log_line(used: list[str], fingerprint: str) -> str:
    """What the hook writes to the gateway log: entry numbers and the store fingerprint, never text."""
    if used:
        return f"[teach] added {len(used)} entries: {','.join(used)} | store {fingerprint}"
    return f"[teach] nothing added | store {fingerprint}"


def safe_log(line: str) -> None:
    """Diagnostics must never break a chat: a closed or broken log pipe is ignored."""
    try:
        print(line, flush=True)
    except Exception:
        pass


try:
    from litellm.integrations.custom_logger import CustomLogger
except Exception:              # the module stays importable (and testable) without the gateway
    CustomLogger = object


class TeachHook(CustomLogger):
    def __init__(self):
        super().__init__()
        from chat_contract import read_json, validate_settings     # the gateway's own settings loader
        self.limits = validate_settings(read_json(ROOT / "settings.json"))

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if call_type not in ("completion", "acompletion"):
            return data
        changed, used, fingerprint = inject_with_evidence(data, self.limits)
        safe_log(log_line(used, fingerprint))
        return changed


def _make():
    try:
        return TeachHook()
    except Exception:
        return None


teach = _make()
