"""Tests for sandbox/source_gate.py and the hostile fixtures. Nothing here executes a candidate:
sources are parsed and read. Standard library only."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "sandbox"))
import source_gate  # noqa: E402

import grade  # noqa: E402


def plain(code, name="solution.py", **others):
    return source_gate.reach_of({name: code, **others})


class EscapeRouteTests(unittest.TestCase):
    """Each of these reaches a module, the interpreter's internals, files or processes. All must be refused."""

    ESCAPES = {
        "plain import of os": "import os\ndef f(x):\n    return os.getcwd()\n",
        "import as": "import subprocess as s\ndef f(x):\n    return 1\n",
        "from os import": "from os import system\ndef f(x):\n    return 1\n",
        "import of a Python module that exposes sys": "import collections\ndef f(x):\n    return collections._sys.modules\n",
        "from typing import sys": "from typing import sys\ndef f(x):\n    return sys.modules\n",
        "from collections import private name": "from collections import _sys\ndef f(x):\n    return 1\n",
        "star import": "from math import *\ndef f(x):\n    return 1\n",
        "relative import": "from . import other\ndef f(x):\n    return 1\n",
        "dunder import call": "def f(x):\n    return __import__('os')\n",
        "builtins name": "def f(x):\n    return __builtins__\n",
        "builtins string subscript": "def f(x):\n    return __builtins__['open']('a')\n",
        "builtins reached through a string key": "def f(d):\n    return d['__builtins__']['open']\n",
        "eval": "def f(x):\n    return eval('1')\n",
        "exec": "def f(x):\n    exec('import os')\n",
        "compile": "def f(x):\n    return compile('1', 'a', 'eval')\n",
        "open": "def f(x):\n    return open('a').read()\n",
        "getattr": "def f(x):\n    return getattr(x, 'real')\n",
        "globals": "def f(x):\n    return globals()\n",
        "vars": "def f(x):\n    return vars(x)\n",
        "class attribute chain": "def f(x):\n    return ().__class__.__bases__[0].__subclasses__()\n",
        "function globals": "def f(x):\n    return f.__globals__\n",
        "dict attribute": "def f(x):\n    return x.__dict__\n",
        "generator frame": "def f(x):\n    g = (i for i in [1])\n    return g.gi_frame.f_builtins\n",
        "coroutine frame": "async def c():\n    pass\ndef f(x):\n    return c().cr_frame\n",
        "frame globals": "def f(x):\n    return x.f_globals\n",
        "traceback frame from __exit__": ("class C:\n    def __enter__(self):\n        return self\n"
                                          "    def __exit__(self, t, e, tb):\n        self.frame = tb.tb_frame\n        return True\n"
                                          "def f(x):\n    with C() as c:\n        1 / 0\n    return c.frame\n"),
        "traceback attribute": "def f(x):\n    try:\n        1 / 0\n    except Exception as e:\n        return e.__traceback__\n",
        "match class pattern reading a dunder": "def f(x):\n    match x:\n        case object(__class__=c):\n            return c\n",
        "match class pattern reading a frame": "def f(x):\n    match x:\n        case object(gi_frame=fr):\n            return fr\n",
        "format template reading internals": "def f(x):\n    return '{0.__class__}'.format(x)\n",
        "dunder dictionary key": "def f(x):\n    return x['__import__']\n",
        "dunder in bytes": "def f(x):\n    return b'__import__'\n",
        "code object": "def f(x):\n    return x.co_consts\n",
        "breakpoint": "def f(x):\n    breakpoint()\n",
        "input": "def f(x):\n    return input()\n",
        "exit": "def f(x):\n    exit(0)\n",
        "argument named like a forbidden builtin": "def f(open):\n    return open\n",
        "import alias to a dunder": "import math as __builtins__\ndef f(x):\n    return 1\n",
        "does not parse": "def f(x:\n",
        "attrgetter": "from operator import attrgetter\ndef f(x):\n    return attrgetter('real')(x)\n",
        "re.compile is not offered": "from re import compile\ndef f(x):\n    return 1\n",
    }

    def test_every_escape_route_is_refused(self):
        for label, code in self.ESCAPES.items():
            result = plain(code)
            self.assertFalse(result["plain"], label)
            self.assertTrue(result["reasons"], label)

    def test_escape_hidden_in_a_second_file_is_refused(self):
        result = source_gate.reach_of({"solution.py": "from helper import g\ndef f(x):\n    return g(x)\n",
                                       "helper.py": "import os\ndef g(x):\n    return os.getcwd()\n"})
        self.assertFalse(result["plain"])


