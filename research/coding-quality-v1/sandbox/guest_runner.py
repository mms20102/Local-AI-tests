"""Runs INSIDE the Windows Sandbox guest. Standard library only.

It is started by the sandbox's logon command from a read-only mapped folder. For each staged entry it
copies the candidate's files to a local working folder, runs the grader's own driver in a fresh
interpreter, and records what the driver reported. It never sees expected values and never decides
pass or fail: the host does that.

Every candidate interpreter is confined before it executes a single instruction:
  - this runner first replaces the access list of ITS OWN process with one that grants access to
    the SYSTEM account only, and gives the owner no implicit right to change it back. Measured on
    Windows 11: low integrity alone does NOT stop a child from opening its parent with the right
    to terminate it (that right is not among the "write" rights integrity blocks), so the access
    list is what protects the runner;
  - it is created with a RESTRICTED, LOW-INTEGRITY copy of the runner's token: every privilege that
    can be removed is removed, and Windows refuses a low-integrity process write access to files
    and objects of higher integrity;
  - it is created SUSPENDED, placed in a Windows job object, and only then resumed;
  - the job allows ONE process (the candidate cannot start another), caps its memory, and is
    terminated as a whole on the deadline, on too much output, or when this runner exits;
  - its output goes to a pipe that this runner reads. The runner stops reading at the limit, so
    the candidate cannot write more than the limit plus one pipe buffer: a hard cap, not a sample.
The runner then checks, from outside the candidate, that the process really is in the job and
really has low integrity. If any step fails, the candidate is not run (or is ended before resuming).

Layout in the guest (set by the .wsb file):
    C:\\cq1\\in    read-only   entries/<id>/{candidate files, __calls__.json}, __driver__.py, entries.json
    C:\\cq1\\py    read-only   a standalone Python
    C:\\cq1\\out   writable    results.json and DONE are written here at the very end
"""
import ctypes
import json
import msvcrt
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

IN, OUT, WORK = Path(r"C:\cq1\in"), Path(r"C:\cq1\out"), Path(r"C:\cq1work")
ENTRY_TIMEOUT_S = 10              # the same deadline grade.py uses for one draft's cases
MAX_OUTPUT_BYTES = 1048576        # the same limit grade.py uses; here it is enforced while the candidate runs
MEMORY_LIMIT_BYTES = 1024 * 1048576
TOTAL_DEADLINE_S = 900
LOW_INTEGRITY_SID, LOW_INTEGRITY_RID = "S-1-16-4096", 4096

CREATE_SUSPENDED, CREATE_UNICODE_ENVIRONMENT, CREATE_NO_WINDOW = 0x00000004, 0x00000400, 0x08000000
STARTF_USESTDHANDLES = 0x00000100
JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9
TOKEN_ALL_ACCESS, TOKEN_QUERY = 0xF01FF, 0x0008
DISABLE_MAX_PRIVILEGE = 0x1
DACL_SECURITY_INFORMATION = 0x4
# Protected access list: SYSTEM everything; OWNER RIGHTS read-only, which removes the owner's implicit
# right to rewrite the list. Nobody else is granted anything.
RUNNER_PROCESS_SDDL = "D:P(A;;GA;;;SY)(A;;RC;;;OW)"
PROCESS_TERMINATE = 0x0001
TokenIntegrityLevel = 25
SE_GROUP_INTEGRITY = 0x20


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


class StartupInfo(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("lpReserved", wintypes.LPWSTR), ("lpDesktop", wintypes.LPWSTR),
                ("lpTitle", wintypes.LPWSTR), ("dwX", wintypes.DWORD), ("dwY", wintypes.DWORD), ("dwXSize", wintypes.DWORD),
                ("dwYSize", wintypes.DWORD), ("dwXCountChars", wintypes.DWORD), ("dwYCountChars", wintypes.DWORD),
                ("dwFillAttribute", wintypes.DWORD), ("dwFlags", wintypes.DWORD), ("wShowWindow", wintypes.WORD),
                ("cbReserved2", wintypes.WORD), ("lpReserved2", ctypes.c_void_p), ("hStdInput", wintypes.HANDLE),
                ("hStdOutput", wintypes.HANDLE), ("hStdError", wintypes.HANDLE)]


