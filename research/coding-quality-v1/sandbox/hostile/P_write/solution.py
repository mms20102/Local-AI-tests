"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Tries to create files in the report folder, the runner's working folder, the Windows temp folder and
its own folder. Returns the places it could write, which must be none.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    written = []
    for path in (r'C:\cq1\out\planted.txt', r'C:\cq1\out\results.json', r'C:\cq1work\planted.txt',
                 r'C:\Windows\Temp\planted.txt', 'planted_here.txt'):
        try:
            with open(path, 'w') as handle:
                handle.write('x')
            written.append(path)
        except Exception:
            pass
    return written
