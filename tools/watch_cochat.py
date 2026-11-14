"""Watch the shared co-chat log and notify each assistant when someone else replies.

Standard library only. It runs `git fetch` in this clone, never pulls, merges,
commits or pushes, and never talks to a model.

A script cannot wake a chat session by itself. What it does on every new reply:
  1. prints one line to stdout  (a session that watches this process wakes on it);
  2. appends the event to an inbox file per reader:
        .notify/for-claude.jsonl     replies NOT written by Claude
        .notify/for-chatgpt.jsonl    replies NOT written by ChatGPT
        .notify/for-chatgpt-latest.md   ready-to-paste text for the ChatGPT chat
  3. with --toast, shows a Windows notification so Mohamed can relay it.

Usage:
    python tools/watch_cochat.py                 # poll every 60 s until stopped
    python tools/watch_cochat.py --once          # one check, then exit
    python tools/watch_cochat.py --toast         # also show a desktop notification
    python tools/watch_cochat.py --since <sha>   # report everything after <sha>

Exit code with --once: 0 = nothing new, 10 = at least one new reply.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOG_PATH = "research/co-chat.md"
BRANCHES = ("origin/main", "origin/claude/cloud-environment-setup-ha4b84")
READERS = {"claude": "Claude", "chatgpt": "ChatGPT"}
# Speaker names as they appear in turn headings, e.g. "### A6 · Claude answers Q6".
SPEAKERS = {
    "Claude": re.compile(r"\bClaude\b"),
    "ChatGPT": re.compile(r"\b(ChatGPT|Codex)\b"),
    "Moderator": re.compile(r"\b(Moderator|Mohamed)\b"),
}
HEADING = re.compile(r"^\+(#{2,4})\s+(.*)$")
SHA = re.compile(r"^[0-9a-f]{7,40}$")


def git(*args: str, check: bool = True) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    result = subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=env, timeout=120,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()[:300]}")
    return result.stdout


def heads() -> dict[str, str]:
    found = {}
    for branch in BRANCHES:
        sha = git("rev-parse", "--verify", "--quiet", branch, check=False).strip()
        if SHA.match(sha):
            found[branch] = sha
    return found


def speaker_of(title: str) -> str | None:
    # The speaker is named after the last "·" when there is one ("A4 · ChatGPT answers ...").
    tail = title.rsplit("·", 1)[-1] if "·" in title else title
    # The first name mentioned wins: "ChatGPT to Claude" is a ChatGPT turn.
    for candidate in (tail, title):
        hits = [(m.start(), name) for name, pattern in SPEAKERS.items()
                if (m := pattern.search(candidate))]
        if hits:
            return min(hits)[1]
    return None


def describe(old: str, new: str) -> dict:
    """Summarise what the range old..new added to the shared log."""
    diff = git("diff", "--unified=0", old, new, "--", LOG_PATH)
    headings, speakers = [], []
    for line in diff.splitlines():
        match = HEADING.match(line)
        if not match:
            continue
        title = match.group(2).strip()
        headings.append(title)
        name = speaker_of(title)
        if name and name not in speakers:
            speakers.append(name)
    added = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    files = [f for f in git("diff", "--name-only", old, new).splitlines() if f]
    subjects = [s for s in git("log", "--format=%s", f"{old}..{new}").splitlines() if s]
    return {
        "old": old[:7], "new": new[:7],
        "speakers": speakers or ["unknown"],
        "log_lines_added": added,
        "headings": headings[:40],
        "files_changed": files[:40],
        "commit_subjects": subjects[:10],
    }


def paste_text(event: dict) -> str:
    who = " and ".join(event["speakers"])
    lines = [
        f"New co-chat reply from {who} on {', '.join(event['branches'])} "
        f"(commit {event['new']}, {event['time_utc']}).",
        "",
        f"Read: https://github.com/mms20102/Local-AI-tests/blob/{event['new_full']}/{LOG_PATH}",
        "",
        "New headings:",
    ]
    lines += [f"- {h}" for h in event["headings"]] or ["- (no new headings; see the diff)"]
    lines += ["", "Please fetch that commit before replying, and write only your own turns."]
    return "\n".join(lines) + "\n"


def toast(title: str, body: str) -> None:
    """Best-effort Windows balloon notification; silently skipped elsewhere."""
    if os.name != "nt":
        return
    script = (
        "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; "
        "$n = New-Object System.Windows.Forms.NotifyIcon; "
        "$n.Icon = [System.Drawing.SystemIcons]::Information; $n.Visible = $true; "
        "$n.ShowBalloonTip(10000, $env:COCHAT_TITLE, $env:COCHAT_BODY, 'Info'); "
        "Start-Sleep -Seconds 6; $n.Dispose()"
    )
    env = dict(os.environ, COCHAT_TITLE=title[:60], COCHAT_BODY=body[:240])
    try:
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError:
        pass


def check(inbox: Path, state: dict, use_toast: bool) -> int:
    """Fetch once, report every branch that moved. Returns the number of events."""
    git("fetch", "--all", "--prune", "--quiet")
    current = heads()
    seen = state.setdefault("heads", {})
    events: dict[tuple[str, str], dict] = {}
    for branch, new in current.items():
        old = seen.get(branch)
        if old is None:          # first sight of this branch: remember, do not report
            seen[branch] = new
            continue
        if old == new:
            continue
        # Report forward movement only (a rewind or an unrelated --since is just recorded).
        if subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", old, new],
                          capture_output=True, timeout=60).returncode != 0:
            seen[branch] = new
            continue
        key = (old, new)
        if key not in events:
            event = describe(old, new)
            event.update(branches=[], new_full=new,
                         time_utc=datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ"))
            events[key] = event
        events[key]["branches"].append(branch)
        seen[branch] = new
    inbox.mkdir(parents=True, exist_ok=True)
    for event in events.values():
        record = json.dumps(event, ensure_ascii=False)
        for key, name in READERS.items():
            if event["speakers"] != [name]:      # do not notify an author of their own reply
                with (inbox / f"for-{key}.jsonl").open("a", encoding="utf-8") as handle:
                    handle.write(record + "\n")
        if event["speakers"] != ["ChatGPT"]:
            (inbox / "for-chatgpt-latest.md").write_text(paste_text(event), encoding="utf-8")
        summary = (f"COCHAT new reply from {'+'.join(event['speakers'])} | "
                   f"{event['old']}..{event['new']} on {','.join(event['branches'])} | "
                   f"+{event['log_lines_added']} log lines | "
                   f"{'; '.join(event['headings'][:4]) or 'no new headings'}")
        print(summary, flush=True)
        if use_toast:
            toast("Co-chat: new reply from " + "+".join(event["speakers"]),
                  "; ".join(event["headings"][:3]) or event["new"])
    tmp = inbox / "state.json.tmp"
    tmp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, inbox / "state.json")
    return len(events)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--once", action="store_true", help="check once and exit")
    parser.add_argument("--interval", type=int, default=60, help="seconds between checks (min 30)")
    parser.add_argument("--toast", action="store_true", help="show a Windows notification")
    parser.add_argument("--since", help="report everything after this commit")
    parser.add_argument("--inbox", type=Path, default=REPO / ".notify",
                        help="folder for inbox files (default: .notify in the clone, git-ignored)")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    state_file = args.inbox / "state.json"
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            state = {}
    if not isinstance(state, dict):
        state = {}
    if args.since:
        if not SHA.match(args.since):
            raise SystemExit("--since needs a commit id")
        base = git("rev-parse", "--verify", args.since + "^{commit}").strip()
        state["heads"] = {branch: base for branch in BRANCHES}
    interval = max(30, args.interval)
    while True:
        try:
            count = check(args.inbox, state, args.toast)
        except (RuntimeError, OSError, subprocess.SubprocessError) as error:
            print(f"COCHAT watcher error: {error}", file=sys.stderr, flush=True)
            count = 0
            if args.once:
                return 2
        if args.once:
            return 10 if count else 0
        time.sleep(interval)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
