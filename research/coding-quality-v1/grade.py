"""CODE-Q1 grader. Standard library only. It never contacts a model or the network.

Commands:
  python grade.py verify-fixtures          Check the suite itself: manifest hashes, every
                                           reference passes every case, every decoy fails.
                                           Runs only code that is part of this repository.
  python grade.py static TASK DRAFT        Structural checks on one saved draft. Runs nothing.
  python grade.py semantic TASK DRAFT      Run the draft against the hidden cases. This EXECUTES
                                           model-written code, so it refuses unless it is told it
                                           is inside a disposable sandbox AND the manifest enables execution.
                                           The flag is an acknowledgement, not containment: this
                                           program does not create or verify a sandbox (see README).

DRAFT is either a text file with the model's answer, or a JSON file saved by the local draft
helper (fields "content", "finish_reason", "truncated").

Results keep four things apart: transport (did a complete answer arrive), structure (fences,
syntax, required names), semantics (hidden cases) and "not assessed". A structural pass is
never reported as correct code.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*([A-Za-z0-9_+-]*)\s*$")
FILE_MARK = re.compile(r"^#\s*file:\s*([A-Za-z_][A-Za-z0-9_]*\.py)\s*$")
PYTHON_LABELS = {"python", "python3", "py", ""}
MAX_DRAFT_BYTES = 262144
RUN_TIMEOUT_S = 10
MAX_CHILD_OUTPUT_BYTES = 1048576
SANDBOX_ENV = "CODE_Q1_SANDBOX"

# Child process: imports the candidate modules from its working directory and calls them.
# It receives only the calls and their arguments. Expected values never enter the candidate's
# folder or process, and the child does not decide pass or fail: it reports what happened and
# the parent (judge) compares. Kept as source text so the child needs no import of this file.
DRIVER = r'''
import copy, importlib, json, sys
sys.path.insert(0, ".")
calls = json.load(open("__calls__.json", encoding="utf-8"))
def plain(value):
    """True only for exact JSON types; a tuple, set, subclass or custom object is not plain."""
    if value is None or type(value) in (bool, int, float, str):
        return True
    if type(value) is list:
        return all(plain(item) for item in value)
    if type(value) is dict:
        return all(type(key) is str and plain(item) for key, item in value.items())
    return False
out = []
for call in calls:
    module_name, _, func_name = call["call"].partition(".")
    args = copy.deepcopy(call["args"])
    record = {"status": "returned", "args_after": None, "value": None, "same_object_as_input": False}
    try:
        func = getattr(importlib.import_module(module_name), func_name)
    except BaseException as error:
        out.append({"status": "import_error", "error": type(error).__name__}); continue
    try:
        got = func(*args)
    except BaseException as error:
        record.update(status="raised", error=type(error).__name__)
    else:
        if plain(got):
            record["value"] = got
            record["same_object_as_input"] = any(got is arg for arg in args if type(arg) in (list, dict))
        else:
            record.update(status="not_json", error=type(got).__name__)
    record["args_after"] = args if plain(args) else "not_json"
    out.append(record)
print(json.dumps(out))
'''


def same(a, b) -> bool:
    """Type-strict equality on JSON values: bool is not int, int is not float, list order counts."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, float):
        return abs(a - b) <= 1e-9
    return a == b


def loads_strict(text: str):
    """json.loads that refuses what the lenient parser lets through: a repeated key in an object
    (the last one would silently win) and the non-JSON constants NaN and Infinity."""
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            raise ValueError("repeated key")
        return dict(items)

    def constant(name):
        raise ValueError("non-JSON constant " + name)

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


_OBSERVED = {"status", "args_after", "value", "same_object_as_input"}
RECORD_FIELDS = {"import_error": {"status", "error"}, "returned": _OBSERVED,
                 "raised": _OBSERVED | {"error"}, "not_json": _OBSERVED | {"error"}}


