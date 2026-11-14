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

First run: the current branch heads are recorded as the baseline and nothing is
reported. Only commits that arrive afterwards produce events. To replay history on
purpose, pass --since <commit>: every commit after it is reported once.

A commit is reported once, whichever branch it shows up on first; `main` catching up
with the Claude branch later is silent. A commit that does not touch the shared log
is reported as "repo update, no new log turns", not as a reply.

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


def commits_between(old: str, new: str) -> list[str]:
    """Non-merge commits in old..new, oldest first."""
    out = git("rev-list", "--reverse", "--no-merges", f"{old}..{new}")
    return [line for line in out.split() if SHA.match(line)]


def describe(commits: list[str]) -> dict:
    """Summarise what these commits added to the shared log (each against its parent)."""
    headings, speakers, files, subjects, added = [], [], [], [], 0
    for commit in commits:
        diff = git("show", "--format=", "--unified=0", commit, "--", LOG_PATH)
        for line in diff.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added += 1
            match = HEADING.match(line)
            if not match:
                continue
            title = match.group(2).strip()
            headings.append(title)
            name = speaker_of(title)
            if name and name not in speakers:
                speakers.append(name)
        for name in git("show", "--format=", "--name-only", commit).splitlines():
            if name and name not in files:
                files.append(name)
        subjects.append(git("show", "-s", "--format=%s", commit).strip())
    return {
        "id": commits[-1],
        "kind": "reply" if added else "files",
        "commits": [c[:7] for c in commits],
        "new": commits[-1][:7], "new_full": commits[-1],
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


def append_once(path: Path, event: dict) -> None:
    """Append the event unless this inbox already holds it (safe to repeat after a failure)."""
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                if json.loads(line).get("id") == event["id"]:
                    return
            except ValueError:
                continue
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def check(inbox: Path, state: dict, use_toast: bool) -> int:
    """Fetch once and report commits not reported before. Returns the number of events.

    `state` is only changed after every inbox write and the state file succeeded, so a
    failure part-way is retried on the next check (delivery is at-least-once to stdout,
    exactly-once per inbox file).
    """
    git("fetch", "--all", "--prune", "--quiet")
    seen = dict(state.get("heads", {}))
    reported = list(state.get("reported", []))
    known = set(reported)
    events: dict[tuple[str, ...], dict] = {}
    for branch, new in heads().items():
        old = seen.get(branch)
        seen[branch] = new
        if old is None or old == new:      # first sight of a branch is a baseline, not a reply
            continue
        # A commit already reported on another branch (main catching up) is not reported again.
        fresh = [c for c in commits_between(old, new) if c not in known]
        if not fresh:
            continue
        key = tuple(fresh)
        if key not in events:
            event = describe(fresh)
            event.update(branches=[], time_utc=datetime.datetime.now(datetime.timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ"))
            events[key] = event
        events[key]["branches"].append(branch)
    for key in events:
        for commit in key:
            if commit not in known:
                known.add(commit)
                reported.append(commit)
    inbox.mkdir(parents=True, exist_ok=True)
    for event in events.values():
        for key, name in READERS.items():
            if event["speakers"] != [name]:      # do not notify an author of their own reply
                append_once(inbox / f"for-{key}.jsonl", event)
        if event["kind"] == "reply" and event["speakers"] != ["ChatGPT"]:
            (inbox / "for-chatgpt-latest.md").write_text(paste_text(event), encoding="utf-8")
    new_state = {"heads": seen, "reported": reported[-2000:]}
    tmp = inbox / "state.json.tmp"
    tmp.write_text(json.dumps(new_state, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, inbox / "state.json")
    state.clear()
    state.update(new_state)
    for event in events.values():
        where = f"{'+'.join(event['commits'])} on {','.join(event['branches'])}"
        if event["kind"] == "reply":
            print(f"COCHAT new reply from {'+'.join(event['speakers'])} | {where} | "
                  f"+{event['log_lines_added']} log lines | "
                  f"{'; '.join(event['headings'][:4]) or 'no new headings'}", flush=True)
            if use_toast:
                toast("Co-chat: new reply from " + "+".join(event["speakers"]),
                      "; ".join(event["headings"][:3]) or event["new"])
        else:
            print(f"COCHAT repo update, no new log turns | {where} | "
                  f"{', '.join(event['files_changed'][:6])}", flush=True)
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
        state["reported"] = []
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
