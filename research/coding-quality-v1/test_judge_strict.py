"""Regression tests for the judge and the report parsing. PURE: nothing here runs a candidate, a child
process or a sandbox. Records are written by hand, the way a hostile or broken reporter could write them.

The first group answers the independent review of 377fae14, which showed that a `raised` record with no
`error`, judged against a case with no `raises`, compared None == None and passed.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "sandbox"))

import grade  # noqa: E402
import sandbox_host  # noqa: E402

VALUE_CASE = {"call": "m.f", "args": [1], "expect": 999}
NULL_CASE = {"call": "m.f", "args": [1], "expect": None}
RAISE_CASE = {"call": "m.f", "args": [1], "raises": "ValueError"}
RETURNED = {"status": "returned", "args_after": [1], "value": 999, "same_object_as_input": False}
RAISED = {"status": "raised", "args_after": [1], "value": None, "same_object_as_input": False, "error": "ValueError"}


def without(record, *keys):
    return {k: v for k, v in record.items() if k not in keys}


class JudgeShapeTests(unittest.TestCase):
    def test_well_formed_records_still_pass(self):
        self.assertTrue(grade.judge(VALUE_CASE, RETURNED)["ok"])
        self.assertTrue(grade.judge(RAISE_CASE, RAISED)["ok"])
        self.assertTrue(grade.judge(NULL_CASE, {**RETURNED, "value": None})["ok"])

    def test_reviewer_counterexample_raised_without_error_against_a_value_case(self):
        result = grade.judge(VALUE_CASE, {"status": "raised", "args_after": [1]})
        self.assertEqual(result, {"ok": False, "why": "bad result"})

    def test_raised_never_passes_a_value_case(self):
        self.assertFalse(grade.judge(VALUE_CASE, RAISED)["ok"])
        self.assertFalse(grade.judge(NULL_CASE, RAISED)["ok"])

    def test_raised_needs_an_explicit_error_name(self):
        for record in (without(RAISED, "error"), {**RAISED, "error": None}, {**RAISED, "error": ""}, {**RAISED, "error": 5},
                       {**RAISED, "error": ["ValueError"]}):
            self.assertEqual(grade.judge(RAISE_CASE, record)["why"], "bad result", record)

    def test_wrong_exception_name_fails(self):
        self.assertFalse(grade.judge(RAISE_CASE, {**RAISED, "error": "KeyError"})["ok"])

    def test_missing_value_does_not_pass_a_null_expectation(self):
        result = grade.judge(NULL_CASE, without(RETURNED, "value"))
        self.assertEqual(result, {"ok": False, "why": "bad result"})

    def test_every_missing_field_is_refused(self):
        for key in RETURNED:
            self.assertEqual(grade.judge(VALUE_CASE, without(RETURNED, key))["why"], "bad result", key)
        for key in RAISED:
            self.assertEqual(grade.judge(RAISE_CASE, without(RAISED, key))["why"], "bad result", key)

    def test_extra_fields_are_refused(self):
        self.assertEqual(grade.judge(VALUE_CASE, {**RETURNED, "ok": True})["why"], "bad result")
        self.assertEqual(grade.judge(VALUE_CASE, {**RETURNED, "error": "x"})["why"], "bad result")

    def test_wrong_types_are_refused(self):
        bad = [None, [], "returned", 7, [RETURNED], {**RETURNED, "status": ["returned"]}, {**RETURNED, "status": "passed"},
               {**RETURNED, "status": None}, {**RETURNED, "same_object_as_input": 0}, {**RETURNED, "same_object_as_input": None},
               {**RETURNED, "same_object_as_input": "False"}, {"status": "import_error"}, {"status": "import_error", "error": 1},
               {**RAISED, "value": 999}, {**RAISED, "same_object_as_input": True},
               {**RAISED, "status": "not_json", "value": 999}]
        for record in bad:
            for case in (VALUE_CASE, NULL_CASE, RAISE_CASE):
                result = grade.judge(case, record)
                self.assertEqual((result["ok"], result["why"]), (False, "bad result"), record)

    def test_identity_flag_must_be_a_real_false_when_a_new_object_is_required(self):
        case = {"call": "m.f", "args": [{"a": 1}], "expect": {"a": 1}, "new_object": True}
        good = {"status": "returned", "args_after": [{"a": 1}], "value": {"a": 1}, "same_object_as_input": False}
        self.assertTrue(grade.judge(case, good)["ok"])
        self.assertEqual(grade.judge(case, {**good, "same_object_as_input": True})["why"], "returned the input object")
        self.assertEqual(grade.judge(case, without(good, "same_object_as_input"))["why"], "bad result")

    def test_args_after_must_match_exactly(self):
        for after in ([1, 2], [], [1.0], [True], "not_json", None):
            self.assertEqual(grade.judge(VALUE_CASE, {**RETURNED, "args_after": after})["why"], "mutated input", after)

    def test_malformed_cases_never_pass(self):
        for case in ({"call": "m.f", "args": [1]}, {"call": "m.f", "args": [1], "expect": 999, "raises": "ValueError"},
                     {"call": "m.f", "args": [1], "raises": None}, {"call": "m.f", "args": [1], "raises": ""},
                     {"call": "m.f", "expect": 999}, None):
            for record in (RETURNED, RAISED, {"status": "raised", "args_after": [1]}):
                self.assertEqual(grade.judge(case, record), {"ok": False, "why": "bad case"})

    def test_every_case_in_the_suite_is_well_formed(self):
        for task_id in sorted(grade.manifest()["tasks"]):
            task = grade.load_task(task_id)
            for case in task["public"] + task["hidden"]:
                self.assertTrue(grade.case_shape_ok(case), (task_id, case))


class StrictJsonTests(unittest.TestCase):
    def test_repeated_keys_are_refused_at_any_depth(self):
        for text in ('{"a": 1, "a": 2}', '[{"status": "raised", "status": "returned"}]', '{"x": {"k": 1, "k": 1}}'):
            with self.assertRaises(ValueError):
                grade.loads_strict(text)

    def test_non_json_constants_are_refused(self):
        for text in ("NaN", "[Infinity]", '{"v": -Infinity}'):
            with self.assertRaises(ValueError):
                grade.loads_strict(text)

    def test_ordinary_json_is_read_unchanged(self):
        text = json.dumps([RETURNED, RAISED, {"k": [1, 2.5, None, True, "نص"]}])
        self.assertEqual(grade.loads_strict(text), json.loads(text))


GOOD_ENVIRONMENT = {"network": {name: "failed: TimeoutError" for name in sandbox_host.NETWORK_PROBES},
                    "input_folder_writable": False, "host_user_folder_visible": False, "tsclient_visible": False}


def guest_item(**changes):
    item = {"id": "X", "status": "finished", "confined": True, "in_job": True, "integrity": 4096, "exit_code": 0, "stdout_bytes": 90, "stdout_capped": False,
            "seconds": 0.1, "records": [dict(RETURNED)]}
    item.update(changes)
    return item


class ReportReadingTests(unittest.TestCase):
    def read(self, text):
        with tempfile.TemporaryDirectory() as temp:
            (Path(temp) / "out").mkdir()
            (Path(temp) / "out" / "results.json").write_text(text, encoding="utf-8")
            return sandbox_host.read_report(Path(temp), ["X"])

    def report(self, **changes):
        base = {"complete": True, "entries": [guest_item()], "environment": GOOD_ENVIRONMENT}
        base.update(changes)
        return json.dumps(base)

    def test_good_report_is_accepted(self):
        report, problems = self.read(self.report())
        self.assertIsNotNone(report)
        self.assertEqual(problems, [])

    def test_empty_or_partial_network_section_is_refused(self):
        partial = dict(list(GOOD_ENVIRONMENT["network"].items())[:2])
        for network in ({}, None, partial, {**GOOD_ENVIRONMENT["network"], "public_ip": "CONNECTED"},
                        {**GOOD_ENVIRONMENT["network"], "public_ip": "ok"}, {**GOOD_ENVIRONMENT["network"], "extra": "failed: X"},
                        {**GOOD_ENVIRONMENT["network"], "public_ip": None}):
            _, problems = self.read(self.report(environment={**GOOD_ENVIRONMENT, "network": network}))
            self.assertTrue(any("network" in p for p in problems), network)

    def test_missing_isolation_facts_are_refused(self):
        for key in ("input_folder_writable", "host_user_folder_visible", "tsclient_visible"):
            _, problems = self.read(self.report(environment=without(GOOD_ENVIRONMENT, key)))
            self.assertTrue(problems, key)
        _, problems = self.read(self.report(environment=None))
        self.assertEqual(len(problems), 3)

    def test_repeated_key_in_the_report_is_refused(self):
        text = self.report()[:-1] + ', "complete": true}'
        self.assertEqual(self.read(text), (None, ["report is not JSON"]))

    def test_incomplete_wrong_shape_and_wrong_entries_are_refused(self):
        self.assertIsNone(self.read(self.report(complete=False))[0])
        self.assertIsNone(self.read(self.report(complete="true"))[0])
        self.assertIsNone(self.read(self.report(entries=[]))[0])
        self.assertIsNone(self.read(self.report(entries=[guest_item(id="Y")]))[0])
        self.assertIsNone(self.read(self.report(entries=[guest_item(), guest_item()]))[0])
        self.assertIsNone(self.read("[]")[0])
        self.assertIsNone(self.read("not json")[0])


class EntryJudgingTests(unittest.TestCase):
    ENTRIES = {"X": {"cases": [VALUE_CASE]}}

    def judged(self, plain_session=True, **changes):
        return sandbox_host.judge_entries({"entries": [guest_item(**changes)]}, self.ENTRIES, plain_session)["X"]

    def test_clean_entry_passes_and_is_trusted_only_in_a_plain_session(self):
        got = self.judged()
        self.assertEqual((got["passed"], got["total"], got["trusted_observation"]), (1, 1, True))
        got = self.judged(plain_session=False)
        self.assertEqual((got["passed"], got["trusted_observation"]), (1, False))

    def test_valid_looking_records_do_not_pass_when_the_run_was_not_clean(self):
        for changes in ({"exit_code": 1}, {"exit_code": None}, {"exit_code": False}, {"exit_code": 0.0}, {"exit_code": "0"}, {"exit_code": -1073741819}, {"stdout_capped": True},
                        {"stdout_capped": None}, {"confined": False}, {"confined": None}, {"in_job": False}, {"in_job": None}, {"in_job": 1},
                        {"integrity": 8192}, {"integrity": 12288}, {"integrity": None}, {"integrity": 4096.0},
                        {"integrity": "4096"}, {"status": "timeout"},
                        {"status": "output_flood"}, {"status": None}, {"records": [dict(RETURNED), dict(RETURNED)]},
                        {"records": []}, {"records": None}, {"records": {"0": RETURNED}}):
            got = self.judged(**changes)
            self.assertEqual((got["passed"], got["trusted_observation"]), (0, False), changes)

    def test_forged_and_malformed_records_do_not_pass(self):
        for record in ({"status": "raised", "args_after": [1]}, {"ok": True, "why": "value"}, without(RETURNED, "value"),
                       {**RETURNED, "value": 998}, {**RETURNED, "ok": True}, None, "returned"):
            self.assertEqual(self.judged(records=[record])["passed"], 0, record)


if __name__ == "__main__":
    unittest.main()
