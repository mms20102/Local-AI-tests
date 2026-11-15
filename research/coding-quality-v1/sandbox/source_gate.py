"""Decide, from source text alone, whether a candidate stays inside plain computation.

Nothing is imported or executed: the candidate's files are parsed into syntax trees and read.

Why this exists. Inside the sandbox guest the candidate runs in the same interpreter as the driver
that observes it, and in the same guest as the runner. Code that can reach a module such as `os`,
`sys`, `ctypes`, `json` or `copy`, or the interpreter's own frames and code objects, could start
processes, touch files, end the runner, or quietly change what the driver reports. Python offers no
way to stop that from inside the interpreter. What CAN be done is to refuse, before anything runs,
every construct through which such a thing can be reached. A candidate that passes is confined to
arithmetic, data structures, its own functions and classes, printing, and a short list of named
imports that hand out values and functions, never modules.

A candidate that does not pass is not called unsafe. It is outside what this gate can vouch for, so
it is run alone in its own sandbox session and its result is marked as an untrusted observation.

The rules, checked on every node of every file:

1. Imports.
   - `import X` only for the candidate's own modules and for MODULES_PLAIN (implemented in C, with
     no other module among their attributes).
   - `from M import a, b` only when M is in FROM_ALLOWED and each name is listed for it. No `*`, no
     relative import. A general `import collections` is refused on purpose: `collections._sys` is
     the `sys` module, and `from typing import sys` would hand over `sys` as well.
2. Names. None of FORBIDDEN_NAMES, and no double-underscore name except `__name__`.
3. Attributes, and the attribute names in `match` class patterns (`case object(__class__=c)` reads
   an attribute without an attribute expression). No double-underscore attribute except the short
   list in DUNDER_ATTRIBUTES_ALLOWED, which yield strings or the candidate's own methods; and none
   of FORBIDDEN_ATTRIBUTES, which lead from generators, coroutines and tracebacks to frames, and
   from frames to the builtins and globals.
4. String constants may not contain a double-underscore word other than `__main__`, so names such
   as `__import__` or `__class__` cannot be smuggled in as dictionary keys or format templates.

Defining special METHODS such as `__init__` or `__exit__` in the candidate's own classes is allowed:
that is a definition, not an access. The traceback such a method may receive is useless without the
forbidden attributes.

This is a reading of the source against rules I believe are sufficient. It is not a proof about
Python, and it has not been independently reviewed. The escape routes it was written against are
kept as tests in ../test_sandbox_gate.py.
"""
from __future__ import annotations

import ast
import re

MODULES_PLAIN = {"math", "cmath", "itertools", "unicodedata"}

FROM_ALLOWED = {
    "math": None,                 # None: any public name (no leading underscore)
    "cmath": None,
    "itertools": None,
    "collections": {"Counter", "OrderedDict", "defaultdict", "deque", "namedtuple", "ChainMap"},
    "functools": {"reduce", "lru_cache", "cache", "partial", "cmp_to_key", "total_ordering", "wraps"},
    "typing": {"Any", "Callable", "Dict", "FrozenSet", "Generic", "Iterable", "Iterator", "List", "Literal", "Mapping",
               "MutableMapping", "NamedTuple", "Optional", "Sequence", "Set", "Tuple", "Type", "TypeVar", "Union",
               "Final", "Hashable", "Deque", "DefaultDict", "Counter", "Generator", "TypedDict", "Protocol", "cast"},
    "dataclasses": {"dataclass", "field", "asdict", "astuple", "replace"},
    "enum": {"Enum", "IntEnum", "auto"},
    "decimal": {"Decimal", "ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_DOWN", "ROUND_UP", "InvalidOperation"},
    "fractions": {"Fraction"},
    "datetime": {"date", "datetime", "time", "timedelta", "timezone"},
    "heapq": {"heappush", "heappop", "heapify", "heapreplace", "heappushpop", "nlargest", "nsmallest", "merge"},
    "bisect": {"bisect", "bisect_left", "bisect_right", "insort", "insort_left", "insort_right"},
    "string": {"ascii_letters", "ascii_lowercase", "ascii_uppercase", "digits", "hexdigits", "octdigits", "punctuation",
               "whitespace", "printable"},
    "re": {"match", "fullmatch", "search", "sub", "subn", "split", "findall", "finditer", "escape",
           "IGNORECASE", "MULTILINE", "DOTALL", "VERBOSE", "ASCII", "UNICODE", "I", "M", "S", "X", "A", "U"},
    "unicodedata": {"normalize", "category", "name", "combining", "east_asian_width", "decimal", "digit", "numeric"},
    "operator": {"itemgetter", "add", "sub", "mul", "truediv", "floordiv", "mod", "neg", "lt", "le", "eq", "ne", "ge", "gt"},
    "copy": {"deepcopy", "copy"},
    "json": {"dumps", "loads"},
    "__future__": {"annotations"},
}

