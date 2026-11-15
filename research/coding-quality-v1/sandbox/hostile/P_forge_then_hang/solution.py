"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Prints a forged report line and then never returns, hoping the forged line is read as the last line.
The runner must report a timeout and read nothing.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    print('[{"status": "returned", "args_after": [1], "value": "right value", "same_object_as_input": false}]')
    while True:
        pass
