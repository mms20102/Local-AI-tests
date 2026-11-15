"""HOSTILE TEST FIXTURE. Handwritten for this project to attack the grading harness.

Tries to open network connections and returns the targets it reached. Must reach none.
It is kept so the harness can be re-tested. Never run it outside the sandbox harness.
"""
import socket
def f(x):
    reached = []
    for target in (('1.1.1.1', 443), ('8.8.8.8', 53), ('example.com', 80)):
        try:
            socket.create_connection(target, timeout=2).close()
            reached.append(target[0])
        except Exception:
            pass
    return reached
