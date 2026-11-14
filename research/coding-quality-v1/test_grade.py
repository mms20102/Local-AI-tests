"""Offline tests for the CODE-Q1 grader. They run only code written in this repository.
Run from this folder:  python -B -m unittest test_grade
"""
import json
import os
import tempfile
import unittest
from pathlib import Path

import grade

FENCE = "```"


def answer(*blocks):
    return "\n\n".join(f"{FENCE}python\n{block}{FENCE}" for block in blocks)


def draft(content, finish="stop", truncated=False):
    return {"content": content, "finish_reason": finish, "truncated": truncated}


def reference(task_id):
    folder = grade.FIX / task_id / "reference"
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.iterdir())}


class SuiteTests(unittest.TestCase):
    def test_fixtures_verify(self):
        report = grade.verify_fixtures()
        self.assertTrue(report["ok"], report)
        self.assertEqual(len(report["tasks"]), 12)

    def test_manifest_matches_the_proposal_shape(self):
        tasks = grade.manifest()["tasks"]
        self.assertEqual(sorted(tasks), ["A01", "A02", "A03", "B01", "B02", "B03",
                                         "E01", "E02", "E03", "F01", "F02", "F03"])
        self.assertEqual(sum(t["prompt_language"] == "ar" for t in tasks.values()), 3)
        self.assertFalse(grade.manifest()["generated_code_execution_enabled"])

    def test_arabic_prompts_are_real_arabic(self):
        for task_id in ("A01", "A02", "A03"):
            text = (grade.FIX / task_id / "prompt.txt").read_text(encoding="utf-8")
            self.assertGreater(sum("؀" <= c <= "ۿ" for c in text), 100)
            self.assertNotIn("?" * 3, text)