class ProcessInformation(ctypes.Structure):
    _fields_ = [("hProcess", wintypes.HANDLE), ("hThread", wintypes.HANDLE), ("dwProcessId", wintypes.DWORD),
                ("dwThreadId", wintypes.DWORD)]


class SidAndAttributes(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wintypes.DWORD)]


class MandatoryLabel(ctypes.Structure):
    _fields_ = [("Label", SidAndAttributes)]


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


def windows():
    """kernel32 and advapi32 with the argument types set, so 64-bit handles are never truncated."""
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    advapi = ctypes.WinDLL("advapi32", use_last_error=True)
    handle, dword, pointer = wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p
    for library, name, restype, argtypes in (
            (kernel, "CreateJobObjectW", handle, [pointer, wintypes.LPCWSTR]),
            (kernel, "SetInformationJobObject", wintypes.BOOL, [handle, ctypes.c_int, pointer, dword]),
            (kernel, "AssignProcessToJobObject", wintypes.BOOL, [handle, handle]),
            (kernel, "IsProcessInJob", wintypes.BOOL, [handle, handle, ctypes.POINTER(wintypes.BOOL)]),
            (kernel, "TerminateJobObject", wintypes.BOOL, [handle, wintypes.UINT]),
            (kernel, "TerminateProcess", wintypes.BOOL, [handle, wintypes.UINT]),
            (kernel, "ResumeThread", dword, [handle]),
            (kernel, "WaitForSingleObject", dword, [handle, dword]),
            (kernel, "GetExitCodeProcess", wintypes.BOOL, [handle, ctypes.POINTER(dword)]),
            (kernel, "GetCurrentProcess", handle, []),
            (kernel, "CloseHandle", wintypes.BOOL, [handle]),
            (kernel, "LocalFree", pointer, [pointer]),
            (advapi, "OpenProcessToken", wintypes.BOOL, [handle, dword, ctypes.POINTER(handle)]),
            (advapi, "CreateRestrictedToken", wintypes.BOOL, [handle, dword, dword, pointer, dword, pointer, dword, pointer,
                                                              ctypes.POINTER(handle)]),
            (advapi, "ConvertStringSidToSidW", wintypes.BOOL, [wintypes.LPCWSTR, ctypes.POINTER(pointer)]),
            (advapi, "GetLengthSid", dword, [pointer]),
            (advapi, "SetTokenInformation", wintypes.BOOL, [handle, ctypes.c_int, pointer, dword]),
            (advapi, "GetTokenInformation", wintypes.BOOL, [handle, ctypes.c_int, pointer, dword, ctypes.POINTER(dword)]),
            (advapi, "GetSidSubAuthorityCount", ctypes.POINTER(ctypes.c_ubyte), [pointer]),
            (advapi, "GetSidSubAuthority", ctypes.POINTER(dword), [pointer, dword]),
            (advapi, "ConvertStringSecurityDescriptorToSecurityDescriptorW", wintypes.BOOL,
             [wintypes.LPCWSTR, dword, ctypes.POINTER(pointer), pointer]),
            (advapi, "SetKernelObjectSecurity", wintypes.BOOL, [handle, dword, pointer]),
            (kernel, "OpenProcess", handle, [dword, wintypes.BOOL, dword]),
            (kernel, "GetCurrentProcessId", dword, []),
            (kernel, "FreeConsole", wintypes.BOOL, []),
            (advapi, "CreateProcessAsUserW", wintypes.BOOL, [handle, wintypes.LPCWSTR, wintypes.LPWSTR, pointer, pointer,
                                                             wintypes.BOOL, dword, pointer, wintypes.LPCWSTR,
                                                             ctypes.POINTER(StartupInfo), ctypes.POINTER(ProcessInformation)])):
        function = getattr(library, name)
        function.restype, function.argtypes = restype, argtypes
    return kernel, advapi


def confining_job(kernel):
    """A job object: one process, capped memory, killed as a whole when closed. Returns a handle or raises."""
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
    return job


