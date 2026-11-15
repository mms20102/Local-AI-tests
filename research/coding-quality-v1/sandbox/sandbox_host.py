"""Host side of CODE-Q1 behavioural grading in Windows Sandbox. Standard library only.

Nothing written by a model is executed by this program or on this machine's own system. It:
  1. stages candidate files and the calls to make (never the expected values) into a per-run folder;
  2. writes a .wsb file that maps that folder READ-ONLY into a Windows Sandbox guest with networking,
     clipboard, printers, audio, video and the virtual GPU switched off;
  3. starts the sandbox, waits for the guest runner to finish or for a deadline, and closes it;
  4. reads the guest's report as untrusted data, checks its shape and size, refuses it if the guest
     reports that it could reach a network or write to its input folder, and judges every case here,
     on the host, with grade.py's own judge and the expected values that never left the host.

What this does and does not give:
  - containment of the candidate's execution is Windows Sandbox's, with the settings above;
  - a candidate cannot learn expected values, so it cannot report a pass without producing the values;
  - it does NOT protect the guest runner from a candidate that deliberately attacks it inside the
    guest (they share the guest and its administrator account). A hostile candidate could make its own
    cases look like crashes or timeouts, or interfere with other entries of the same run. Run
    untrusted candidates one per sandbox session if that matters; `--isolate` does this.

    python sandbox_host.py probe   --python <standalone python folder> --run-dir <empty scratch folder>
    python sandbox_host.py drafts  --python ... --run-dir ... --drafts <folder of TASK.json> [--isolate]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import grade  # noqa: E402  (static checks, the driver text and the judge; nothing here runs a draft)

MAX_RESULT_BYTES = 8 * 1024 * 1024
SANDBOX_DEADLINE_S = 1500
SANDBOX_IMAGES = ("WindowsSandbox.exe", "WindowsSandboxClient.exe", "WindowsSandboxRemoteSession.exe",
                  "WindowsSandboxServer.exe")

WSB = """<Configuration>
  <Networking>Disable</Networking>
  <VGpu>Disable</VGpu>
  <AudioInput>Disable</AudioInput>
  <VideoInput>Disable</VideoInput>
  <PrinterRedirection>Disable</PrinterRedirection>
  <ClipboardRedirection>Disable</ClipboardRedirection>
  <ProtectedClient>Enable</ProtectedClient>
  <MemoryInMB>4096</MemoryInMB>
  <MappedFolders>
    <MappedFolder><HostFolder>{in_dir}</HostFolder><SandboxFolder>C:\\cq1\\in</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>{py_dir}</HostFolder><SandboxFolder>C:\\cq1\\py</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>{out_dir}</HostFolder><SandboxFolder>C:\\cq1\\out</SandboxFolder><ReadOnly>false</ReadOnly></MappedFolder>
  </MappedFolders>
  <LogonCommand><Command>C:\\cq1\\py\\python.exe -I -B C:\\cq1\\in\\guest_runner.py</Command></LogonCommand>
</Configuration>
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sandbox_processes() -> set[int]:
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    found = set()
    for line in out.splitlines():
        parts = [p.strip('"') for p in line.split('","')]
        if len(parts) > 1 and parts[0] in SANDBOX_IMAGES:
            found.add(int(parts[1]))
    return found


def stage(run_dir: Path, python_dir: Path, entries: dict[str, dict]) -> Path:
    """entries: id -> {"files": {name: code}, "cases": [...]}. Only the calls and arguments are staged."""
    if run_dir.exists() and any(run_dir.iterdir()):
        raise SystemExit(f"run folder is not empty: {run_dir}")
    in_dir, out_dir = run_dir / "in", run_dir / "out"
    (in_dir / "entries").mkdir(parents=True)
    out_dir.mkdir()
    for entry_id, entry in entries.items():
        folder = in_dir / "entries" / entry_id
        folder.mkdir()
        for name, code in entry["files"].items():
            if "/" in name or "\\" in name or not name.endswith(".py") or name.startswith("__"):
                raise SystemExit(f"refused file name in {entry_id}: {name!r}")
            (folder / name).write_text(code, encoding="utf-8", newline="\n")
        calls = [{"call": c["call"], "args": c["args"]} for c in entry["cases"]]       # never "expect" or "raises"
        (folder / "__calls__.json").write_text(json.dumps(calls), encoding="utf-8")
    (in_dir / "__driver__.py").write_text(grade.DRIVER, encoding="utf-8")
    (in_dir / "entries.json").write_text(json.dumps(list(entries)), encoding="utf-8")
    shutil.copy(HERE / "guest_runner.py", in_dir / "guest_runner.py")
    staged = json.dumps({p.relative_to(in_dir).as_posix(): sha256(p) for p in sorted(in_dir.rglob("*")) if p.is_file()})
    if any(word in staged for word in ('"expect"', '"raises"')) or \
            any('"expect"' in p.read_text(encoding="utf-8", errors="replace") for p in in_dir.rglob("__calls__.json")):
        raise SystemExit("expected values found in the staged input")
    wsb = run_dir / "run.wsb"
    wsb.write_text(WSB.format(in_dir=in_dir, py_dir=python_dir, out_dir=out_dir), encoding="utf-8")
    return wsb


