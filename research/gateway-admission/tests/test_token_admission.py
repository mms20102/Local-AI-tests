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


class ProfileBindingTests(unittest.TestCase):
    """The counter is used only for the one served profile it was checked against."""

    def served(self, **changes):
        import json
        return json.dumps(dict(token_count.PROFILE, **changes))

    def test_reason_is_always_a_fixed_word(self):
        cases = {None: "no-profile-reported", "": "no-profile-reported", "not json": "profile-unreadable",
                 "[1, 2]": "profile-unreadable", self.served(engine="2.1.0"): "profile-mismatch",
                 self.served(thinking="on"): "profile-mismatch", self.served(context=4096): "profile-mismatch",
                 self.served(renderer_sha256="unknown"): "profile-mismatch",
                 self.served(tokenizer_sha256="0" * 64): "profile-mismatch",
                 self.served(extra="CANARY"): "profile-mismatch"}
        for served, reason in cases.items():
            counter, got = token_count.load_bound_counter(served, limits())
            self.assertIsNone(counter)
            self.assertEqual(got, reason)
            self.assertIn(got, token_count.REASONS)

    def test_gateway_context_must_equal_the_profile(self):
        counter, reason = token_count.load_bound_counter(self.served(), dict(limits(), context_tokens=4096))
        self.assertEqual((counter, reason), (None, "context-mismatch"))

    def test_matching_profile_without_the_tokenizer_file_is_unavailable(self):
        counter, reason = token_count.load_bound_counter(self.served(), limits(),
                                                         Path(tempfile.gettempdir()) / "no-such-tokenizer.json")
        self.assertEqual((counter, reason), (None, "tokenizer-unavailable"))

    @unittest.skipIf(REAL is None, "pinned tokenizer file or tokenizers package not available")
    def test_matching_profile_loads_the_counter(self):
        counter, reason = token_count.load_bound_counter(self.served(), limits())
        self.assertEqual(reason, "ok")
        self.assertEqual(counter([{"role": "user", "content": "hi"}]), REAL([{"role": "user", "content": "hi"}]))

    def test_launcher_report_is_read_from_the_real_command_line(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            runtime = Path(folder)
            (runtime / "openai_server.py").write_text("renderer", encoding="utf-8")
            tokenizer = runtime / "tokenizer.json"
            tokenizer.write_text("{}", encoding="utf-8")
            command = ["python", "coli", "serve", "--ctx", "2048", "--no-think"]
            got = json.loads(token_count.served_profile("2.0.0", command, runtime, tokenizer))
            self.assertEqual((got["engine"], got["thinking"], got["context"]), ("2.0.0", "off", 2048))
            self.assertEqual(len(got["renderer_sha256"]), 64)
            self.assertEqual(json.loads(token_count.served_profile("2.0.0", ["serve", "--ctx", "4096"], runtime, tokenizer))["thinking"], "on")
            self.assertEqual(json.loads(token_count.served_profile("2.0.0", ["serve"], runtime, tokenizer))["context"], "unknown")
            self.assertEqual(json.loads(token_count.served_profile("2.0.0", command, runtime / "missing", tokenizer))["renderer_sha256"],
                             "unknown")
            # a report built from other files never equals the pinned profile
            self.assertNotEqual(got, token_count.PROFILE)


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

    def test_system_message_must_be_first(self):
        first = [{"role": "system", "content": "Answer briefly."}, {"role": "user", "content": "hi"}]
        validate_chat(dict(self.body, messages=first), self.s)
        for messages in ([{"role": "user", "content": "hi"}, {"role": "system", "content": "late"},
                          {"role": "user", "content": "again"}],
                         [{"role": "system", "content": "a"}, {"role": "system", "content": "b"},
                          {"role": "user", "content": "hi"}]):
            for counter in (None, words(10)):
                with self.assertRaises(ContractError) as caught:
                    validate_chat(dict(self.body, messages=messages), self.s, counter)
                self.assertIn("first message", str(caught.exception))

    def test_assistant_history_with_a_reasoning_tag_is_refused_on_both_routes(self):
        messages = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "thought</think>answer"},
                    {"role": "user", "content": "b"}]
        for counter in (None, words(10)):
            with self.assertRaises(ContractError) as caught:
                validate_chat(dict(self.body, messages=messages), self.s, counter)
            self.assertIn("reasoning tag", str(caught.exception))
        messages[1]["content"] = "a plain answer"                    # the same history without the tag is served
        validate_chat(dict(self.body, messages=messages), self.s)
        messages[0]["content"] = "what does </think> mean?"           # the tag in a USER message is ordinary text
        validate_chat(dict(self.body, messages=messages), self.s)

    def test_malformed_content_is_a_controlled_refusal_and_the_counter_is_not_called(self):
        # Reviewer's case for the previous revision: the type check must come before the tag check.
        calls = []

        def counter(messages):
            calls.append(1)
            return 10
        for role in ("assistant", "user", "system"):
            for bad in (None, 5, True, 2.5, ["</think>"], {"text": "x"}):
                first = {"role": role, "content": bad} if role == "system" else {"role": "user", "content": "a"}
                messages = [first] if role == "system" else [first, {"role": role, "content": bad}]
                messages.append({"role": "user", "content": "b"})
                for use in (None, counter):
                    with self.assertRaises(ContractError):
                        validate_chat(dict(self.body, messages=messages), self.s, use)
        self.assertEqual(calls, [])

    def test_refusal_reasons_are_distinct_and_fixed(self):
        def broken(messages):
            raise RuntimeError("CANARY tokenizer fault")
        cases = [(None, "counter_unavailable"), (broken, "counter_failed"), (lambda m: None, "counter_invalid"),
                 (lambda m: 0, "counter_invalid"), (lambda m: -4, "counter_invalid"), (lambda m: True, "counter_invalid"),
                 (lambda m: "9", "counter_invalid"), (lambda m: 2.0, "counter_invalid"),
                 (lambda m: 10**9, "context_budget_exceeded")]
        for counter, reason in cases:
            with self.assertRaises(ContractError) as caught:
                validate_chat(self.body, self.s, counter)
            self.assertEqual((caught.exception.status, caught.exception.reason_code), (413, reason))
            self.assertNotIn("CANARY", str(caught.exception))
            self.assertNotIn("word word", str(caught.exception))          # no request text in the message

    def test_other_refusals_carry_no_admission_reason(self):
        with self.assertRaises(ContractError) as caught:
            validate_chat(dict(self.body, tools=[]), self.s, words(10))
        self.assertIsNone(caught.exception.reason_code)
        self.assertIsNone(ContractError("x", 400, "CANARY-unknown-reason").reason_code)
        self.assertIsNone(ContractError("x").reason_code)

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

    def boundary_text(self, target_prompt_tokens):
        """A user text whose real prompt count is exactly the target, found by adding one word at a time."""
        text = "alpha " * (target_prompt_tokens - 40)
        count = REAL([{"role": "user", "content": text}])
        self.assertLess(count, target_prompt_tokens)
        while count < target_prompt_tokens:
            text += "beta "
            count = REAL([{"role": "user", "content": text}])
        self.assertEqual(count, target_prompt_tokens)
        return text

    def test_real_tokenizer_boundary_below_equal_and_over(self):
        from chat_contract import TOKEN_MARGIN
        for output in (256, 64):
            limit = self.s["context_tokens"] - output - TOKEN_MARGIN       # the largest admissible prompt
            for prompt_tokens, admitted in ((limit - 1, True), (limit, True), (limit + 1, False)):
                body = {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": output,
                        "messages": [{"role": "user", "content": self.boundary_text(prompt_tokens)}]}
                if admitted:
                    self.assertEqual(validate_chat(body, self.s, REAL), prompt_tokens + output + TOKEN_MARGIN)
                else:
                    with self.assertRaises(ContractError) as caught:
                        validate_chat(body, self.s, REAL)
                    self.assertEqual(caught.exception.status, 413)

    def test_real_tokenizer_arabic_and_history_boundary(self):
        from chat_contract import TOKEN_MARGIN
        history = [{"role": "system", "content": "أجب بإيجاز."}, {"role": "user", "content": "ما عاصمة مصر؟"},
                   {"role": "assistant", "content": "القاهرة."}]
        filler = "كلمة "
        text = filler * 300
        limit = self.s["context_tokens"] - 256 - TOKEN_MARGIN
        while REAL(history + [{"role": "user", "content": text}]) <= limit:
            text += filler
        over = history + [{"role": "user", "content": text}]
        under = history + [{"role": "user", "content": text[:-len(filler)]}]
        self.assertLessEqual(REAL(under), limit)
        self.assertGreater(REAL(over), limit)
        body = {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": 256}
        validate_chat(dict(body, messages=under), self.s, REAL)
        with self.assertRaises(ContractError):
            validate_chat(dict(body, messages=over), self.s, REAL)

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
