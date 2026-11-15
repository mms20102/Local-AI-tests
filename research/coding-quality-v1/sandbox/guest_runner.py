"""Runs INSIDE the Windows Sandbox guest. Standard library only.

It is started by the sandbox's logon command from a read-only mapped folder. For each staged entry it
copies the candidate's files to a local working folder, runs the grader's own driver in a fresh
interpreter, and records what the driver reported. It never sees expected values and never decides
pass or fail: the host does that.

Every candidate interpreter is confined before it executes a single instruction:
  - it is created SUSPENDED, placed in a Windows job object, and only then resumed;
  - the job allows ONE process (the candidate cannot start another), caps its memory, and is
    terminated as a whole on the deadline, on an output flood, or when this runner exits;
  - its output goes to a file that is watched while it runs, and it is stopped if the file grows
    past a limit.
If the job cannot be created or applied, the candidate is not run at all.

Layout in the guest (set by the .wsb file):
    C:\\cq1\\in    read-only   entries/<id>/{candidate files, __calls__.json}, __driver__.py, entries.json
    C:\\cq1\\py    read-only   a standalone Python
    C:\\cq1\\out   writable    results.json and DONE are written here at the very end
"""
import ctypes
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

IN, OUT, WORK = Path(r"C:\cq1\in"), Path(r"C:\cq1\out"), Path(r"C:\cq1work")
ENTRY_TIMEOUT_S = 10              # the same deadline grade.py uses for one draft's cases
MAX_OUTPUT_BYTES = 1048576        # the same cap grade.py uses for what is read back
FLOOD_BYTES = 4 * 1048576         # the candidate is stopped when its output file passes this
MEMORY_LIMIT_BYTES = 1024 * 1048576
TOTAL_DEADLINE_S = 900

CREATE_SUSPENDED = 0x00000004
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9


class BasicLimits(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]


class IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint64) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                                                     "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", BasicLimits), ("IoInfo", IoCounters), ("ProcessMemoryLimit", ctypes.c_size_t),
                ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                ("PeakJobMemoryUsed", ctypes.c_size_t)]


def loads_strict(text):
    """As grade.loads_strict: a repeated key or a non-JSON constant is refused, not silently resolved."""
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("repeated key")
        return dict(items)

    def constant(name):
        raise ValueError("non-JSON constant " + name)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def confining_job():
    """A job object: one process, capped memory, killed as a whole when closed. Returns a handle or raises."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise OSError("CreateJobObjectW failed")
    limits = ExtendedLimits()
    limits.BasicLimitInformation.LimitFlags = (JOB_OBJECT_LIMIT_ACTIVE_PROCESS | JOB_OBJECT_LIMIT_PROCESS_MEMORY
                                               | JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION
                                               | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
    limits.BasicLimitInformation.ActiveProcessLimit = 1
    limits.ProcessMemoryLimit = MEMORY_LIMIT_BYTES
    limits.JobMemoryLimit = MEMORY_LIMIT_BYTES
    if not kernel.SetInformationJobObject(job, JobObjectExtendedLimitInformation, ctypes.byref(limits), ctypes.sizeof(limits)):
        kernel.CloseHandle(job)
        raise OSError("SetInformationJobObject failed")
    return kernel, job


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
    record = {"id": entry_id, "records": None, "confined": False}
    try:
        kernel, job = confining_job()
    except Exception as error:  # noqa: BLE001
        record.update(status="not_run_no_job", error=type(error).__name__)
        return record
    out_path = folder / "__stdout__.bin"
    started = time.monotonic()
    try:
        with open(out_path, "wb") as sink:
            process = subprocess.Popen([sys.executable, "-I", "-B", "__driver__.py"], cwd=folder, env=env,
                                       stdout=sink, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                                       creationflags=CREATE_SUSPENDED)
            if not kernel.AssignProcessToJobObject(job, int(process._handle)):
                process.kill()                           # never ran: it was still suspended
                record.update(status="not_run_job_not_applied")
                return record
            record["confined"] = True
            ctypes.WinDLL("ntdll").NtResumeProcess(wintypes.HANDLE(int(process._handle)))
            status = "finished"
            while process.poll() is None:
                if time.monotonic() - started > ENTRY_TIMEOUT_S:
                    status = "timeout"
                elif out_path.stat().st_size > FLOOD_BYTES:
                    status = "output_flood"
                else:
                    time.sleep(0.02)
                    continue
                kernel.TerminateJobObject(job, 1)        # the whole job, so nothing the candidate started survives
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    status += "_and_not_killed"
                break
            record["status"] = status
            record["exit_code"] = process.returncode
    finally:
        kernel.CloseHandle(job)                           # kill-on-close: ends anything still inside
    record["seconds"] = round(time.monotonic() - started, 2)
    size = out_path.stat().st_size
    record["stdout_bytes"] = size
    record["stdout_capped"] = size > MAX_OUTPUT_BYTES
    if record["status"] == "finished" and not record["stdout_capped"]:
        with open(out_path, "rb") as source_file:
            output = source_file.read(MAX_OUTPUT_BYTES).decode("utf-8", errors="replace")
        try:
            parsed = loads_strict(output.strip().splitlines()[-1])
            if isinstance(parsed, list):
                record["records"] = parsed
        except (ValueError, IndexError, RecursionError):
            pass
    return record


def main() -> None:
    started = time.monotonic()
    result = {"guest_runner": "cq1-sandbox-3", "environment": {}, "entries": [], "complete": False,
              "limits": {"entry_timeout_s": ENTRY_TIMEOUT_S, "flood_bytes": FLOOD_BYTES, "memory_limit_bytes": MEMORY_LIMIT_BYTES,
                         "active_process_limit": 1}}
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
    # Written once, at the very end, after every candidate job has been closed.
    (OUT / "results.json").write_text(json.dumps(result), encoding="utf-8")
    (OUT / "DONE").write_text("done\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    subprocess.run(["shutdown", "/s", "/t", "5", "/f"], capture_output=True)     # closes the sandbox
