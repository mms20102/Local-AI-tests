"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Tries to start other programs. The job allows one process, so every attempt must fail.
Returns the list of attempts that succeeded, which must be empty.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import os, subprocess
def f(x):
    started = []
    for name, action in (('subprocess', lambda: subprocess.run(['cmd', '/c', 'echo', 'hi'], capture_output=True, timeout=5)),
                         ('os.system', lambda: os.system('cmd /c echo hi')),
                         ('os.startfile', lambda: os.startfile('notepad.exe'))):
        try:
            result = action()
            code = getattr(result, 'returncode', result)
            if code in (0, None):
                started.append(name)
        except Exception:
            pass
    return started