def run_sandbox(run_dir: Path, wsb: Path) -> dict:
    """Start the sandbox, wait for DONE or the deadline, close it. Returns how the session went."""
    before = sandbox_processes()
    if before:
        raise SystemExit("a Windows Sandbox is already running; close it first (only one can run)")
    started = time.monotonic()
    subprocess.Popen(["WindowsSandbox.exe", str(wsb)])
    done, session = run_dir / "out" / "DONE", {"deadline_hit": False}
    while time.monotonic() - started < SANDBOX_DEADLINE_S:
        if done.exists():
            break
        if time.monotonic() - started > 180 and not sandbox_processes():
            session["sandbox_exited_without_report"] = True
            break
        time.sleep(2)
    else:
        session["deadline_hit"] = True
    session["seconds_to_report"] = round(time.monotonic() - started, 1)
    # Give the guest's own shutdown a moment, then end only sandbox processes that this run started.
    waited = time.monotonic()
    while sandbox_processes() - before and time.monotonic() - waited < 60:
        time.sleep(2)
    leftover = sandbox_processes() - before
    for pid in leftover:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    time.sleep(3)
    session["closed_by_guest_shutdown"] = not leftover
    session["sandbox_processes_after"] = sorted(sandbox_processes())
    return session


def read_report(run_dir: Path, expected_ids: list[str]) -> tuple[dict | None, list[str]]:
    """Parse the guest's report as untrusted data. Returns (report or None, reasons it was refused)."""
    path, problems = run_dir / "out" / "results.json", []
    if not path.is_file():
        return None, ["no report"]
    if path.stat().st_size > MAX_RESULT_BYTES:
        return None, ["report too large"]
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None, ["report is not JSON"]
    if not isinstance(report, dict) or not isinstance(report.get("entries"), list) or report.get("complete") is not True:
        return None, ["report has the wrong shape or is incomplete"]
    if [e.get("id") if isinstance(e, dict) else None for e in report["entries"]] != expected_ids:
        return None, ["report entries do not match what was staged"]
    environment = report.get("environment") if isinstance(report.get("environment"), dict) else {}
    network = environment.get("network") if isinstance(environment.get("network"), dict) else None
    if network is None or any(value == "CONNECTED" for value in network.values()):
        problems.append("guest could reach a network (or did not report)")
    if environment.get("input_folder_writable") is not False:
        problems.append("guest could write to its input folder (or did not report)")
    if environment.get("host_user_folder_visible") is not False or environment.get("tsclient_visible") is not False:
        problems.append("guest could see host folders (or did not report)")
    return report, problems


def judge_entries(report: dict, entries: dict[str, dict]) -> dict:
    """Every case is decided HERE, from the guest's raw records and the host's own expected values."""
    judged = {}
    for item in report["entries"]:
        cases, records = entries[item["id"]]["cases"], item.get("records")
        if item.get("status") != "finished" or not isinstance(records, list) or len(records) != len(cases):
            why = item.get("status") if item.get("status") != "finished" else ("output capped" if item.get("stdout_capped") else "crashed")
            results = [{"ok": False, "why": str(why)} for _ in cases]
        else:
            results = [grade.judge(case, record) for case, record in zip(cases, records)]
        summary = grade.summarise(results)
        judged[item["id"]] = {"status": item.get("status"), "seconds": item.get("seconds"), "exit_code": item.get("exit_code"),
                              "stdout_bytes": item.get("stdout_bytes"), **summary}
    return judged