class StaticTests(unittest.TestCase):
    def test_reference_answer_passes_structure_only(self):
        task = grade.load_task("F01")
        result = grade.static_grade(task, draft(answer(reference("F01")["solution.py"])))
        self.assertEqual((result["transport"], result["structure"]), ("complete", "pass"))
        self.assertEqual(result["semantics"], "not_assessed")
        self.assertFalse(result["code_executed"])

    def test_wrong_code_still_passes_structure(self):
        task = grade.load_task("F01")
        result = grade.static_grade(task, draft(answer("def stable_unique(values):\n    return []\n")))
        self.assertEqual(result["structure"], "pass")
        self.assertEqual(result["semantics"], "not_assessed")

    def test_truncated_answer_is_incomplete(self):
        task = grade.load_task("F01")
        result = grade.static_grade(task, draft(FENCE + "python\ndef stable_unique(values):\n    seen",
                                                finish="length", truncated=True))
        self.assertEqual(result["transport"], "incomplete")
        self.assertEqual(result["structure"], "fail")
        self.assertIn("unclosed code fence", result["problems"])

    def test_stop_does_not_hide_a_missing_function(self):
        task = grade.load_task("E02")
        result = grade.static_grade(task, draft(answer("def clamp(value, lo, hi):\n    return value\n")))
        self.assertEqual(result["structure"], "fail")
        self.assertTrue(any("bundle.sign" in p for p in result["problems"]))

    def test_syntax_error_fails(self):
        task = grade.load_task("B02")
        result = grade.static_grade(task, draft(answer("def lookup(cache, key, default)\n    return 1\n")))
        self.assertIn("cache.py does not parse", result["problems"])

    def test_two_blocks_for_a_single_file_task_fail(self):
        task = grade.load_task("F01")
        code = reference("F01")["solution.py"]
        self.assertEqual(grade.static_grade(task, draft(answer(code, code)))["structure"], "fail")

    def test_bare_code_without_fences_is_accepted(self):
        task = grade.load_task("F01")
        self.assertEqual(grade.static_grade(task, draft(reference("F01")["solution.py"]))["structure"], "pass")

    def test_multi_file_needs_file_markers(self):
        task = grade.load_task("E03")
        files = reference("E03")
        marked = answer(*(f"# file: {name}\n{code}" for name, code in files.items()))
        self.assertEqual(grade.static_grade(task, draft(marked))["structure"], "pass")
        unmarked = answer(*files.values())
        self.assertEqual(grade.static_grade(task, draft(unmarked))["structure"], "fail")
        one_missing = answer(f"# file: invoice.py\n{files['invoice.py']}")
        self.assertIn("missing file summary.py", grade.static_grade(task, draft(one_missing))["problems"])

    def test_unknown_finish_reason_is_reported_as_unknown(self):
        task = grade.load_task("F01")
        result = grade.static_grade(task, draft(answer(reference("F01")["solution.py"]), finish=None, truncated=None))
        self.assertEqual(result["transport"], "unknown")

    def test_known_truncation_wins_over_missing_finish_reason(self):
        task = grade.load_task("F01")
        good = answer(reference("F01")["solution.py"])
        result = grade.static_grade(task, draft(good, finish=None, truncated=True))
        self.assertEqual((result["transport"], result["structure"]), ("incomplete", "fail"))
        self.assertEqual(grade.static_grade(task, draft(good, finish="stop", truncated=None))["transport"], "unknown")
        self.assertEqual(grade.static_grade(task, draft(good, finish="length", truncated=False))["transport"], "incomplete")

    def test_saved_helper_json_is_read(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "d.json"
            path.write_text(json.dumps({"content": "x", "finish_reason": "length", "truncated": True}), encoding="utf-8")
            self.assertEqual(grade.read_draft(path)["finish_reason"], "length")


class ExecutionGateTests(unittest.TestCase):
    def test_semantic_refuses_outside_a_sandbox(self):
        task = grade.load_task("F01")
        with self.assertRaises(SystemExit):
            grade.semantic_grade(task, draft(answer(reference("F01")["solution.py"])), in_sandbox=False)

    def test_manifest_gate_refuses_even_inside_a_declared_sandbox(self):
        task = grade.load_task("F01")
        self.assertIs(grade.manifest()["generated_code_execution_enabled"], False)
        with self.assertRaises(SystemExit) as caught:
            grade.semantic_grade(task, draft(answer(reference("F01")["solution.py"])), in_sandbox=True)
        self.assertIn("manifest", str(caught.exception))

    def test_sandbox_flag_alone_is_refused_when_manifest_allows(self):
        task = grade.load_task("F01")
        real = grade.manifest
        grade.manifest = lambda: dict(real(), generated_code_execution_enabled=True)
        try:
            with self.assertRaises(SystemExit) as caught:
                grade.semantic_grade(task, draft(answer(reference("F01")["solution.py"])), in_sandbox=False)
        finally:
            grade.manifest = real
        self.assertIn("sandbox", str(caught.exception))

    def test_cli_needs_both_flag_and_environment(self):
        self.assertNotEqual(os.environ.get(grade.SANDBOX_ENV), "1")


class JudgeTests(unittest.TestCase):
    """The value judge, exercised with code written here (never model output)."""

    def run_one(self, code, case):
        return grade.run_cases({"m.py": code}, [case])[0]

    def test_bool_is_not_int(self):
        code = "def f():\n    return True\n"
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "expect": 1})["ok"])
        self.assertTrue(self.run_one(code, {"call": "m.f", "args": [], "expect": True})["ok"])

    def test_int_is_not_float(self):
        code = "def f():\n    return 2\n"
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "expect": 2.0})["ok"])

    def test_input_mutation_is_caught(self):
        code = "def f(xs):\n    xs.append(1)\n    return 0\n"
        result = self.run_one(code, {"call": "m.f", "args": [[5]], "expect": 0})
        self.assertEqual((result["ok"], result["why"]), (False, "mutated input"))

    def test_expected_exception(self):
        code = "def f():\n    raise ValueError('x')\n"
        self.assertTrue(self.run_one(code, {"call": "m.f", "args": [], "raises": "ValueError"})["ok"])
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "raises": "KeyError"})["ok"])

    def test_missing_exception_fails(self):
        code = "def f():\n    return None\n"
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "raises": "ValueError"})["ok"])

    def test_dict_order_is_ignored_and_list_order_is_not(self):
        code = "def f():\n    return {'b': [1, 2], 'a': 0}\n"
        self.assertTrue(self.run_one(code, {"call": "m.f", "args": [], "expect": {"a": 0, "b": [1, 2]}})["ok"])
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "expect": {"a": 0, "b": [2, 1]}})["ok"])

    def test_candidate_never_receives_expected_values(self):
        code = ("import pathlib\n"
                "def f():\n"
                "    seen = ' '.join(p.read_text(encoding='utf-8') for p in pathlib.Path('.').iterdir() if p.is_file())\n"
                "    return ('SECRET' + '-EXPECTED') in seen\n")      # split so its own source does not match
        self.assertTrue(self.run_one(code, {"call": "m.f", "args": [], "expect": False, "note": "SECRET-EXPECTED"})["ok"])
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "expect": "SECRET-EXPECTED"})["ok"])

    def test_candidate_cannot_declare_its_own_pass(self):
        code = ("import atexit, json\n"
                "atexit.register(lambda: print(json.dumps([{'ok': True, 'why': 'value'}])))\n"
                "def f():\n    return 1\n")
        self.assertFalse(self.run_one(code, {"call": "m.f", "args": [], "expect": 2})["ok"])

    def test_tuple_is_not_a_list(self):
        code = "def f():\n    return (1, 2)\n"
        result = self.run_one(code, {"call": "m.f", "args": [], "expect": [1, 2]})
        self.assertEqual((result["ok"], result["why"]), (False, "returned tuple"))

    def test_mutation_is_caught_even_when_an_exception_is_expected(self):
        code = "def f(xs):\n    xs.clear()\n    raise ValueError('x')\n"
        result = self.run_one(code, {"call": "m.f", "args": [[1]], "raises": "ValueError"})
        self.assertEqual((result["ok"], result["why"]), (False, "mutated input"))

    def test_new_object_requirement(self):
        code = "def f(d):\n    return d\n"
        case = {"call": "m.f", "args": [{"a": 1}], "expect": {"a": 1}, "new_object": True}
        self.assertEqual(self.run_one(code, case)["why"], "returned the input object")
        self.assertTrue(self.run_one("def f(d):\n    return dict(d)\n", case)["ok"])
        self.assertTrue(self.run_one(code, {"call": "m.f", "args": [{"a": 1}], "expect": {"a": 1}})["ok"])

    def test_endless_loop_times_out_as_failure(self):
        old = grade.RUN_TIMEOUT_S
        grade.RUN_TIMEOUT_S = 2
        try:
            result = self.run_one("def f():\n    while True:\n        pass\n", {"call": "m.f", "args": [], "expect": 0})
        finally:
            grade.RUN_TIMEOUT_S = old
        self.assertEqual(result, {"ok": False, "why": "timeout"})

    def test_starters_fail_and_references_pass_semantically(self):
        for task_id in ("B01", "B02", "B03", "E01", "E03", "A03"):
            task = grade.load_task(task_id)
            folder = grade.FIX / task_id / "starter"
            starter = {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.iterdir())}
            outcome = grade.summarise(grade.run_cases(starter, task["hidden"]))
            self.assertLess(outcome["passed"], outcome["total"], task_id)
            good = grade.summarise(grade.run_cases(reference(task_id), task["hidden"]))
            self.assertEqual(good["passed"], good["total"], task_id)


if __name__ == "__main__":
    unittest.main()