def protect_self(kernel, advapi) -> dict:
    """Replace this process's access list so that only SYSTEM is granted access. Returns what was observed:
    whether the list was set, and whether THIS process, asking afresh by process id, is now refused the right
    to terminate itself (the same question a candidate running as the same user would ask)."""
    outcome = {"access_list_set": False, "fresh_terminate_handle_refused": None}
    # Leave the console. Measured in the seventh probe: a candidate is granted a terminate handle on
    # conhost.exe, the console host this runner was attached to, and ending a console host ends the
    # programs attached to it. With no console there is nothing of that kind to end.
    outcome["console_left"] = bool(kernel.FreeConsole())
    descriptor = ctypes.c_void_p()
    if not advapi.ConvertStringSecurityDescriptorToSecurityDescriptorW(RUNNER_PROCESS_SDDL, 1, ctypes.byref(descriptor), None):
        return outcome
    try:
        outcome["access_list_set"] = bool(advapi.SetKernelObjectSecurity(kernel.GetCurrentProcess(), DACL_SECURITY_INFORMATION,
                                                                         descriptor))
    finally:
        kernel.LocalFree(descriptor)
    fresh = kernel.OpenProcess(PROCESS_TERMINATE, False, kernel.GetCurrentProcessId())
    outcome["fresh_terminate_handle_refused"] = not fresh
    if fresh:
        kernel.CloseHandle(fresh)
    return outcome


def low_rights_token(kernel, advapi):
    """A copy of this process's token with removable privileges removed and LOW integrity. Returns a handle or raises."""
    own, restricted, sid = wintypes.HANDLE(), wintypes.HANDLE(), ctypes.c_void_p()
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), TOKEN_ALL_ACCESS, ctypes.byref(own)):
        raise OSError("OpenProcessToken failed")
    # The Administrators group is left as it is. Revision 5 switched it to deny-only and, in the guest,
    # every candidate interpreter then failed to start (exit code 0xC0000142, DLL initialisation failed).
    try:
        if not advapi.CreateRestrictedToken(own, DISABLE_MAX_PRIVILEGE, 0, None, 0, None, 0, None, ctypes.byref(restricted)):
            raise OSError("CreateRestrictedToken failed")
    finally:
        kernel.CloseHandle(own)
    if not advapi.ConvertStringSidToSidW(LOW_INTEGRITY_SID, ctypes.byref(sid)):
        kernel.CloseHandle(restricted)
        raise OSError("ConvertStringSidToSidW failed")
    try:
        label = MandatoryLabel()
        label.Label.Sid, label.Label.Attributes = sid, SE_GROUP_INTEGRITY
        if not advapi.SetTokenInformation(restricted, TokenIntegrityLevel, ctypes.byref(label),
                                          ctypes.sizeof(label) + advapi.GetLengthSid(sid)):
            kernel.CloseHandle(restricted)
            raise OSError("SetTokenInformation failed")
    finally:
        kernel.LocalFree(sid)
    return restricted


def integrity_of(kernel, advapi, process):
    """The integrity level (as a number) of a process, read from its own token by this runner. None if unreadable."""
    token, needed = wintypes.HANDLE(), wintypes.DWORD()
    if not advapi.OpenProcessToken(process, TOKEN_QUERY, ctypes.byref(token)):
        return None
    try:
        advapi.GetTokenInformation(token, TokenIntegrityLevel, None, 0, ctypes.byref(needed))
        buffer = ctypes.create_string_buffer(needed.value or 64)
        if not advapi.GetTokenInformation(token, TokenIntegrityLevel, buffer, len(buffer), ctypes.byref(needed)):
            return None
        sid = ctypes.cast(buffer, ctypes.POINTER(MandatoryLabel)).contents.Label.Sid
        count = advapi.GetSidSubAuthorityCount(sid).contents.value
        return int(advapi.GetSidSubAuthority(sid, count - 1).contents.value)
    finally:
        kernel.CloseHandle(token)


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
    try:
        kernel, advapi = windows()
        facts["runner_integrity"] = integrity_of(kernel, advapi, kernel.GetCurrentProcess())
    except Exception as error:  # noqa: BLE001
        facts["runner_integrity"] = "failed: " + type(error).__name__
    return facts


