"""Synthetic core tests only. No framework, filesystem, network or model."""
import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError

from teach_status_core import AttemptNotice, TeachingDecision, encode_status


class DecisionTests(unittest.TestCase):
    def test_empty_and_fully_applied_need_no_omission_notice(self):
        for decision in (
            TeachingDecision("available", relevant=0),
            TeachingDecision("available", relevant=2, applied=2),
            TeachingDecision("available", relevant=2, applied=2, byte_only=2),
        ):
            self.assertIsNone(encode_status(decision))

    def test_partial_count_failure_does_not_claim_all_notes_omitted(self):
        decision = TeachingDecision(
            "available", relevant=3, applied=2, omitted_uncounted=1
        )
        self.assertEqual(decision.notice_kind(), "uncounted")
        text = json.loads(encode_status(decision))["event"]["data"]["description"]
        self.assertTrue(text.startswith("Some saved notes"))

    def test_cap_and_room_omissions(self):
        for key in ("omitted_cap", "omitted_no_room"):
            with self.subTest(key=key):
                decision = TeachingDecision("available", relevant=1, **{key: 1})
                self.assertEqual(decision.notice_kind(), "omitted")

    def test_invalid_entries_separate_from_relevant_set(self):
        decision = TeachingDecision("available", relevant=1, applied=1, invalid=2)
        self.assertEqual(decision.notice_kind(), "invalid")

    def test_unknown_is_not_zero_relevant(self):
        for decision in (
            TeachingDecision("unknown"),
            TeachingDecision("available"),
        ):
            self.assertEqual(decision.notice_kind(), "unknown")
            self.assertIsNotNone(encode_status(decision))

    def test_unavailable_store(self):
        decision = TeachingDecision("unavailable")
        self.assertEqual(decision.notice_kind(), "unavailable")

    def test_decision_is_immutable(self):
        decision = TeachingDecision("available", relevant=0)
        with self.assertRaises(FrozenInstanceError):
            decision.applied = 1

    def test_invalid_counts_are_controlled(self):
        for value in (True, False, -1, 1025, 1.0, "1", None, [], {}):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "^Invalid teaching count"):
                    TeachingDecision("available", applied=value)

    def test_invalid_relevant_is_controlled(self):
        for value in (True, -1, 1025, 1.0, "0"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValueError):
                    TeachingDecision("available", relevant=value)

    def test_accounting_and_byte_subset(self):
        with self.assertRaises(ValueError):
            TeachingDecision("available", relevant=1, applied=0)
        with self.assertRaises(ValueError):
            TeachingDecision("available", relevant=1, applied=1, byte_only=2)
        with self.assertRaises(ValueError):
            TeachingDecision("available", applied=1024, omitted_cap=1)

    def test_unknown_store_rejects_fabricated_known_counts(self):
        for store in ("unknown", "unavailable"):
            with self.subTest(store=store):
                with self.assertRaises(ValueError):
                    TeachingDecision(store, relevant=0)
                with self.assertRaises(ValueError):
                    TeachingDecision(store, applied=1)

    def test_malformed_strings_not_stringified_or_leaked(self):
        class Canary:
            def __str__(self):
                raise AssertionError("must not stringify")
        for value in ("PRIVATE_CANARY", None, Canary()):
            with self.subTest(type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, "^Invalid teaching store state$"):
                    TeachingDecision(value)


class EncodingTests(unittest.TestCase):
    def test_allowlisted_completed_visible_event_and_no_prefix(self):
        text = encode_status(TeachingDecision("available", relevant=1, omitted_cap=1))
        self.assertFalse(text.startswith("data:"))
        event = json.loads(text)
        self.assertEqual(set(event), {"event"})
        self.assertEqual(set(event["event"]), {"type", "data"})
        self.assertEqual(event["event"]["type"], "status")
        data = event["event"]["data"]
        self.assertEqual(set(data), {"description", "done", "hidden"})
        self.assertIs(data["done"], True)
        self.assertIs(data["hidden"], False)
        self.assertLess(len(data["description"]), 160)
        self.assertNotIn("choices", event)

    def test_arabic_fixed_text_valid_utf8(self):
        text = encode_status(
            TeachingDecision("available", relevant=1, omitted_no_room=1), "ar"
        )
        self.assertIn("ملاحظات", text)
        self.assertEqual(text.encode("utf-8").decode("utf-8"), text)

    def test_invalid_locale_does_not_leak(self):
        for locale in ("PRIVATE_CANARY", None, True, []):
            with self.subTest(type=type(locale).__name__):
                with self.assertRaisesRegex(ValueError, "^Unsupported teaching notice locale$"):
                    encode_status(TeachingDecision("available", relevant=0), locale)

    def test_arbitrary_decision_rejected(self):
        with self.assertRaisesRegex(ValueError, "^Invalid teaching decision$"):
            encode_status({"text": "PRIVATE_CANARY"})

    def test_omission_priority_is_truthful(self):
        decision = TeachingDecision(
            "available", relevant=3, omitted_cap=1,
            omitted_no_room=1, omitted_uncounted=1, invalid=1
        )
        self.assertEqual(decision.notice_kind(), "uncounted")


class AttemptTests(unittest.TestCase):
    def test_only_one_event_per_attempt(self):
        attempt = AttemptNotice(TeachingDecision("available", relevant=1, omitted_cap=1))
        self.assertIsNotNone(attempt.take())
        self.assertIsNone(attempt.take())

    def test_retry_is_explicit_new_instance(self):
        decision = TeachingDecision("available", relevant=1, omitted_cap=1)
        first, retry = AttemptNotice(decision), AttemptNotice(decision)
        self.assertEqual(first.take(), retry.take())
        self.assertIsNone(first.take())
        self.assertIsNone(retry.take())

    def test_independent_attempts_cannot_borrow_status(self):
        first = AttemptNotice(TeachingDecision("available", relevant=1, omitted_cap=1))
        second = AttemptNotice(TeachingDecision("available", relevant=0))
        self.assertIsNone(second.take())
        self.assertIsNotNone(first.take())

    def test_same_attempt_thread_contention_emits_at_most_once(self):
        attempt = AttemptNotice(TeachingDecision("available", relevant=1, omitted_cap=1))
        with ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: attempt.take(), range(32)))
        self.assertEqual(sum(value is not None for value in outputs), 1)


if __name__ == "__main__":
    unittest.main()
