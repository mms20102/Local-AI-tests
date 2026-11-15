"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Never returns. The runner must stop it at the deadline and carry on with the next entry.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    while True:
        pass
