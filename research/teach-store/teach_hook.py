"""Gateway hook that adds the owner's reviewed notes to chat requests.

The gateway loads this only if its configuration lists the callback:

    "litellm_settings": { ..., "callbacks": ["teach_hook.teach"] }

Adding or removing that line changes what the model receives and needs a gateway restart.
TEACH.md records whether it is currently enabled.

Behaviour: runs after the gateway's own request check has passed. Applying it twice to the
same request adds nothing the second time. It re-reads the store on
every request, so a new rule applies without a restart. If anything goes wrong it returns the
request data it was given, so teaching never fails a chat request. It can delay one: the store
file is read, and one log line written, inside the request. A locked store file is retried for
at most about 0.1 s (STORE_READ_ATTEMPTS) and then skipped for that request; the time of the
read and of the log write themselves is not bounded here. It writes only entry ids and a
store fingerprint (never note text) to the gateway log, and a failure to write that line is
ignored. The ids and the fingerprint come from the same single read of the store.

"Returns the request data it was given" is what this module does and what its tests check. It
is not a claim about the bytes the gateway finally sends to the engine.
"""
from __future__ import annotations

import re
from pathlib import Path

from teach_store import DEFAULT_BUDGET_UNITS, DEFAULT_DIR, apply_with_status, snapshot_full

ROOT = Path(__file__).resolve().parent
STORE_READ_ATTEMPTS = 3        # reads of a locked store file inside one request, 50 ms apart


def inject_with_status(data: dict, limits: dict, folder: Path = DEFAULT_DIR,
                       budget_units: int = DEFAULT_BUDGET_UNITS, count_tokens=None
                       ) -> tuple[dict, list[str], str, dict]:
    """Return (request data, ids used, store fingerprint, status). Never raises.

    With count_tokens, notes for a long request are budgeted in real tokens (see
    teach_store.apply_with_status). status is a dict of counts, all zero when there is nothing
    to report:
      "note_cap"  applicable entries left out because they exceed the size cap for notes;
      "no_room"   applicable entries left out because the request had no room;
      "invalid"   entries marked active in the store that are malformed and were skipped.
    The question and the history are sent regardless. A store that could not be read at all is
    reported through the fingerprint "unknown", not through these counts.
    """
    none = {"note_cap": 0, "no_room": 0, "invalid": 0}
    try:
        messages = data.get("messages")
        if not isinstance(messages, list) or not all(
                isinstance(m, dict) and set(m) == {"role", "content"} and isinstance(m["content"], str)
                for m in messages):
            return data, [], "not-read", none
        output = data.get("max_tokens", limits["default_output_tokens"])
        if type(output) is not int:
            return data, [], "not-read", none
        # One read: the entries, the fingerprint and the invalid count describe the same bytes.
        entries, fingerprint, invalid = snapshot_full(folder, STORE_READ_ATTEMPTS)
        if not entries:
            return data, [], fingerprint, dict(none, invalid=invalid)
        new_messages, used, left_out = apply_with_status(messages, entries, limits, output, budget_units,
                                                         count_tokens)
        status = dict(left_out, invalid=invalid)
        if not used:
            return data, [], fingerprint, status
        changed = dict(data)
        changed["messages"] = new_messages
        return changed, used, fingerprint, status
    except Exception:          # deliberate: a broken store must not break chat
        return data, [], "unknown", none


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
        entries, fingerprint, _ = snapshot_full(folder, STORE_READ_ATTEMPTS)
        if not entries:
            return data, [], fingerprint
        new_messages, used, _ = apply_with_status(messages, entries, limits, output, budget_units)
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


ID_FORM = re.compile(r"t[0-9]{3,9}")
FINGERPRINT_FORM = re.compile(r"[0-9a-f]{12}|none|unknown|not-read")


STATUS_LABELS = (("note_cap", "omitted-note-cap"), ("no_room", "omitted-no-room"), ("invalid", "skipped-invalid"))


def log_line(used, fingerprint, status=None) -> str:
    """What the hook writes to the gateway log.

    Only values in a known, harmless form are written: entry ids exactly as the store issues
    them ("t" and digits) and a fingerprint that is 12 hex digits or one of the fixed words.
    Anything else is never echoed: a malformed id is counted ("invalid:N") and a malformed
    fingerprint is written as "invalid". So the line cannot carry note text or other content
    that reached it through a damaged store, and it never shows the value's own text.
    """
    items = used if isinstance(used, (list, tuple)) else []
    good = [item for item in items if type(item) is str and ID_FORM.fullmatch(item)]
    bad = len(items) - len(good) + (0 if isinstance(used, (list, tuple)) else 1)
    mark = fingerprint if type(fingerprint) is str and FINGERPRINT_FORM.fullmatch(fingerprint) else "invalid"
    counts = status if isinstance(status, dict) else {}
    left_out = "".join(f" | {label}:{counts[key]}" for key, label in STATUS_LABELS
                       if type(counts.get(key)) is int and 0 < counts[key] < 10**6)
    if not good and not bad:
        return f"[teach] nothing added{left_out} | store {mark}"
    line = f"[teach] added {len(good)} entries: {','.join(good) or '-'}"
    if bad:
        line += f" | invalid:{bad}"
    return line + left_out + f" | store {mark}"


def safe_log(used, fingerprint, status=None) -> None:
    """Diagnostics must never break a chat.

    Building the line and writing it are both inside the guard, so neither odd values nor a
    closed or broken log pipe can raise into the request. Limit: a write that BLOCKS does not
    raise, so this does not bound how long logging can take; the gateway's log pipe is drained
    continuously by the launcher, and nothing here adds a timeout.
    """
    try:
        print(log_line(used, fingerprint, status), flush=True)
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
        try:                                    # real token counting is optional; None means bytes only
            from token_count import load_counter
            self.count_tokens = load_counter()
        except Exception:
            self.count_tokens = None

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if call_type not in ("completion", "acompletion"):
            return data
        changed, used, fingerprint, status = inject_with_status(
            data, self.limits, count_tokens=getattr(self, "count_tokens", None))
        safe_log(used, fingerprint, status)
        return changed


def _make():
    try:
        return TeachHook()
    except Exception:
        return None


teach = _make()
