"""Reviewed "teach" store: short rules and facts the owner approves, added to chat requests.

Nothing here changes the model's weights and nothing is learned automatically. The owner adds,
lists, disables and deletes entries with the command line below. For each request, the entries
that apply are placed in the system message, inside a fixed budget, without ever truncating an
entry or pushing a request over the gateway's limit.

    python teach_store.py add                 # asks for the text (keeps it out of shell history)
    python teach_store.py add "Always answer code questions with a short test." --kind rule
    python teach_store.py add "My project uses Python 3.12." --kind fact --when python,version
    python teach_store.py list [--all]
    python teach_store.py disable t003 | enable t003 | delete t003
    python teach_store.py preview "how do I parse a date in python?"

Data lives in .runtime/teach/ (ignored by git): store.json, store.json.bak (previous version)
and audit.jsonl (every change, append-only). Entries are plain text and are sent to the local
model, so do not store passwords or keys; key-shaped text is refused.

Standard library only. This module never opens a network connection.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DIR = ROOT / ".runtime" / "teach"
KINDS = ("rule", "fact", "correction")
MAX_TEXT_CHARS = 300
MAX_ENTRIES = 500
MAX_KEYWORDS = 8
DEFAULT_BUDGET_UNITS = 320          # same units as the gateway: UTF-8 bytes of message text
# Notes are background from the owner. They do not outrank the gateway's rules or what the
# user asks for in the current message.
HEADER = "Owner's saved notes (the current request takes priority if they conflict):"
SECRET_SHAPES = (
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\b[A-Fa-f0-9]{40,}\b"),
    re.compile(r"\b[A-Za-z0-9+/_\-]{48,}={0,2}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)
# Arabic short vowels, superscript alef and tatweel: ignored when matching keywords.
ARABIC_MARKS = re.compile("[ً-ْٰـ]")
WORD = re.compile(r"\w+", re.UNICODE)


class TeachError(ValueError):
    """A request the store refuses; the message is safe to show."""


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tokens(text: str) -> list[str]:
    return WORD.findall(ARABIC_MARKS.sub("", unicodedata.normalize("NFC", text)).casefold())


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        raise TeachError("Text must be a string.")
    text = unicodedata.normalize("NFC", text).strip()
    if any(unicodedata.category(ch) in ("Cc", "Cs", "Co", "Cn") for ch in text):
        raise TeachError("Use one line of plain text (no line breaks or control characters).")
    text = " ".join(text.split())
    if not 1 <= len(text) <= MAX_TEXT_CHARS:
        raise TeachError(f"Text must be 1 to {MAX_TEXT_CHARS} characters.")
    if any(shape.search(text) for shape in SECRET_SHAPES):
        raise TeachError("This looks like a key or password. Entries are stored and sent as plain text; not saved.")
    return text


def clean_keywords(raw) -> list[str]:
    if raw in (None, "", []):
        return []
    items = raw.split(",") if isinstance(raw, str) else list(raw)
    cleaned = []
    for item in items:
        words = tokens(str(item))
        if words and " ".join(words) not in cleaned:
            cleaned.append(" ".join(words))
    if len(cleaned) > MAX_KEYWORDS:
        raise TeachError(f"At most {MAX_KEYWORDS} keywords.")
    return cleaned


class Store:
    """All entries, in one JSON file that is replaced atomically on every change."""

    def __init__(self, folder: Path = DEFAULT_DIR):
        self.folder = Path(folder)
        self.path = self.folder / "store.json"
        self.audit_path = self.folder / "audit.jsonl"
        self.data = {"version": 1, "next_id": 1, "entries": []}
        if self.path.exists():
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or loaded.get("version") != 1 \
                    or not isinstance(loaded.get("entries"), list):
                raise TeachError("store.json has an unknown format; not touched.")
            self.data = loaded

    # -- reading ---------------------------------------------------------------------------
    def entries(self, include_inactive: bool = False) -> list[dict]:
        return [e for e in self.data["entries"]
                if e["status"] == "active" or (include_inactive and e["status"] == "disabled")]

    def get(self, entry_id: str) -> dict:
        for entry in self.data["entries"]:
            if entry["id"] == entry_id and entry["status"] != "deleted":
                return entry
        raise TeachError(f"No entry {entry_id}.")

    # -- writing ---------------------------------------------------------------------------
    def _save(self, action: str, entry: dict) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            os.replace(self.path, self.path.with_suffix(".json.bak"))
        temp = self.path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        os.replace(temp, self.path)
        record = {"time": now(), "action": action, "id": entry["id"], "kind": entry["kind"],
                  "text": entry["text"], "when": entry["when"]}
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def add(self, text: str, kind: str = "rule", when=None) -> dict:
        if kind not in KINDS:
            raise TeachError("Kind must be one of: " + ", ".join(KINDS) + ".")
        text = clean_text(text)
        keywords = clean_keywords(when)
        live = [e for e in self.data["entries"] if e["status"] != "deleted"]
        if len(live) >= MAX_ENTRIES:
            raise TeachError(f"The store is full ({MAX_ENTRIES} entries). Delete some first.")
        if any(e["text"].casefold() == text.casefold() for e in live):
            raise TeachError("The same text is already stored.")
        entry = {"id": f"t{self.data['next_id']:03d}", "kind": kind, "text": text, "when": keywords,
                 "status": "active", "created": now(), "source": "owner"}
        self.data["next_id"] += 1
        self.data["entries"].append(entry)
        self._save("add", entry)
        return entry

    def set_status(self, entry_id: str, status: str) -> dict:
        entry = self.get(entry_id)
        entry["status"] = status
        self._save(status, entry)
        return entry


def line_for(entry: dict) -> str:
    prefix = {"rule": "- ", "fact": "- Fact: ", "correction": "- Correction: "}[entry["kind"]]
    return prefix + entry["text"]


def select(entries: list[dict], query: str, budget_units: int) -> list[dict]:
    """Entries to inject for this user message: always-on first, then keyword matches.

    Deterministic. An entry is included whole or not at all. The budget counts UTF-8 bytes of
    the block that will be added, header included.
    """
    words = set(tokens(query))
    always = [e for e in entries if not e["when"]]
    matched = []
    for entry in entries:
        if entry["when"]:
            hits = sum(1 for keyword in entry["when"] if set(keyword.split()) <= words)
            if hits:
                matched.append((-hits, entry["created"], entry["id"], entry))
    ordered = always + [item[3] for item in sorted(matched, key=lambda item: item[:3])]
    chosen, used = [], len(HEADER.encode("utf-8"))
    for entry in ordered:
        cost = len(("\n" + line_for(entry)).encode("utf-8"))
        if used + cost <= budget_units:
            chosen.append(entry)
            used += cost
    return chosen


def block_for(chosen: list[dict]) -> str:
    return "\n".join([HEADER] + [line_for(e) for e in chosen]) if chosen else ""


def request_units(messages: list[dict], limits: dict, output_tokens: int) -> int:
    """The gateway's own admission arithmetic (chat_contract.validate_chat), restated."""
    return limits["context_reserve_units"] + output_tokens + sum(
        len(m["content"].encode("utf-8")) + limits["per_message_overhead_units"] for m in messages)


