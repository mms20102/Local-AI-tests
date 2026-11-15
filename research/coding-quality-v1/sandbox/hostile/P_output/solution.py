"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Writes 20 MB to standard output through sys, then returns the right value.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import sys
def f(x):
    sys.stdout.write('A' * (20 * 1024 * 1024))
    return x