def run_confined(folder: Path) -> dict:
    """Run `python -I -B __driver__.py` in `folder`, confined as the module text says. Returns what was observed."""
    record = {"records": None, "confined": False, "in_job": None, "integrity": None}
    kernel, advapi = windows()
    job = token = None
    read_fd = write_fd = null_fd = None
    info = ProcessInformation()
    started = time.monotonic()
    try:
        try:
            job = confining_job(kernel)
            token = low_rights_token(kernel, advapi)
        except Exception as error:  # noqa: BLE001
            record.update(status="not_run_no_confinement", error=str(error))
            return record
        read_fd, write_fd = os.pipe()
        null_fd = os.open(os.devnull, os.O_RDWR)
        write_handle, null_handle = msvcrt.get_osfhandle(write_fd), msvcrt.get_osfhandle(null_fd)
        os.set_handle_inheritable(write_handle, True)
        os.set_handle_inheritable(null_handle, True)
        startup = StartupInfo()
        startup.cb, startup.dwFlags = ctypes.sizeof(StartupInfo), STARTF_USESTDHANDLES
        startup.hStdInput, startup.hStdOutput, startup.hStdError = null_handle, write_handle, null_handle
        variables = {k.upper(): v for k, v in os.environ.items() if k.upper() in ("SYSTEMROOT", "PATH", "TEMP", "TMP")}
        variables["PYTHONIOENCODING"] = "utf-8"
        block = ctypes.create_unicode_buffer("".join(f"{k}={v}\0" for k, v in sorted(variables.items())) + "\0")
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline([sys.executable, "-I", "-B", "__driver__.py"]))
        created = advapi.CreateProcessAsUserW(token, sys.executable, command, None, None, True,
                                              CREATE_SUSPENDED | CREATE_UNICODE_ENVIRONMENT | CREATE_NO_WINDOW,
                                              block, str(folder), ctypes.byref(startup), ctypes.byref(info))
        error_code = ctypes.get_last_error()
        os.close(write_fd)                                # the child holds its own copy; ours would keep the pipe open
        write_fd = None
        if not created:
            record.update(status="not_run_not_created", error=f"CreateProcessAsUserW error {error_code}")
            return record
        # Still suspended: nothing of the candidate has run. Confine, verify from outside, then resume.
        in_job = wintypes.BOOL(False)
        assigned = kernel.AssignProcessToJobObject(job, info.hProcess)
        kernel.IsProcessInJob(info.hProcess, job, ctypes.byref(in_job))
        record["in_job"] = bool(assigned and in_job.value)
        record["integrity"] = integrity_of(kernel, advapi, info.hProcess)
        if not (record["in_job"] and record["integrity"] == LOW_INTEGRITY_RID):
            kernel.TerminateProcess(info.hProcess, 1)     # never ran: it was still suspended
            record.update(status="not_run_confinement_not_verified")
            return record
        record["confined"] = True

        chunks, state = [], {"bytes": 0, "over": False}

        def drain():
            while True:
                try:
                    chunk = os.read(read_fd, 65536)
                except OSError:
                    return
                if not chunk:
                    return
                state["bytes"] += len(chunk)
                if state["bytes"] > MAX_OUTPUT_BYTES:
                    state["over"] = True                 # stop reading: the writer blocks once the pipe is full
                    return
                chunks.append(chunk)

        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        kernel.ResumeThread(info.hThread)
        status = "finished"
        while kernel.WaitForSingleObject(info.hProcess, 20) != 0:
            if state["over"]:
                status = "output_flood"
            elif time.monotonic() - started > ENTRY_TIMEOUT_S:
                status = "timeout"
            else:
                continue
            kernel.TerminateJobObject(job, 1)             # the whole job, so nothing the candidate started survives
            if kernel.WaitForSingleObject(info.hProcess, 10000) != 0:
                status += "_and_not_killed"
            break
        reader.join(timeout=5)
        if state["over"] and status == "finished":
            status = "output_flood"                       # it finished between two looks, but it did pass the limit
        code = wintypes.DWORD()
        kernel.GetExitCodeProcess(info.hProcess, ctypes.byref(code))
        record.update(status=status, exit_code=int(code.value), stdout_bytes=state["bytes"], stdout_capped=state["over"])
        if status == "finished":
            try:
                parsed = loads_strict(b"".join(chunks).decode("utf-8", errors="replace").strip().splitlines()[-1])
                if isinstance(parsed, list):
                    record["records"] = parsed
            except (ValueError, IndexError, RecursionError):
                pass
        return record
    finally:
        record["seconds"] = round(time.monotonic() - started, 2)
        if job:
            kernel.CloseHandle(job)                       # kill-on-close: ends anything still inside
        for handle in (info.hThread, info.hProcess, token):
            if handle:
                kernel.CloseHandle(handle)
        for fd in (write_fd, read_fd, null_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass


PROGRESS = []          # what this runner has written to progress.log, kept here to detect tampering


def note(text: str) -> None:
    """A breadcrumb in the report folder, so a runner that dies leaves a trace of how far it got.
    The whole file is rewritten from this runner's own memory each time."""
    PROGRESS.append(f"{time.strftime('%H:%M:%S')} {text}\n")
    try:
        (OUT / "progress.log").write_bytes("".join(PROGRESS).encode("utf-8"))
    except OSError:
        pass


def report_folder_tampering() -> list:
    """The report folder is a host share, and Windows does not apply integrity levels to it: measured, a
    low-integrity candidate can create files there. So after every candidate the runner looks. Anything
    other than its own progress.log, byte for byte, is tampering; extra files are removed."""
    found = []
    try:
        for path in sorted(OUT.iterdir()):
            if path.name == "progress.log" and path.is_file():
                if path.read_bytes() != "".join(PROGRESS).encode("utf-8"):
                    found.append("progress.log changed")
                continue
            found.append(path.name[:80])
            try:
                shutil.rmtree(path) if path.is_dir() else path.unlink()
            except OSError:
                found.append("could not remove " + path.name[:80])
    except OSError as error:
        found.append("could not list: " + type(error).__name__)
    return found[:20]


def run_entry(entry_id: str) -> dict:
    source, folder = IN / "entries" / entry_id, WORK / entry_id
    shutil.copytree(source, folder)
    shutil.copy(IN / "__driver__.py", folder / "__driver__.py")
    note(f"start {entry_id}")
    record = {"id": entry_id, **run_confined(folder)}
    tampering = report_folder_tampering()
    if tampering:
        record.update(status="report_folder_tampered", records=None, report_folder_tampering=tampering)
    note(f"end {entry_id} {record.get('status')}")
    return record


def main() -> None:
    started = time.monotonic()
    result = {"guest_runner": "cq1-sandbox-8", "environment": {}, "entries": [], "complete": False,
              "limits": {"entry_timeout_s": ENTRY_TIMEOUT_S, "max_output_bytes": MAX_OUTPUT_BYTES,
                         "memory_limit_bytes": MEMORY_LIMIT_BYTES, "active_process_limit": 1,
                         "candidate_integrity": LOW_INTEGRITY_RID}}
    try:
        result["environment"] = environment_facts()
        kernel, advapi = windows()
        result["runner_protection"] = protect_self(kernel, advapi)
        note(f"runner protected {result['runner_protection']}")
        if result["runner_protection"]["fresh_terminate_handle_refused"] is not True:
            raise RuntimeError("runner not protected")       # no candidate is run beside an unprotected runner
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
        result["runner_error"] = type(error).__name__ + ": " + str(error)
    result["total_seconds"] = round(time.monotonic() - started, 1)
    # Written once, at the very end, after every candidate job has been closed.
    (OUT / "results.json").write_text(json.dumps(result), encoding="utf-8")
    (OUT / "DONE").write_text("done\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    subprocess.run(["shutdown", "/s", "/t", "5", "/f"], capture_output=True)     # closes the sandbox
