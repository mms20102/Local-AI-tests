"""Runs INSIDE the Windows Sandbox guest. Standard library only.

It is started by the sandbox's logon command from a read-only mapped folder. For each staged entry it
copies the candidate's files to a local working folder, runs the grader's own driver in a fresh
interpreter with a deadline and an output cap, and records what the driver reported. It never sees
expected values and never decides pass or fail: the host does that.

Layout in the guest (set by the .wsb file):
    C:\\cq1\\in    read-only   entries/<id>/{candidate files, __calls__.json}, __driver__.py, entries.json
    C:\\cq1\\py    read-only   a standalone Python
    C:\\cq1\\out   writable    results.json and DONE are written here at the very end
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

IN, OUT, WORK = Path(r"C:\cq1\in"), Path(r"C:\cq1\out"), Path(r"C:\cq1work")
ENTRY_TIMEOUT_S = 10          # the same deadline grade.py uses for one draft's cases
MAX_OUTPUT_BYTES = 1048576    # the same cap grade.py uses
TOTAL_DEADLINE_S = 900


def environment_facts() -> dict:
    """What this guest can reach. Recorded so the host can refuse results from a guest that is not isolated."""
    facts = {"python": sys.version.split()[0], "user": os.environ.get("USERNAME"), "computer": os.environ.get("COMPUTERNAME")}
    reach = {}
    for name, target in (("public_ip", ("1.1.1.1", 443)), ("public_dns_name", ("example.com", 80)),
                         ("default_gateway_guess", ("172.17.0.1", 445)), ("link_local_host", ("169.254.1.1", 445))):
        try:
            socket.create_connection(target, timeout=3).close()
            reach[name] = "CONNECTED"
        except Exception as error:  # noqa: BLE001
            reach[name] = "failed: " + type(error).__name__
    facts["network"] = reach
    try:
        (IN / "__write_probe__").write_text("x", encoding="utf-8")
        facts["input_folder_writable"] = True
    except Exception as error:  # noqa: BLE001
        facts["input_folder_writable"] = False
        facts["input_folder_write_error"] = type(error).__name__
    facts["drives"] = [f"{letter}:" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{letter}:\\")]
    facts["host_user_folder_visible"] = os.path.exists(r"C:\Users\User")
    facts["tsclient_visible"] = os.path.exists(r"\\tsclient\C")
    return facts


def run_entry(entry_id: str) -> dict:
    source, folder = IN / "entries" / entry_id, WORK / entry_id
    shutil.copytree(source, folder)
    shutil.copy(IN / "__driver__.py", folder / "__driver__.py")
    env = {k: v for k, v in os.environ.items() if k.upper() in ("SYSTEMROOT", "PATH", "TEMP", "TMP")}
    env["PYTHONIOENCODING"] = "utf-8"
    started = time.monotonic()
    record = {"id": entry_id}
    with open(folder / "__stdout__.bin", "wb") as sink:
        process = subprocess.Popen([sys.executable, "-I", "-B", "__driver__.py"], cwd=folder, env=env,
                                   stdout=sink, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        try:
            process.wait(timeout=ENTRY_TIMEOUT_S)
            record["exit_code"] = process.returncode
            record["status"] = "finished"
        except subprocess.TimeoutExpired:
            record["status"] = "timeout"
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                record["status"] = "timeout_and_not_killed"
    record["seconds"] = round(time.monotonic() - started, 2)
    size = (folder / "__stdout__.bin").stat().st_size
    record["stdout_bytes"] = size
    record["stdout_capped"] = size > MAX_OUTPUT_BYTES
    with open(folder / "__stdout__.bin", "rb") as source_file:
        output = source_file.read(MAX_OUTPUT_BYTES).decode("utf-8", errors="replace")
    record["records"] = None
    if record["status"] == "finished" and not record["stdout_capped"]:
        try:
            parsed = json.loads(output.strip().splitlines()[-1])
            if isinstance(parsed, list):
                record["records"] = parsed
        except (ValueError, IndexError):
            pass
    return record


def main() -> None:
    started = time.monotonic()
    result = {"guest_runner": "cq1-sandbox-1", "environment": {}, "entries": [], "complete": False}
    try:
        result["environment"] = environment_facts()
        entries = json.loads((IN / "entries.json").read_text(encoding="utf-8"))
        WORK.mkdir(exist_ok=True)
        for entry_id in entries:
            if time.monotonic() - started > TOTAL_DEADLINE_S:
                result["entries"].append({"id": entry_id, "status": "not_run_total_deadline", "records": None})
                continue
            try:
                result["entries"].append(run_entry(entry_id))
            except Exception as error:  # noqa: BLE001
                result["entries"].append({"id": entry_id, "status": "runner_error", "error": type(error).__name__, "records": None})
        result["complete"] = True
    except Exception as error:  # noqa: BLE001
        result["runner_error"] = type(error).__name__
    result["total_seconds"] = round(time.monotonic() - started, 1)
    # Written once, at the very end, after every candidate process has finished or been killed.
    (OUT / "results.json").write_text(json.dumps(result), encoding="utf-8")
    (OUT / "DONE").write_text("done\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    subprocess.run(["shutdown", "/s", "/t", "5", "/f"], capture_output=True)     # closes the sandbox