FORBIDDEN_NAMES = {
    "open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "globals", "locals", "vars", "getattr",
    "setattr", "delattr", "help", "exit", "quit", "memoryview", "copyright", "credits", "license",
}
DUNDER_NAMES_ALLOWED = {"__name__"}
DUNDER_ATTRIBUTES_ALLOWED = {"__name__", "__doc__", "__qualname__", "__init__", "__str__", "__repr__", "__eq__", "__lt__",
                             "__hash__", "__len__", "__iter__", "__next__"}
# From a generator, coroutine or traceback to its frame; from a frame to builtins and globals; code objects.
FORBIDDEN_ATTRIBUTES = {
    "gi_frame", "gi_code", "gi_yieldfrom", "cr_frame", "cr_code", "cr_await", "cr_origin", "ag_frame", "ag_code", "ag_await",
    "tb_frame", "tb_next", "f_back", "f_builtins", "f_code", "f_globals", "f_locals", "f_trace",
    "co_code", "co_consts", "co_names", "co_varnames", "func_globals", "func_code",
}
DUNDER_WORD = re.compile(r"__[A-Za-z0-9_]+__")
STRING_DUNDERS_ALLOWED = {"__main__"}


def _is_dunder(text: str) -> bool:
    return len(text) > 4 and text.startswith("__") and text.endswith("__")


def _attribute_problem(name: str) -> str | None:
    if name in FORBIDDEN_ATTRIBUTES:
        return f"attribute .{name}"
    if _is_dunder(name) and name not in DUNDER_ATTRIBUTES_ALLOWED:
        return f"attribute .{name}"
    return None


def _name_problem(name: str) -> str | None:
    if name in FORBIDDEN_NAMES or (_is_dunder(name) and name not in DUNDER_NAMES_ALLOWED):
        return f"name {name}"
    return None


def reach_of(files: dict[str, str]) -> dict:
    """Return {"plain": bool, "reasons": [...]} for a candidate's files ({name.py: source})."""
    own = {name[:-3] for name in files}
    reasons: list[str] = []

    def note(text: str | None) -> None:
        if text and text not in reasons:
            reasons.append(text)

    for file_name, code in sorted(files.items()):
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            note(f"{file_name}: does not parse")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in own and alias.name not in MODULES_PLAIN:
                        note(f"import {alias.name}")
                    note(_name_problem(alias.asname) if alias.asname else None)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.level:
                    note("relative import")
                elif module in own:
                    if any(alias.name == "*" for alias in node.names):
                        note(f"from {module} import *")
                elif module not in FROM_ALLOWED:
                    note(f"from {module} import ...")
                else:
                    allowed = FROM_ALLOWED[module]
                    for alias in node.names:
                        ok = (alias.name != "*" and not alias.name.startswith("_")) if allowed is None else alias.name in allowed
                        if not ok:
                            note(f"from {module} import {alias.name}")
                for alias in node.names:
                    note(_name_problem(alias.asname) if alias.asname else None)
            elif isinstance(node, ast.Name):
                note(_name_problem(node.id))
            elif isinstance(node, ast.Attribute):
                note(_attribute_problem(node.attr))
            elif isinstance(node, ast.MatchClass):
                for name in node.kwd_attrs:
                    note(_attribute_problem(name))
            elif isinstance(node, (ast.MatchAs, ast.MatchStar)):
                note(_name_problem(node.name) if node.name else None)
            elif isinstance(node, ast.MatchMapping):
                note(_name_problem(node.rest) if node.rest else None)
            elif isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
                text = node.value if isinstance(node.value, str) else node.value.decode("latin-1")
                if any(word not in STRING_DUNDERS_ALLOWED for word in DUNDER_WORD.findall(text)):
                    note("string containing a double-underscore name")
            elif isinstance(node, (ast.Global, ast.Nonlocal)):
                for name in node.names:
                    note(_name_problem(name))
            elif isinstance(node, ast.arg):
                note(_name_problem(node.arg))
            elif isinstance(node, ast.ExceptHandler):
                note(_name_problem(node.name) if node.name else None)
            elif isinstance(node, ast.keyword):
                note(_name_problem(node.arg) if node.arg else None)
    return {"plain": not reasons, "reasons": reasons}
