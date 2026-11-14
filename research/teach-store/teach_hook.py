"""Gateway hook that adds the owner's reviewed notes to chat requests. NOT ENABLED BY DEFAULT.

The gateway loads this only if its configuration lists the callback:

    "litellm_settings": { ..., "callbacks": ["teach_hook.teach"] }

That line is not in litellm.base.json. Adding it changes what the model receives, needs a
gateway restart, and should be reviewed and tested first (see TEACH.md).

Behaviour: runs after the gateway's own request check has passed. It re-reads the store on
every request, so a new rule applies without a restart. If anything goes wrong it leaves the
request exactly as it was: teaching can never block a chat. It writes only entry ids (never
their text) to the gateway log.
"""
from __future__ import annotations

from pathlib import Path

from chat_contract import read_json, validate_settings
from teach_store import DEFAULT_BUDGET_UNITS, DEFAULT_DIR, Store, apply_to_messages

ROOT = Path(__file__).resolve().parent


def inject(data: dict, limits: dict, folder: Path = DEFAULT_DIR,
           budget_units: int = DEFAULT_BUDGET_UNITS) -> tuple[dict, list[str]]:
    """Return (request data, ids used). Never raises; on any problem returns data unchanged."""
    try:
        messages = data.get("messages")
        if not isinstance(messages, list) or not all(
                isinstance(m, dict) and set(m) == {"role", "content"} and isinstance(m["content"], str)
                for m in messages):
            return data, []
        output = data.get("max_tokens", limits["default_output_tokens"])
        if type(output) is not int:
            return data, []
        entries = Store(folder).entries()
        if not entries:
            return data, []
        new_messages, used = apply_to_messages(messages, entries, limits, output, budget_units)
        if not used:
            return data, []
        changed = dict(data)
        changed["messages"] = new_messages
        return changed, used
    except Exception:          # deliberate: a broken store must not break chat
        return data, []


try:
    from litellm.integrations.custom_logger import CustomLogger
except Exception:              # the module stays importable (and testable) without the gateway
    CustomLogger = object


class TeachHook(CustomLogger):
    def __init__(self):
        super().__init__()
        self.limits = validate_settings(read_json(ROOT / "settings.json"))

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if call_type not in ("completion", "acompletion"):
            return data
        changed, used = inject(data, self.limits)
        if used:
            print("[teach] added entries: " + ",".join(used), flush=True)
        return changed


def _make():
    try:
        return TeachHook()
    except Exception:
        return None


teach = _make()
