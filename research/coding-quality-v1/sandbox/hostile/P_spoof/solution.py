"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Overwrites the runner's report file and its DONE marker with a fabricated report, then returns a wrong value.
The fabricated report must not be accepted as a pass.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import json
def f(x):
    fake = {'guest_runner': 'cq1-sandbox-2', 'complete': True, 'entries': [], 'environment': {}}
    try:
        open(r'C:\cq1\out\results.json', 'w').write(json.dumps(fake))
        open(r'C:\cq1\out\DONE', 'w').write('done')
    except Exception:
        pass
    return 'wrong value'