def apply_to_messages(messages: list[dict], entries: list[dict], limits: dict, output_tokens: int,
                      budget_units: int = DEFAULT_BUDGET_UNITS) -> tuple[list[dict], list[str]]:
    """Return (new message list, ids used). The input list is not modified.

    The block goes at the end of an existing leading system message, or into a new one. If the
    request has no room, fewer entries (or none) are added: this never makes a request that
    passed the gateway's check exceed it.
    """
    if not messages or messages[-1].get("role") != "user":
        return list(messages), []
    has_system = messages[0].get("role") == "system"
    if not has_system and len(messages) >= limits["max_messages"]:
        return list(messages), []
    room = limits["context_tokens"] - request_units(messages, limits, output_tokens)
    room -= 2 if has_system else limits["per_message_overhead_units"]     # "\n\n" or a new message
    chosen = select(entries, messages[-1]["content"], min(budget_units, room))
    if not chosen:
        return list(messages), []
    block = block_for(chosen)
    result = [dict(m) for m in messages]
    if has_system:
        result[0]["content"] = result[0]["content"] + "\n\n" + block
    else:
        result.insert(0, {"role": "system", "content": block})
    if request_units(result, limits, output_tokens) > limits["context_tokens"]:
        return list(messages), []                                         # defensive; should not happen
    return result, [e["id"] for e in chosen]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Reviewed rules and facts for the local assistant.")
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add", help="store a new rule, fact or correction")
    add.add_argument("text", nargs="?")
    add.add_argument("--kind", choices=KINDS, default="rule")
    add.add_argument("--when", default="", help="comma-separated keywords; without them the entry always applies")
    listing = sub.add_parser("list", help="show stored entries")
    listing.add_argument("--all", action="store_true", help="include disabled entries")
    for name in ("disable", "enable", "delete"):
        sub.add_parser(name).add_argument("id")
    preview = sub.add_parser("preview", help="show what would be added for a message; sends nothing")
    preview.add_argument("message")
    preview.add_argument("--budget", type=int, default=DEFAULT_BUDGET_UNITS)
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    try:
        store = Store(args.dir)
        if args.command == "add":
            text = args.text if args.text is not None else input("Text to teach (one line): ")
            entry = store.add(text, args.kind, args.when)
            print(f"Saved {entry['id']} ({entry['kind']}): {entry['text']}")
            print("Applies " + ("when the message mentions: " + ", ".join(entry["when"]) if entry["when"] else "to every chat."))
        elif args.command == "list":
            rows = store.entries(include_inactive=args.all)
            if not rows:
                print("Nothing stored yet.")
            for entry in rows:
                scope = "when: " + ", ".join(entry["when"]) if entry["when"] else "always"
                flag = "" if entry["status"] == "active" else " [disabled]"
                print(f"{entry['id']}  {entry['kind']:<10} {scope:<28} {entry['text']}{flag}")
        elif args.command in ("disable", "enable", "delete"):
            status = {"disable": "disabled", "enable": "active", "delete": "deleted"}[args.command]
            entry = store.set_status(args.id, status)
            print(f"{entry['id']} is now {status}.")
        elif args.command == "preview":
            chosen = select(store.entries(), args.message, args.budget)
            print(block_for(chosen) or "(nothing would be added)")
            print(f"\n{len(chosen)} of {len(store.entries())} active entries; "
                  f"{len(block_for(chosen).encode('utf-8'))} of {args.budget} budget units.")
    except TeachError as error:
        print("Not done: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
