"""Host side of CODE-Q1 behavioural grading in Windows Sandbox. Standard library only.

Nothing written by a model is executed by this program or on this machine's own system. It:
  1. reads each candidate's source with source_gate (no import, no execution) and sorts candidates
     into PLAIN ones, which cannot reach files, processes or the interpreter's internals, and the
     rest;
  2. stages candidate files and the calls to make (never the expected values) into a per-run folder;
  3. writes a .wsb file that maps that folder READ-ONLY into a Windows Sandbox guest with networking,
     clipboard, printers, audio, video and the virtual GPU switched off;
  4. runs plain candidates together in one sandbox session, and every other candidate ALONE in a
     session of its own, so that it can disturb nothing but itself;
  5. reads each guest report as untrusted data, refuses it if the guest was not isolated or did not
     end cleanly, and judges every case here, on the host, with grade.py's own judge and the
     expected values that never left the host.

A result is TRUSTED only when the candidate was plain, ran confined in a job object, exited with
status 0 and produced the driver's report. A candidate that is not plain is still run and judged,
alone, but its result is reported as an untrusted observation and is not counted as a pass.

    python sandbox_host.py probe   --python <standalone python folder> --run-dir <empty folder> --out probe.json
    python sandbox_host.py drafts  --python ... --run-dir ... --drafts <folder of TASK.json> --out drafts.json
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import grade  # noqa: E402  (static checks, the driver text and the judge; nothing here runs a draft)
import source_gate  # noqa: E402

MAX_RESULT_BYTES = 8 * 1024 * 1024
SANDBOX_DEADLINE_S = 900
GUEST_MEMORY_MB = 2048
HOST_HEADROOM_MB = 1536            # refuse to start a guest unless this much stays free on the host
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
  <MemoryInMB>{memory}</MemoryInMB>
  <MappedFolders>
    <MappedFolder><HostFolder>{in_dir}</HostFolder><SandboxFolder>C:\\cq1\\in</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>{py_dir}</HostFolder><SandboxFolder>C:\\cq1\\py</SandboxFolder><ReadOnly>true</ReadOnly></MappedFolder>
    <MappedFolder><HostFolder>{out_dir}</HostFolder><SandboxFolder>C:\\cq1\\out</SandboxFolder><ReadOnly>false</ReadOnly></MappedFolder>
  </MappedFolders>
  <LogonCommand><Command>C:\\cq1\\py\\python.exe -I -B C:\\cq1\\in\\guest_runner.py</Command></LogonCommand>
</Configuration>
"""


