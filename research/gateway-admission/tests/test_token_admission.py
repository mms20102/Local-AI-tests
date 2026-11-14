"""Offline tests for real-token admission. No services, HTTP, credentials or model execution."""
import copy
from pathlib import Path
import tempfile
import unittest

from chat_contract import ContractError, TOKEN_MARGIN, read_json, validate_chat, validate_settings
import token_count

ROOT = Path(__file__).resolve().parents[1]
REAL = token_count.load_counter()
# The limits as configured on the laptop. Used when this file is run from a published copy that
# has no settings.json beside it; the values are the same.
PUBLISHED_LIMITS = {"model_alias": "local-qwen36-chat", "upstream_model": "qwen3.6-colibri", "context_tokens": 2048,
                    "default_output_tokens": 256, "max_output_tokens": 256, "context_reserve_units": 256,
                    "per_message_overhead_units": 32, "max_messages": 32, "max_request_bytes": 32768,
                    "max_concurrent_requests": 1, "request_timeout_seconds": 120, "temperature": 0}


def limits():
    path = ROOT / "settings.json"
    return validate_settings(read_json(path) if path.is_file() else dict(PUBLISHED_LIMITS))


def words(n):
    """A fake counter: one token per whitespace-separated word of the rendered prompt."""
    return lambda messages: n if n is not None else len(token_count.render(messages).split())


class RenderTests(unittest.TestCase):
    def test_system_user_shape(self):
        text = token_count.render([{"role": "system", "content": " S "}, {"role": "user", "content": "U\n"}])
        self.assertEqual(text, "<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n"
                               "<|im_start|>assistant\n<think>\n\n</think>\n\n")

    def test_user_only_has_no_system_frame(self):
        text = token_count.render([{"role": "user", "content": "U"}])
        self.assertNotIn("system", text)
        self.assertTrue(text.endswith(token_count.GENERATION_PROMPT))

    def test_past_assistant_turn_keeps_empty_think_block(self):
        text = token_count.render([{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},
                                   {"role": "user", "content": "c"}])
        self.assertIn("<|im_start|>assistant\n<think>\n\n</think>\n\nb<|im_end|>\n", text)

    def test_render_does_not_modify_messages(self):
        messages = [{"role": "user", "content": "  x  "}]
        before = copy.deepcopy(messages)
        token_count.render(messages)
        self.assertEqual(messages, before)


class LoadCounterTests(unittest.TestCase):
    def test_missing_file_gives_none(self):
        self.assertIsNone(token_count.load_counter(Path(tempfile.gettempdir()) / "no-such-tokenizer.json"))

    def test_wrong_hash_gives_none(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tokenizer.json"
            path.write_text("{}", encoding="utf-8")
            self.assertIsNone(token_count.load_counter(path))

    def test_unreadable_content_gives_none(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tokenizer.json"
            path.write_text("not a tokenizer", encoding="utf-8")
            self.assertIsNone(token_count.load_counter(path, pinned=None))


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.s = limits()
        self.long = "word " * 1200                      # 6000 bytes: far over the byte rule
        self.body = {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": 256,
                     "messages": [{"role": "user", "content": self.long}]}

    def test_byte_rule_still_refuses_without_counter(self):
        with self.assertRaises(ContractError) as caught:
            validate_chat(self.body, self.s)
        self.assertEqual(caught.exception.status, 413)

    def test_long_request_admitted_by_tokens(self):
        limit = self.s["context_tokens"] - 256 - TOKEN_MARGIN
        self.assertEqual(validate_chat(self.body, self.s, words(limit)), self.s["context_tokens"])

    def test_one_token_over_is_refused(self):
        limit = self.s["context_tokens"] - 256 - TOKEN_MARGIN
        with self.assertRaises(ContractError) as caught:
            validate_chat(self.body, self.s, words(limit + 1))
        self.assertEqual(caught.exception.status, 413)
        self.assertIn("NOT silently truncated", str(caught.exception))

    def test_requested_output_is_fully_reserved(self):
        self.body["max_tokens"] = 100
        limit = self.s["context_tokens"] - 100 - TOKEN_MARGIN
        validate_chat(self.body, self.s, words(limit))
        self.body["max_tokens"] = 101
        with self.assertRaises(ContractError):
            validate_chat(self.body, self.s, words(limit))

    def test_small_request_is_decided_by_bytes_exactly_as_before(self):
        self.body["messages"][0]["content"] = "Explain why the sky looks blue."
        calls = []
        result = validate_chat(self.body, self.s, lambda m: calls.append(1) or 10**6)
        self.assertEqual(result, validate_chat(self.body, self.s))
        self.assertEqual(calls, [])                     # the counter is not even consulted

    def test_counter_failure_falls_back_to_byte_rule(self):
        def broken(messages):
            raise RuntimeError("tokenizer fault")
        for counter in (broken, lambda m: None, lambda m: 0, lambda m: -5, lambda m: True, lambda m: "12"):
            with self.assertRaises(ContractError) as caught:
                validate_chat(self.body, self.s, counter)
            self.assertEqual(caught.exception.status, 413)

    def test_other_rules_unchanged_with_counter(self):
        counter = words(10)
        for change in ({"tools": []}, {"model": "other"}, {"temperature": 0.5}, {"max_tokens": 257}):
            body = dict(self.body, **change)
            with self.assertRaises(ContractError):
                validate_chat(body, self.s, counter)
        body = dict(self.body, messages=self.body["messages"] + [{"role": "assistant", "content": "x"}])
        with self.assertRaises(ContractError):
            validate_chat(body, self.s, counter)
        body = dict(self.body, messages=[{"role": "user", "content": "x"}] * (self.s["max_messages"] + 1))
        with self.assertRaises(ContractError):
            validate_chat(body, self.s, counter)

    def test_messages_not_modified(self):
        before = copy.deepcopy(self.body)
        validate_chat(self.body, self.s, words(500))
        self.assertEqual(self.body, before)


@unittest.skipIf(REAL is None, "pinned tokenizer file or tokenizers package not available")
class RealTokenizerTests(unittest.TestCase):
    def setUp(self):
        self.s = limits()

    def test_tokens_never_exceed_byte_units(self):
        samples = ["hi", "Explain why the sky looks blue.", "x" * 900, "اكتب دالة بايثون تجمع عددين. " * 20,
                   "a b c d e f g " * 100, "🙂" * 200, "\n\n\t  spaced   out \n" * 50]
        for text in samples:
            messages = [{"role": "system", "content": "Answer clearly."}, {"role": "user", "content": text},
                        {"role": "assistant", "content": text[:50]}, {"role": "user", "content": text}]
            units = sum(len(m["content"].encode("utf-8")) + self.s["per_message_overhead_units"] for m in messages)
            self.assertLess(REAL(messages), units, text[:20])

    def test_frames_are_single_special_tokens(self):
        self.assertLess(REAL([{"role": "user", "content": "hi"}]), 16)

    def test_long_english_request_is_admitted_and_too_long_refused(self):
        body = {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": 256,
                "messages": [{"role": "user", "content": "The quick brown fox jumps over the lazy dog. " * 150}]}
        self.assertGreater(len(body["messages"][0]["content"]), 6000)
        needed = validate_chat(body, self.s, REAL)
        self.assertLessEqual(needed, self.s["context_tokens"])
        body["messages"][0]["content"] *= 2
        with self.assertRaises(ContractError):
            validate_chat(body, self.s, REAL)


if __name__ == "__main__":
    unittest.main()
