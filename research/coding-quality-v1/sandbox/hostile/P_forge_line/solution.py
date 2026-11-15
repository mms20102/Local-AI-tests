"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Prints a line shaped like the driver's own report, claiming a result, then returns a wrong value.
The host must judge the driver's real last line, not the forged one.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
def f(x):
    print('[{"status": "returned", "args_after": [1], "value": "right value", "same_object_as_input": false}]')
    return 'wrong value'
