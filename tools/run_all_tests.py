"""Run every test suite in this repository and print one summary table.

    python tools/run_all_tests.py            run everything
    python tools/run_all_tests.py teach      run suites whose name contains "teach"

Standard library only. Each suite runs in its own process from its own folder, with bytecode
writing off, so suites cannot affect each other. Nothing here starts a service, calls a model or
touches the network. Tests that need the laptop's private files or the LiteLLM library are skipped
by the suites themselves and show up in the "skipped" column.

Exit status is 0 only if every suite passed.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# name, folder (relative to the repository root), unittest arguments
SUITES = [
    ("co-chat watcher", "tools", ["discover", "-s", ".", "-p", "test_*.py"]),
    ("coding-quality grader", "research/coding-quality-v1", ["discover", "-s", ".", "-p", "test_*.py"]),
    ("teach store and hook", "research/teach-store", ["discover", "-s", "tests"]),
    ("gateway admission", "research/gateway-admission", ["discover", "-s", "tests"]),
    ("teach status adapter", "research/teach-status-adapter-prototype", ["discover", "-s", ".", "-p", "test_*.py"]),
]


def run(name: str, folder: str, arguments: list[str]) -> dict:
    started = time.monotonic()
    done = subprocess.run([sys.executable, "-B", "-m", "unittest", *arguments], cwd=ROOT / folder,
                          capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    output = done.stdout + done.stderr
    ran = re.search(r"^Ran (\d+) tests?", output, re.MULTILINE)
    skipped = re.search(r"skipped=(\d+)", output)
    failed = sum(int(n) for n in re.findall(r"(?:failures|errors)=(\d+)", output))
    return {"name": name, "folder": folder, "ran": int(ran.group(1)) if ran else 0,
            "skipped": int(skipped.group(1)) if skipped else 0, "failed": failed,
            "ok": done.returncode == 0 and ran is not None, "seconds": round(time.monotonic() - started, 1),
            "output": output}


def main() -> int:
    wanted = [word.lower() for word in sys.argv[1:]]
    suites = [s for s in SUITES if not wanted or any(word in s[0] for word in wanted)]
    if not suites:
        print("No suite matches: " + " ".join(sys.argv[1:]))
        return 2
    rows = [run(*suite) for suite in suites]
    width = max(len(row["name"]) for row in rows)
    print(f"{'suite'.ljust(width)}  result  ran  skipped  failed  seconds  folder")
    for row in rows:
        print(f"{row['name'].ljust(width)}  {'pass' if row['ok'] else 'FAIL':6}  {row['ran']:3}  {row['skipped']:7}  "
              f"{row['failed']:6}  {row['seconds']:7}  {row['folder']}")
    for row in rows:
        if not row["ok"]:
            print(f"\n--- {row['name']} ({row['folder']}) ---\n{row['output'][-3000:]}")
    total = sum(row["ran"] for row in rows)
    print(f"\n{total} tests in {len(rows)} suites; {sum(row['skipped'] for row in rows)} skipped; "
          f"{sum(not row['ok'] for row in rows)} suites failing")
    return 0 if all(row["ok"] for row in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
