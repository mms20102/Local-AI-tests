"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Allocates without end. The job's memory limit must stop it without harming the runner.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    hoard = []
    while True:
        hoard.append([0] * 10_000_000)