def record_shape_ok(record) -> bool:
    """Exactly the fields the driver writes for that status, with the types it writes. Nothing missing, nothing extra."""
    if not isinstance(record, dict) or not isinstance(record.get("status"), str) or record["status"] not in RECORD_FIELDS:
        return False
    if set(record) != RECORD_FIELDS[record["status"]]:
        return False
    if "error" in record and not (isinstance(record["error"], str) and record["error"]):
        return False
    if "same_object_as_input" in record and type(record["same_object_as_input"]) is not bool:
        return False
    if record["status"] in ("raised", "not_json") and (record["value"] is not None or record["same_object_as_input"] is not False):
        return False
    return True


def case_shape_ok(case) -> bool:
    """A case expects EITHER a value or a named exception, never both and never neither."""
    if not isinstance(case, dict) or not isinstance(case.get("args"), list) or ("expect" in case) == ("raises" in case):
        return False
    return "raises" not in case or (isinstance(case["raises"], str) and bool(case["raises"]))


def judge(case: dict, record) -> dict:
    """Decide one case from the child's report. Runs in the judge process only.

    A pass needs a positive match: a well-formed record AND either the expected value or the expected
    exception name. Absent fields never compare equal to absent expectations.
    """
    if not case_shape_ok(case):
        return {"ok": False, "why": "bad case"}
    if not record_shape_ok(record):
        return {"ok": False, "why": "bad result"}
    if record["status"] == "import_error":
        return {"ok": False, "why": "import: " + record["error"]}
    if not same(record["args_after"], case["args"]):
        return {"ok": False, "why": "mutated input"}
    if record["status"] == "raised":
        return {"ok": "raises" in case and case["raises"] == record["error"], "why": "raised " + record["error"]}
    if "raises" in case:
        return {"ok": False, "why": "no exception"}
    if record["status"] == "not_json":
        return {"ok": False, "why": "returned " + record["error"]}
    if case.get("new_object") and record["same_object_as_input"] is not False:
        return {"ok": False, "why": "returned the input object"}
    return {"ok": same(record["value"], case["expect"]), "why": "value"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_hash(folder: Path) -> str:
    entries = {p.name: sha256(p) for p in sorted(folder.iterdir()) if p.is_file()}
    joined = "".join(f"{name}\0{digest}\n" for name, digest in sorted(entries.items()))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def manifest() -> dict:
    return json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))


def load_task(task_id: str) -> dict:
    tasks = manifest()["tasks"]
    if task_id not in tasks:
        raise SystemExit(f"unknown task {task_id}; known: {', '.join(tasks)}")
    task = dict(tasks[task_id], id=task_id)
    base = FIX / task_id
    task["public"] = json.loads((base / "public_tests.json").read_text(encoding="utf-8"))
    task["hidden"] = json.loads((base / "hidden_tests.json").read_text(encoding="utf-8"))
    return task


def read_draft(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) > MAX_DRAFT_BYTES:
        raise SystemExit("draft is too large")
    text = raw.decode("utf-8", errors="replace")
    info = {"content": text, "finish_reason": None, "truncated": None}
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if not isinstance(data, dict) or not isinstance(data.get("content"), str):
            raise SystemExit("draft JSON needs a string 'content' field")
        info.update(content=data["content"], finish_reason=data.get("finish_reason"),
                    truncated=data.get("truncated"))
    return info


def extract_blocks(content: str) -> tuple[list[str], bool]:
    """Fenced Python blocks in order, and whether every fence was closed."""
    blocks, lines, active = [], [], None
    for line in content.splitlines():
        match = FENCE.match(line)
        if active is None:
            if match and match.group(2).lower() in PYTHON_LABELS:
                active, lines = match.group(1), []
        elif match and match.group(1)[0] == active[0] and len(match.group(1)) >= len(active) \
                and not match.group(2):
            blocks.append("\n".join(lines) + "\n")
            active = None
        else:
            lines.append(line)
    return blocks, active is None