def one_session(run_dir: Path, python_dir: Path, entries: dict[str, dict]) -> dict:
    wsb = stage(run_dir, python_dir, entries)
    session = run_sandbox(run_dir, wsb)
    report, problems = read_report(run_dir, list(entries))
    if not session["closed_by_guest_shutdown"]:
        # The guest runner shuts the guest down right after writing its report. A DONE file that appears
        # while the guest keeps running was not written at the end of the runner, so it is not trusted.
        problems.append("guest did not shut itself down after reporting")
    result = {"session": session, "refused": problems, "environment": (report or {}).get("environment"),
              "guest_total_seconds": (report or {}).get("total_seconds"), "judged": None}
    if report is not None and not problems:
        result["judged"] = judge_entries(report, entries)
    return result


# ---------------------------------------------------------------- handwritten probe entries
HOSTILE = {
    "P_loop": ({"solution.py": "def f(x):\n    while True:\n        pass\n"},
               [{"call": "solution.f", "args": [1], "expect": 1}], "timeout"),
    "P_output": ({"solution.py": "import sys\ndef f(x):\n    sys.stdout.write('A' * (20 * 1024 * 1024))\n    return x\n"},
                 [{"call": "solution.f", "args": [1], "expect": 1}], "fail"),
    "P_network": ({"solution.py": (
        "import socket\n"
        "def f(x):\n"
        "    reached = []\n"
        "    for target in (('1.1.1.1', 443), ('8.8.8.8', 53), ('example.com', 80)):\n"
        "        try:\n"
        "            socket.create_connection(target, timeout=2).close()\n"
        "            reached.append(target[0])\n"
        "        except Exception:\n"
        "            pass\n"
        "    return reached\n")},
        [{"call": "solution.f", "args": [1], "expect": []}], "pass"),
    "P_host_files": ({"solution.py": (
        "import os\n"
        "def f(x):\n"
        "    seen = [p for p in (r'C:\\Users\\User', r'\\\\tsclient\\C', r'C:\\Users\\User\\Documents') if os.path.exists(p)]\n"
        "    try:\n"
        "        open(r'C:\\cq1\\in\\planted.txt', 'w').write('x')\n"
        "        seen.append('wrote input folder')\n"
        "    except Exception:\n"
        "        pass\n"
        "    return seen\n")},
        [{"call": "solution.f", "args": [1], "expect": []}], "pass"),
    "P_spoof": ({"solution.py": (
        "import json\n"
        "def f(x):\n"
        "    fake = {'guest_runner': 'cq1-sandbox-1', 'complete': True, 'entries': [], 'environment': {}}\n"
        "    try:\n"
        "        open(r'C:\\cq1\\out\\results.json', 'w').write(json.dumps(fake))\n"
        "        open(r'C:\\cq1\\out\\DONE', 'w').write('done')\n"
        "    except Exception:\n"
        "        pass\n"
        "    return 'wrong value'\n")},
        [{"call": "solution.f", "args": [1], "expect": "right value"}], "fail"),
}


def probe_entries() -> tuple[dict, dict]:
    """Repository-authored code only: every task's reference (must pass), decoys (must fail), and hostile probes."""
    entries, expect = {}, {}
    for task_id in sorted(grade.manifest()["tasks"]):
        task = grade.load_task(task_id)
        cases = task["public"] + task["hidden"]
        base = grade.FIX / task_id
        entries[f"{task_id}_reference"] = {"files": {p.name: p.read_text(encoding="utf-8") for p in sorted((base / "reference").iterdir())},
                                           "cases": cases}
        expect[f"{task_id}_reference"] = "pass"
        decoy = base / "decoy"
        if decoy.is_dir():
            groups = [d for d in sorted(decoy.iterdir()) if d.is_dir()] or [decoy]
            for n, group in enumerate(groups):
                files = {p.name: p.read_text(encoding="utf-8") for p in sorted(group.iterdir()) if p.suffix == ".py"}
                if files:
                    entries[f"{task_id}_decoy{n}"] = {"files": files, "cases": cases}
                    expect[f"{task_id}_decoy{n}"] = "fail"
    for name, (files, cases, outcome) in HOSTILE.items():
        entries[name] = {"files": files, "cases": cases}
        expect[name] = outcome
    return entries, expect


RISKY_NAMES = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "globals", "vars", "getattr",
               "setattr", "delattr"}


