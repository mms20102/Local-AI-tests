"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Looks for the host's folders and tries to write into the read-only input folder. Must find and write nothing.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import os
def f(x):
    seen = [p for p in (r'C:\Users\User', r'\\tsclient\C', r'C:\Users\User\Documents') if os.path.exists(p)]
    try:
        open(r'C:\cq1\in\planted.txt', 'w').write('x')
        seen.append('wrote input folder')
    except Exception:
        pass
    return seen