def assign_files(blocks: list[str], files: list[str]) -> tuple[dict[str, str], list[str]]:
    """Map code blocks to the task's files. Returns (mapping, problems)."""
    problems, mapping = [], {}
    if len(files) == 1:
        if len(blocks) != 1:
            problems.append(f"expected exactly one Python block, found {len(blocks)}")
        if blocks:
            mapping[files[0]] = blocks[0]
        return mapping, problems
    for block in blocks:
        first = block.splitlines()[0] if block.strip() else ""
        mark = FILE_MARK.match(first.strip())
        if not mark:
            problems.append("a block does not start with a '# file: name.py' line")
        elif mark.group(1) not in files:
            problems.append(f"unexpected file {mark.group(1)}")
        elif mark.group(1) in mapping:
            problems.append(f"file {mark.group(1)} given twice")
        else:
            mapping[mark.group(1)] = block
    problems += [f"missing file {name}" for name in files if name not in mapping]
    return mapping, problems


def static_grade(task: dict, draft: dict) -> dict:
    """Structure only. Nothing from the draft is imported or run."""
    content = draft["content"]
    blocks, closed = extract_blocks(content)
    if not blocks and closed and "```" not in content and "~~~" not in content and len(task["files"]) == 1:
        blocks = [content if content.endswith("\n") else content + "\n"]   # bare code, no fence
    mapping, problems = assign_files(blocks, task["files"])
    if not closed:
        problems.append("unclosed code fence")
    defined: set[str] = set()
    for name, code in mapping.items():
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            problems.append(f"{name} does not parse")
            continue
        module = name[:-3]
        defined |= {f"{module}.{node.name}" for node in tree.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    missing = [c for c in task["required_callables"] if c not in defined]
    if missing:
        problems.append("missing required functions: " + ", ".join(missing))
    finish = draft["finish_reason"]
    if draft["truncated"] is True or finish not in (None, "stop"):
        transport = "incomplete"                  # known truncation wins over missing metadata
    elif finish == "stop" and draft["truncated"] is False:
        transport = "complete"
    else:
        transport = "unknown"
    if transport == "incomplete":
        problems.append(f"answer not complete (finish_reason={finish}, truncated={draft['truncated']})")
    return {"task": task["id"], "transport": transport,
            "structure": "pass" if not problems else "fail", "problems": problems,
            "files": mapping, "semantics": "not_assessed", "code_executed": False}


def run_cases(files: dict[str, str], cases: list[dict]) -> list[dict]:
    """Run code in a child interpreter in a temp folder; judge its reports here.

    Callers decide whether running the code is allowed. The child sees calls and arguments only.
    """
    calls = [{"call": c["call"], "args": c["args"]} for c in cases]
    with tempfile.TemporaryDirectory(prefix="code-q1-") as temp:
        folder = Path(temp)
        for name, code in files.items():
            (folder / name).write_text(code, encoding="utf-8", newline="\n")
        (folder / "__calls__.json").write_text(json.dumps(calls), encoding="utf-8")
        (folder / "__driver__.py").write_text(DRIVER, encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k.upper() in ("SYSTEMROOT", "PATH", "TEMP", "TMP")}
        env["PYTHONIOENCODING"] = "utf-8"
        try:
            done = subprocess.run([sys.executable, "-I", "-B", "__driver__.py"], cwd=folder, env=env,
                                  capture_output=True, timeout=RUN_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return [{"ok": False, "why": "timeout"} for _ in cases]
        if done.returncode != 0:
            return [{"ok": False, "why": f"crashed (exit code {done.returncode})"} for _ in cases]
        if len(done.stdout) > MAX_CHILD_OUTPUT_BYTES:
            return [{"ok": False, "why": "output over the limit"} for _ in cases]
        output = done.stdout.decode("utf-8", errors="replace")
        try:
            records = loads_strict(output.strip().splitlines()[-1])
        except (ValueError, IndexError, RecursionError):
            return [{"ok": False, "why": "crashed"} for _ in cases]
        if not isinstance(records, list) or len(records) != len(cases):
            return [{"ok": False, "why": "bad result"} for _ in cases]
        return [judge(case, record) for case, record in zip(cases, records)]


def summarise(results: list[dict]) -> dict:
    passed = sum(1 for r in results if r.get("ok") is True)
    return {"passed": passed, "total": len(results),
            "failures": [f"case {i}: {r.get('why')}" for i, r in enumerate(results) if r.get("ok") is not True]}


def semantic_grade(task: dict, draft: dict, in_sandbox: bool) -> dict:
    if manifest().get("generated_code_execution_enabled") is not True:
        raise SystemExit("Refused: the manifest has generated_code_execution_enabled set to false.")
    if not in_sandbox:
        raise SystemExit(
            "Refused: this would execute model-written code on this machine. Run it only inside a "
            f"disposable sandbox, with --i-am-in-a-sandbox and {SANDBOX_ENV}=1 set there.")
    result = static_grade(task, draft)
    if result["structure"] != "pass":
        result["semantics"] = "not_run_structure_failed"
        return result
    outcome = summarise(run_cases(result["files"], task["public"] + task["hidden"]))
    result.update(semantics="pass" if outcome["passed"] == outcome["total"] else "fail",
                  cases=outcome, code_executed=True)
    return result


def verify_fixtures() -> dict:
    """Run only repository-authored code: references must pass, decoys and starters must fail."""
    report, ok = {}, True
    data = manifest()
    for task_id, entry in data["tasks"].items():
        base = FIX / task_id
        problems = []
        checks = {"prompt_sha256": sha256(base / "prompt.txt"),
                  "public_tests_sha256": sha256(base / "public_tests.json"),
                  "hidden_tests_sha256": sha256(base / "hidden_tests.json"),
                  "reference_sha256": tree_hash(base / "reference"),
                  "decoy_sha256": tree_hash(base / "decoy")}
        if entry["starter_sha256"]:
            checks["starter_sha256"] = tree_hash(base / "starter")
        problems += [f"{key} differs from manifest" for key, value in checks.items() if entry[key] != value]
        task = load_task(task_id)
        cases = task["public"] + task["hidden"]

        def files_of(kind):
            return {p.name: p.read_text(encoding="utf-8") for p in sorted((base / kind).iterdir())}

        reference = summarise(run_cases(files_of("reference"), cases))
        if reference["passed"] != reference["total"]:
            problems.append("reference fails: " + "; ".join(reference["failures"]))
        decoy = summarise(run_cases(files_of("decoy"), task["hidden"]))
        if decoy["passed"] == decoy["total"]:
            problems.append("decoy passes every hidden case (tests too weak)")
        static = static_grade(task, {"content": "\n\n".join(
            "```python\n" + (f"# file: {name}\n" if len(task["files"]) > 1 else "") + code + "```"
            for name, code in files_of("reference").items()), "finish_reason": "stop", "truncated": False})
        if static["structure"] != "pass":
            problems.append("reference fails the static check: " + "; ".join(static["problems"]))
        prompt = (base / "prompt.txt").read_text(encoding="utf-8")
        if any(json.dumps(c["args"], ensure_ascii=False) in prompt for c in task["hidden"]
               if len(json.dumps(c["args"])) > 12):
            problems.append("a hidden case appears in the prompt")
        report[task_id] = {"cases": len(cases), "reference": f"{reference['passed']}/{reference['total']}",
                           "decoy_hidden": f"{decoy['passed']}/{decoy['total']}",
                           "prompt_chars": len(prompt), "problems": problems}
        ok = ok and not problems
    return {"ok": ok, "tasks": report}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify-fixtures")
    for name in ("static", "semantic"):
        p = sub.add_parser(name)
        p.add_argument("task")
        p.add_argument("draft", type=Path)
        if name == "semantic":
            p.add_argument("--i-am-in-a-sandbox", action="store_true")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.command == "verify-fixtures":
        result = verify_fixtures()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["ok"] else 1
    task = load_task(args.task)
    draft = read_draft(args.draft)
    if args.command == "static":
        result = static_grade(task, draft)
    else:
        result = semantic_grade(task, draft, args.i_am_in_a_sandbox and os.environ.get(SANDBOX_ENV) == "1")
    result.pop("files", None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["structure"] == "pass" and result["semantics"] in ("pass", "not_assessed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