def reach_of(files: dict[str, str], own_modules: set[str]) -> dict:
    """What a draft's source reaches for, read from its syntax tree. Nothing is imported or run.

    Used to decide whether a draft shares a sandbox session with others. A draft that imports nothing
    outside its own files and names none of RISKY_NAMES has no way, in plain Python, to touch files,
    processes or the guest runner. This is a reading of the source, not a proof about Python.
    """
    import ast
    imports, names, dunders = set(), set(), False
    for code in files.values():
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom):
                imports.add((node.module or "").split(".")[0])
            elif isinstance(node, ast.Name) and node.id in RISKY_NAMES:
                names.add(node.id)
            elif isinstance(node, ast.Attribute) and node.attr.startswith("__") and node.attr.endswith("__"):
                dunders = True
    outside = sorted(imports - own_modules)
    return {"imports_outside_own_files": outside, "risky_names": sorted(names), "dunder_attributes": dunders,
            "plain": not outside and not names and not dunders}


def draft_entries(folder: Path) -> tuple[dict, dict]:
    entries, static = {}, {}
    for task_id in sorted(grade.manifest()["tasks"]):
        task = grade.load_task(task_id)
        path = folder / f"{task_id}.json"
        result = grade.static_grade(task, grade.read_draft(path))
        static[task_id] = {"draft_sha256": sha256(path), "transport": result["transport"], "structure": result["structure"],
                           "problems": result["problems"]}
        if result["structure"] == "pass" and result["transport"] == "complete":
            entries[task_id] = {"files": result["files"], "cases": task["public"] + task["hidden"]}
            static[task_id]["reach"] = reach_of(result["files"], {name[:-3] for name in result["files"]})
    return entries, static


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("mode", choices=("probe", "drafts"))
    parser.add_argument("--python", type=Path, required=True, help="folder of a standalone Python to map read-only into the guest")
    parser.add_argument("--run-dir", type=Path, required=True, help="empty scratch folder for this run")
    parser.add_argument("--drafts", type=Path)
    parser.add_argument("--isolate", action="store_true", help="one sandbox session per entry")
    parser.add_argument("--out", type=Path, required=True, help="where to write the host's result JSON")
    args = parser.parse_args()
    if not (args.python / "python.exe").is_file():
        raise SystemExit("no python.exe in --python")
    identities = {"grade.py": sha256(HERE.parent / "grade.py"), "manifest.json": sha256(HERE.parent / "manifest.json"),
                  "sandbox_host.py": sha256(Path(__file__)), "guest_runner.py": sha256(HERE / "guest_runner.py"),
                  "fixture_revision": grade.manifest()["fixture_revision"]}
    if args.mode == "probe":
        entries, expect = probe_entries()
        static = None
    else:
        entries, static = draft_entries(args.drafts)
        expect = None
    sessions = []
    if args.isolate:
        groups = [{k: v} for k, v in entries.items()]
    elif static is not None:
        # Drafts whose source reaches outside plain Python each get a sandbox session of their own.
        plain = {k: v for k, v in entries.items() if static[k]["reach"]["plain"]}
        groups = ([plain] if plain else []) + [{k: v} for k, v in entries.items() if k not in plain]
    else:
        groups = [entries]
    args.run_dir.mkdir(parents=True, exist_ok=True)
    for n, group in enumerate(groups):
        sessions.append(one_session(args.run_dir / f"session-{n:02d}", args.python, group))
    judged = {}
    for session in sessions:
        judged.update(session["judged"] or {})
    result = {"mode": args.mode, "identities": identities, "isolated_sessions": args.isolate,
              "sessions": [{k: v for k, v in s.items() if k != "judged"} for s in sessions], "static": static, "judged": judged}
    if expect is not None:
        outcome = {}
        for entry_id, want in expect.items():
            got = judged.get(entry_id)
            if got is None:
                outcome[entry_id] = "NOT JUDGED"
            elif want == "pass":
                outcome[entry_id] = "as expected" if got["passed"] == got["total"] else "UNEXPECTED: did not pass"
            elif want == "fail":
                outcome[entry_id] = "as expected" if got["passed"] < got["total"] else "UNEXPECTED: passed"
            else:
                outcome[entry_id] = "as expected" if got["status"] == want else f"UNEXPECTED: status {got['status']}"
        result["probe_outcome"] = outcome
        result["probe_ok"] = all(v == "as expected" for v in outcome.values())
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"mode": args.mode, "sessions": len(sessions), "refused": [s["refused"] for s in sessions],
                      "judged_entries": len(judged), "probe_ok": result.get("probe_ok")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
