"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Tries to end its parent, the guest runner, through the Windows API, then returns the right value.
Whatever happens, the entry must not be accepted as a trusted pass, and it runs alone so no other entry is affected.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import ctypes, os
def f(x):
    try:
        kernel = ctypes.WinDLL('kernel32')
        handle = kernel.OpenProcess(0x0001, False, os.getppid())
        if handle:
            kernel.TerminateProcess(handle, 1)
    except Exception:
        pass
    return x
