"""Offline tests for the teach store and its (disabled) gateway hook. No model, no network."""
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import teach_hook
import teach_store as ts
from chat_contract import read_json, validate_chat, validate_settings

LIMITS = validate_settings(read_json(Path(__file__).resolve().parents[1] / "settings.json"))


def body(messages, max_tokens=128):
    return {"model": LIMITS["model_alias"], "temperature": 0, "max_tokens": max_tokens, "messages": messages}


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name) / "teach"
        self.store = ts.Store(self.folder)

    def tearDown(self):
        self.temp.cleanup()


class StoreTests(Base):
    def test_add_list_and_persist(self):
        entry = self.store.add("  Answer   briefly. ", "rule")
        self.assertEqual((entry["id"], entry["text"], entry["when"]), ("t001", "Answer briefly.", []))
        again = ts.Store(self.folder)
        self.assertEqual([e["text"] for e in again.entries()], ["Answer briefly."])

    def test_arabic_text_and_keywords_round_trip(self):
        entry = self.store.add("أجب بالعربية الفصحى دائما.", "rule", "عَرَبِيّ, لغة")
        self.assertEqual(entry["when"], ["عربي", "لغة"])
        self.assertEqual(ts.Store(self.folder).entries()[0]["text"], "أجب بالعربية الفصحى دائما.")

    def test_rejects_multiline_empty_long_and_duplicates(self):
        for bad in ("", "   ", "a\nb", "x" * 301, "tab\there\x07"):
            with self.assertRaises(ts.TeachError, msg=repr(bad)):
                self.store.add(bad)
        self.store.add("Use tabs.")
        with self.assertRaises(ts.TeachError):
            self.store.add("use TABS.")

    def test_rejects_key_shaped_text(self):
        for bad in ("my key is sk-" + "a1B2" * 8, "token " + "9f" * 24, "-----BEGIN RSA PRIVATE KEY-----"):
            with self.assertRaises(ts.TeachError):
                self.store.add(bad)
        self.assertEqual(self.store.entries(), [])

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ts.TeachError):
            self.store.add("x", "secret")

    def test_disable_enable_delete(self):
        entry = self.store.add("One.")
        self.store.set_status(entry["id"], "disabled")
        self.assertEqual(self.store.entries(), [])
        self.assertEqual(len(self.store.entries(include_inactive=True)), 1)
        self.store.set_status(entry["id"], "active")
        self.assertEqual(len(self.store.entries()), 1)
        self.store.set_status(entry["id"], "deleted")
        self.assertEqual(self.store.entries(include_inactive=True), [])
        with self.assertRaises(ts.TeachError):
            self.store.get(entry["id"])
        self.assertEqual(self.store.add("Two.")["id"], "t002")        # ids are never reused

    def test_every_change_is_audited_and_previous_version_kept(self):
        entry = self.store.add("One.")
        self.store.set_status(entry["id"], "disabled")
        lines = [json.loads(l) for l in (self.folder / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([l["action"] for l in lines], ["add", "disabled"])
        backup = json.loads((self.folder / "store.json.bak").read_text(encoding="utf-8"))
        self.assertEqual(backup["entries"][0]["status"], "active")

    def test_unknown_store_format_is_not_overwritten(self):
        self.folder.mkdir(parents=True)
        (self.folder / "store.json").write_text('{"version": 99}', encoding="utf-8")
        with self.assertRaises(ts.TeachError):
            ts.Store(self.folder)
        self.assertEqual((self.folder / "store.json").read_text(encoding="utf-8"), '{"version": 99}')

    def test_store_limit(self):
        old = ts.MAX_ENTRIES
        ts.MAX_ENTRIES = 2
        try:
            self.store.add("a")
            self.store.add("b")
            with self.assertRaises(ts.TeachError):
                self.store.add("c")
        finally:
            ts.MAX_ENTRIES = old


class SelectionTests(Base):
    def test_always_entries_come_first_then_keyword_matches(self):
        self.store.add("Be brief.")
        self.store.add("Project uses Python 3.12.", "fact", "python")
        self.store.add("Database is SQLite.", "fact", "database, sql")
        chosen = ts.select(self.store.entries(), "Which PYTHON version?", 1000)
        self.assertEqual([e["id"] for e in chosen], ["t001", "t002"])
        self.assertEqual(ts.select(self.store.entries(), "hello", 1000)[0]["id"], "t001")
        self.assertEqual(len(ts.select(self.store.entries(), "hello", 1000)), 1)

    def test_multiword_keyword_needs_all_words(self):
        self.store.add("Use pytest.", "rule", "unit test")
        self.assertEqual(ts.select(self.store.entries(), "write a unit for this", 1000), [])
        self.assertEqual(len(ts.select(self.store.entries(), "write a test for this unit", 1000)), 1)

    def test_arabic_matching_ignores_diacritics(self):
        self.store.add("استخدم التقويم الهجري.", "rule", "تاريخ")
        self.assertEqual(len(ts.select(self.store.entries(), "ما هو التَّارِيخ اليوم؟ تَارِيخ", 1000)), 1)

    def test_budget_is_respected_and_entries_are_never_cut(self):
        for index in range(10):
            self.store.add(f"Rule number {index} " + "x" * 40)
        chosen = ts.select(self.store.entries(), "q", 200)
        block = ts.block_for(chosen)
        self.assertLessEqual(len(block.encode("utf-8")), 200)
        self.assertTrue(0 < len(chosen) < 10)
        for entry in chosen:
            self.assertIn(entry["text"], block)
        self.assertEqual(ts.select(self.store.entries(), "q", 10), [])

    def test_selection_is_deterministic(self):
        for word in ("b", "a", "c"):
            self.store.add(f"About {word}.", "fact", "topic")
        first = [e["id"] for e in ts.select(self.store.entries(), "topic", 1000)]
        self.assertEqual(first, [e["id"] for e in ts.select(ts.Store(self.folder).entries(), "topic", 1000)])


class InjectionTests(Base):
    def test_block_is_added_to_an_existing_system_message(self):
        self.store.add("Be brief.")
        messages = [{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "hi"}]
        result, used = ts.apply_to_messages(messages, self.store.entries(), LIMITS, 128)
        self.assertEqual(used, ["t001"])
        self.assertEqual(len(result), 2)
        self.assertTrue(result[0]["content"].startswith("You are helpful.\n\n" + ts.HEADER))
        self.assertEqual(messages[0]["content"], "You are helpful.")            # input untouched
        validate_chat(body(result), LIMITS)

    def test_new_system_message_when_there_is_none(self):
        self.store.add("Be brief.")
        result, used = ts.apply_to_messages([{"role": "user", "content": "hi"}], self.store.entries(), LIMITS, 128)
        self.assertEqual([m["role"] for m in result], ["system", "user"])
        validate_chat(body(result), LIMITS)

    def test_a_full_request_is_left_alone_and_still_valid(self):
        self.store.add("Be brief.")
        room = LIMITS["context_tokens"] - LIMITS["context_reserve_units"] - 128 - LIMITS["per_message_overhead_units"]
        messages = [{"role": "user", "content": "x" * room}]
        validate_chat(body(messages), LIMITS)
        result, used = ts.apply_to_messages(messages, self.store.entries(), LIMITS, 128)
        self.assertEqual((result, used), (messages, []))

    def test_partly_full_request_gets_only_what_fits(self):
        for index in range(6):
            self.store.add(f"Rule {index} " + "y" * 30)
        room = LIMITS["context_tokens"] - LIMITS["context_reserve_units"] - 128 - 2 * LIMITS["per_message_overhead_units"]
        messages = [{"role": "user", "content": "x" * (room - 130)}]
        result, used = ts.apply_to_messages(messages, self.store.entries(), LIMITS, 128)
        self.assertTrue(0 < len(used) < 6)
        validate_chat(body(result), LIMITS)

    def test_message_limit_is_respected(self):
        self.store.add("Be brief.")
        messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": "a"} for i in range(LIMITS["max_messages"] - 1)]
        messages.append({"role": "user", "content": "a"})
        self.assertEqual(len(messages), LIMITS["max_messages"])
        result, used = ts.apply_to_messages(messages, self.store.entries(), LIMITS, 16)
        self.assertEqual(used, [])
        self.assertEqual(len(result), LIMITS["max_messages"])

    def test_no_entries_or_wrong_last_role_changes_nothing(self):
        messages = [{"role": "user", "content": "hi"}]
        self.assertEqual(ts.apply_to_messages(messages, [], LIMITS, 128), (messages, []))
        self.store.add("Be brief.")
        ended = messages + [{"role": "assistant", "content": "yo"}]
        self.assertEqual(ts.apply_to_messages(ended, self.store.entries(), LIMITS, 128), (ended, []))


class HookTests(Base):
    def test_inject_changes_only_messages(self):
        self.store.add("Be brief.")
        data = body([{"role": "user", "content": "hi"}])
        changed, used = teach_hook.inject(data, LIMITS, self.folder)
        self.assertEqual(used, ["t001"])
        self.assertEqual({k: v for k, v in changed.items() if k != "messages"},
                         {k: v for k, v in data.items() if k != "messages"})
        self.assertEqual(len(data["messages"]), 1)
        validate_chat(changed, LIMITS)

    def test_inject_fails_open(self):
        data = body([{"role": "user", "content": "hi"}])
        self.assertEqual(teach_hook.inject(data, LIMITS, self.folder), (data, []))              # empty store
        self.folder.mkdir(parents=True)
        (self.folder / "store.json").write_text("not json", encoding="utf-8")
        self.assertEqual(teach_hook.inject(data, LIMITS, self.folder), (data, []))              # broken store
        odd = {"messages": [{"role": "user", "content": ["image"]}]}
        self.assertEqual(teach_hook.inject(odd, LIMITS, self.folder), (odd, []))                # not plain text
        self.assertEqual(teach_hook.inject({}, LIMITS, self.folder), ({}, []))

    def test_hook_is_not_enabled_in_the_gateway_config(self):
        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("teach_hook", (root / "litellm.base.json").read_text(encoding="utf-8"))


class CliTests(Base):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = ts.main(["--dir", str(self.folder), *args])
        return code, out.getvalue(), err.getvalue()

    def test_add_list_preview_disable(self):
        self.assertEqual(self.run_cli("add", "Be brief.")[0], 0)
        self.assertEqual(self.run_cli("add", "Uses SQLite.", "--kind", "fact", "--when", "database")[0], 0)
        code, out, _ = self.run_cli("list")
        self.assertIn("t001", out)
        self.assertIn("when: database", out)
        code, out, _ = self.run_cli("preview", "which database?")
        self.assertIn("- Fact: Uses SQLite.", out)
        self.assertIn("2 of 2 active entries", out)
        self.assertEqual(self.run_cli("disable", "t002")[0], 0)
        self.assertNotIn("SQLite", self.run_cli("preview", "which database?")[1])
        self.assertIn("[disabled]", self.run_cli("list", "--all")[1])

    def test_errors_are_reported_without_a_traceback(self):
        code, out, err = self.run_cli("delete", "t999")
        self.assertEqual(code, 1)
        self.assertIn("Not done: No entry t999.", err)
        code, _, err = self.run_cli("add", "sk-" + "Zz9" * 8)
        self.assertEqual(code, 1)
        self.assertIn("key or password", err)


if __name__ == "__main__":
    unittest.main()
