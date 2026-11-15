"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Prints without end. The runner must stop it when its output passes the flood limit.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    while True:
        print('A' * 65536)