class OrdinaryCodeTests(unittest.TestCase):
    """Ordinary answers must not be turned away, or the gate would be useless."""

    ORDINARY = {
        "arithmetic and structures": "def f(xs):\n    return sorted({x * 2 for x in xs if x % 2 == 0})\n",
        "math module": "import math\ndef f(x):\n    return math.sqrt(x)\n",
        "from math": "from math import floor, pi\ndef f(x):\n    return floor(x * pi)\n",
        "collections names": "from collections import Counter, defaultdict\ndef f(xs):\n    return dict(Counter(xs))\n",
        "typing": "from typing import List, Optional\ndef f(xs: List[int]) -> Optional[int]:\n    return xs[0] if xs else None\n",
        "future annotations": "from __future__ import annotations\ndef f(x: int) -> int:\n    return x\n",
        "dataclass": "from dataclasses import dataclass\n@dataclass\nclass P:\n    x: int\ndef f(x):\n    return P(x).x\n",
        "own class with special methods": ("class A:\n    def __init__(self, v):\n        self.v = v\n"
                                           "    def __repr__(self):\n        return 'A'\n"
                                           "    def __eq__(self, o):\n        return self.v == o.v\n"
                                           "def f(x):\n    return A(x) == A(x)\n"),
        "super init": "class B:\n    def __init__(self):\n        self.v = 1\nclass C(B):\n    def __init__(self):\n        super().__init__()\ndef f(x):\n    return C().v\n",
        "type name in a message": "def f(x):\n    raise TypeError(type(x).__name__)\n",
        "main guard": "def f(x):\n    return x\nif __name__ == '__main__':\n    print(f(1))\n",
        "exceptions": "def f(x):\n    try:\n        return 1 / x\n    except ZeroDivisionError as e:\n        raise ValueError('zero') from e\n",
        "generators and lambdas": "def f(xs):\n    g = (x for x in xs)\n    return list(map(lambda v: v + 1, g))\n",
        "regular expression functions": "from re import sub, findall\ndef f(s):\n    return sub(r'\\s+', ' ', s), findall(r'\\d+', s)\n",
        "unicodedata": "import unicodedata\ndef f(s):\n    return unicodedata.normalize('NFC', s)\n",
        "printing": "def f(x):\n    print('working on', x)\n    return x\n",
        "deepcopy": "from copy import deepcopy\ndef f(x):\n    return deepcopy(x)\n",
        "match statement": "def f(x):\n    match x:\n        case [a, b]:\n            return a + b\n        case {'k': v}:\n            return v\n        case _:\n            return None\n",
        "docstring and arabic text": 'def f(x):\n    """يعيد القيمة كما هي."""\n    return x\n',
    }

    def test_ordinary_code_is_plain(self):
        for label, code in self.ORDINARY.items():
            result = plain(code)
            self.assertTrue(result["plain"], f"{label}: {result['reasons']}")

    def test_two_file_answer_importing_its_own_module(self):
        result = source_gate.reach_of({"invoice.py": "def subtotal(items):\n    return sum(q * c for q, c in items)\n",
                                       "summary.py": "from invoice import subtotal\ndef render(items):\n    return subtotal(items)\n"})
        self.assertTrue(result["plain"], result["reasons"])


class RepositoryContentTests(unittest.TestCase):
    def test_every_reference_and_decoy_is_plain(self):
        for task_id in sorted(grade.manifest()["tasks"]):
            for kind in ("reference", "decoy"):
                files = {p.name: p.read_text(encoding="utf-8") for p in sorted((grade.FIX / task_id / kind).iterdir())
                         if p.suffix == ".py"}
                result = source_gate.reach_of(files)
                self.assertTrue(result["plain"], f"{task_id} {kind}: {result['reasons']}")

    def test_published_first_pass_drafts_are_plain(self):
        folder = ROOT / "drafts-2026-11-14-first-pass"
        for task_id in sorted(grade.manifest()["tasks"]):
            draft = grade.static_grade(grade.load_task(task_id), grade.read_draft(folder / f"{task_id}.json"))
            result = source_gate.reach_of(draft["files"])
            self.assertTrue(result["plain"], f"{task_id}: {result['reasons']}")

    def test_hostile_fixtures_are_kept_and_classified(self):
        index = json.loads((ROOT / "sandbox" / "hostile" / "index.json").read_text(encoding="utf-8"))
        must_share = {"P_loop", "P_print_flood", "P_memory", "P_forge_line", "P_forge_then_hang"}
        must_be_alone = {"P_output", "P_network", "P_host_files", "P_spoof", "P_spawn", "P_kill_runner"}
        self.assertEqual(set(index), must_share | must_be_alone)
        for name, spec in index.items():
            path = ROOT / "sandbox" / "hostile" / name / "solution.py"
            source = path.read_text(encoding="utf-8")
            self.assertIn("HOSTILE TEST FIXTURE", source)
            self.assertEqual(source_gate.reach_of({"solution.py": source})["plain"], name in must_share, name)
            self.assertTrue(spec["cases"] and spec["expect"] and spec["what"])
            for case in spec["cases"]:
                self.assertTrue({"call", "args"} <= set(case))

    def test_gate_does_not_run_what_it_reads(self):
        marker = ROOT / "__gate_executed_marker__"
        code = f"open(r'{marker}', 'w').write('x')\ndef f(x):\n    return x\n"
        self.assertFalse(plain(code)["plain"])
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