NETWORK_PROBES = {"public_ip", "public_dns_name", "default_gateway_guess", "link_local_host"}   # as in guest_runner.py


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def available_memory_mb() -> int:
    class Status(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    status = Status()
    status.dwLength = ctypes.sizeof(Status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return int(min(status.ullAvailPhys, status.ullAvailPageFile) // (1024 * 1024))


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
    for calls_file in in_dir.rglob("__calls__.json"):
        staged = json.loads(calls_file.read_text(encoding="utf-8"))
        if any(set(call) != {"call", "args"} for call in staged):
            raise SystemExit("something other than calls and arguments was staged")
    wsb = run_dir / "run.wsb"
    wsb.write_text(WSB.format(in_dir=in_dir, py_dir=python_dir, out_dir=out_dir, memory=GUEST_MEMORY_MB), encoding="utf-8")
    return wsb


def run_sandbox(run_dir: Path, wsb: Path) -> dict:
    """Start the sandbox, wait for DONE or the deadline, close it. Returns how the session went."""
    session = {"deadline_hit": False, "host_available_mb_before": available_memory_mb()}
    if session["host_available_mb_before"] < GUEST_MEMORY_MB + HOST_HEADROOM_MB:
        session["not_started"] = "not enough free memory on the host"
        session["closed_by_guest_shutdown"] = False
        return session
    before = sandbox_processes()
    if before:
        raise SystemExit("a Windows Sandbox is already running; close it first (only one can run)")
    started = time.monotonic()
    subprocess.Popen(["WindowsSandbox.exe", str(wsb)])
    done = run_dir / "out" / "DONE"
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
        report = grade.loads_strict(path.read_text(encoding="utf-8"))
    except (ValueError, RecursionError):
        return None, ["report is not JSON"]
    if not isinstance(report, dict) or not isinstance(report.get("entries"), list) or report.get("complete") is not True:
        return None, ["report has the wrong shape or is incomplete"]
    if [e.get("id") if isinstance(e, dict) else None for e in report["entries"]] != expected_ids:
        return None, ["report entries do not match what was staged"]
    environment = report.get("environment") if isinstance(report.get("environment"), dict) else {}
    network = environment.get("network")
    if not (isinstance(network, dict) and set(network) == NETWORK_PROBES
            and all(isinstance(value, str) and value.startswith("failed: ") for value in network.values())):
        problems.append("guest could reach a network (or did not report every network check as failed)")
    if environment.get("input_folder_writable") is not False:
        problems.append("guest could write to its input folder (or did not report)")
    if environment.get("host_user_folder_visible") is not False or environment.get("tsclient_visible") is not False:
        problems.append("guest could see host folders (or did not report)")
    return report, problems


def judge_entries(report: dict, entries: dict[str, dict], plain_session: bool) -> dict:
    """Every case is decided HERE, from the guest's raw records and the host's own expected values."""
    judged = {}
    for item in report["entries"]:
        cases, records = entries[item["id"]]["cases"], item.get("records")
        clean = (item.get("status") == "finished" and item.get("confined") is True and item.get("exit_code") == 0
                 and item.get("stdout_capped") is False and isinstance(records, list) and len(records) == len(cases))
        if clean:
            results = [grade.judge(case, record) for case, record in zip(cases, records)]
        else:
            if item.get("status") != "finished":
                why = item.get("status")
            elif item.get("confined") is not True:
                why = "not confined"
            elif item.get("stdout_capped"):
                why = "output capped"
            elif item.get("exit_code") != 0:
                why = f"crashed (exit code {item.get('exit_code')})"
            else:
                why = "no usable report"
            results = [{"ok": False, "why": str(why)} for _ in cases]
        summary = grade.summarise(results)
        judged[item["id"]] = {"status": item.get("status"), "confined": item.get("confined"), "seconds": item.get("seconds"),
                              "exit_code": item.get("exit_code"), "stdout_bytes": item.get("stdout_bytes"),
                              "trusted_observation": bool(plain_session and clean), **summary}
    return judged


def one_session(run_dir: Path, python_dir: Path, entries: dict[str, dict], plain_session: bool) -> dict:
    wsb = stage(run_dir, python_dir, entries)
    session = run_sandbox(run_dir, wsb)
    report, problems = read_report(run_dir, list(entries)) if "not_started" not in session else (None, [session["not_started"]])
    if not session["closed_by_guest_shutdown"] and "not_started" not in session:
        # The runner shuts the guest down right after writing its report. A DONE file that appears
        # while the guest keeps running was not written at the end of the runner, so it is not trusted.
        problems.append("guest did not shut itself down after reporting")
    result = {"entries": list(entries), "plain_session": plain_session, "session": session, "refused": problems,
              "environment": (report or {}).get("environment"), "limits": (report or {}).get("limits"),
              "guest_total_seconds": (report or {}).get("total_seconds"), "judged": None}
    if report is not None and not problems:
        result["judged"] = judge_entries(report, entries, plain_session)
    return result


def probe_entries() -> tuple[dict, dict]:
    """Repository-authored code only: every task's reference (must pass), decoys (must fail), and the
    hostile fixtures kept in hostile/."""
    entries, expect = {}, {}
    for task_id in sorted(grade.manifest()["tasks"]):
        task = grade.load_task(task_id)
        cases = task["public"] + task["hidden"]
        base = grade.FIX / task_id
        entries[f"{task_id}_reference"] = {"files": {p.name: p.read_text(encoding="utf-8") for p in sorted((base / "reference").iterdir())},
                                           "cases": cases}
        expect[f"{task_id}_reference"] = "pass"
        files = {p.name: p.read_text(encoding="utf-8") for p in sorted((base / "decoy").iterdir()) if p.suffix == ".py"}
        if files:
            entries[f"{task_id}_decoy"] = {"files": files, "cases": cases}
            expect[f"{task_id}_decoy"] = "fail"
    index = json.loads((HERE / "hostile" / "index.json").read_text(encoding="utf-8"))
    for name, spec in index.items():
        entries[name] = {"files": {"solution.py": (HERE / "hostile" / name / "solution.py").read_text(encoding="utf-8")},
                         "cases": spec["cases"]}
        expect[name] = spec["expect"]
    return entries, expect


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
    return entries, static


def probe_outcome(want: str, got: dict | None, plain: bool) -> str:
    if want == "untrusted":
        return "as expected" if (not plain and (got is None or got["trusted_observation"] is False)) else "UNEXPECTED: trusted"
    if got is None:
        return "as expected" if want == "no_pass" else "NOT JUDGED"
    full = got["passed"] == got["total"]
    if want == "pass":
        return "as expected" if full else "UNEXPECTED: did not pass"
    if want in ("fail", "no_pass"):
        return "as expected" if not full else "UNEXPECTED: passed"
    if want.startswith("status:"):
        return "as expected" if got["status"] == want[7:] and not full else f"UNEXPECTED: status {got['status']}"
    return "UNKNOWN EXPECTATION"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("mode", choices=("probe", "drafts"))
    parser.add_argument("--python", type=Path, required=True, help="folder of a standalone Python to map read-only into the guest")
    parser.add_argument("--run-dir", type=Path, required=True, help="empty scratch folder for this run")
    parser.add_argument("--drafts", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="where to write the host's result JSON")
    args = parser.parse_args()
    if not (args.python / "python.exe").is_file():
        raise SystemExit("no python.exe in --python")
    identities = {name: sha256(path) for name, path in (
        ("grade.py", HERE.parent / "grade.py"), ("manifest.json", HERE.parent / "manifest.json"),
        ("sandbox_host.py", Path(__file__)), ("guest_runner.py", HERE / "guest_runner.py"),
        ("source_gate.py", HERE / "source_gate.py"), ("hostile/index.json", HERE / "hostile" / "index.json"))}
    identities["fixture_revision"] = grade.manifest()["fixture_revision"]
    if args.mode == "probe":
        entries, expect = probe_entries()
        static = None
    else:
        entries, static = draft_entries(args.drafts)
        expect = None
    gate = {entry_id: source_gate.reach_of(entry["files"]) for entry_id, entry in entries.items()}
    plain = {k: v for k, v in entries.items() if gate[k]["plain"]}
    groups = ([(plain, True)] if plain else []) + [({k: v}, False) for k, v in entries.items() if k not in plain]
    args.run_dir.mkdir(parents=True, exist_ok=True)
    sessions = [one_session(args.run_dir / f"session-{n:02d}", args.python, group, is_plain)
                for n, (group, is_plain) in enumerate(groups)]
    judged = {}
    for session in sessions:
        judged.update(session["judged"] or {})
    result = {"mode": args.mode, "identities": identities, "source_gate": gate,
              "sessions": [{k: v for k, v in s.items() if k != "judged"} for s in sessions], "static": static, "judged": judged}
    if expect is not None:
        outcome = {entry_id: probe_outcome(want, judged.get(entry_id), gate[entry_id]["plain"]) for entry_id, want in expect.items()}
        result["probe_outcome"] = outcome
        result["probe_ok"] = all(v == "as expected" for v in outcome.values())
    else:
        trusted = sorted(k for k, v in judged.items() if v["trusted_observation"] and v["passed"] == v["total"])
        result["summary"] = {"tasks": len(static), "fully_passing_trusted": trusted, "count": len(trusted),
                             "passing_but_untrusted": sorted(k for k, v in judged.items()
                                                             if not v["trusted_observation"] and v["passed"] == v["total"]),
                             "not_run": sorted(k for k in static if k not in judged)}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"mode": args.mode, "sessions": len(sessions), "refused": [s["refused"] for s in sessions],
                      "judged_entries": len(judged), "probe_ok": result.get("probe_ok"), "summary": result.get("summary")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
