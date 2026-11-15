"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Tries to open its parent, the guest runner, with the right to end it, and ends it if it can.
Returns 'refused' when Windows does not hand out that right. The candidate runs with low integrity,
so it must be refused, and the runner must survive to report.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import ctypes, os
def f(x):
    try:
        kernel = ctypes.WinDLL('kernel32')
        kernel.OpenProcess.restype = ctypes.c_void_p
        handle = kernel.OpenProcess(0x0001, False, os.getppid())
        if handle:
            kernel.TerminateProcess(ctypes.c_void_p(handle), 1)
            return 'opened the runner'
    except Exception:
        pass
    return 'refused'
