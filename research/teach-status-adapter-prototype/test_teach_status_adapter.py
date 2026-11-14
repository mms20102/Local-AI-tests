"""Offline tests for the teach status adapter prototype. Handwritten fake streams only.
No service, no model, no store, no network. LiteLLM-dependent tests are skipped when the
library is not installed in the Python that runs them."""
import asyncio
import copy
import json
import unittest

import teach_status_adapter as adapter
from teach_status_core import TeachingDecision

NONE = {"note_cap": 0, "no_room": 0, "uncounted": 0, "byte_only": 0, "invalid": 0}


def status(**changes):
    return dict(NONE, **changes)


class FakeStream:
    """An async iterator over fixed chunks that records how it was used."""

    def __init__(self, chunks, fail_at=None):
        self.chunks, self.fail_at = list(chunks), fail_at
        self.served, self.closed = 0, 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(0)                      # give other tasks a turn, as a real stream does
        if self.fail_at is not None and self.served == self.fail_at:
            raise RuntimeError("upstream failed CANARY")
        if self.served >= len(self.chunks):
            raise StopAsyncIteration
        self.served += 1
        return self.chunks[self.served - 1]

    async def aclose(self):
        self.closed += 1


async def collect(stream):
    return [item async for item in stream]


def run(coro):
    return asyncio.run(coro)


class MappingTests(unittest.TestCase):
    def test_not_read_means_no_notice_at_all(self):
        self.assertIsNone(adapter.decision_from_hook([], "not-read", status()))

    def test_store_states_from_the_fingerprint(self):
        for fingerprint in ("none", "abc123abc123", "000000000000"):
            decision = adapter.decision_from_hook([], fingerprint, status())
            self.assertEqual((decision.store, decision.notice_kind()), ("available", None))
        self.assertEqual(adapter.decision_from_hook([], "unknown", status()).notice_kind(), "unavailable")
        for odd in ("invalid", "ABC123ABC123", "abc123", "abc123abc123 x", None, 5, ["none"], "abc123abc12\n"):
            self.assertEqual(adapter.decision_from_hook([], odd, status()).notice_kind(), "unknown")

    def test_revision_18_fields_map_onto_the_core(self):
        decision = adapter.decision_from_hook(["t001", "t004"], "abc123abc123",
                                              status(note_cap=1, no_room=2, uncounted=3, invalid=4, byte_only=2))
        self.assertEqual((decision.applied, decision.omitted_cap, decision.omitted_no_room, decision.omitted_uncounted,
                          decision.invalid, decision.byte_only, decision.relevant), (2, 1, 2, 3, 4, 2, 8))

    def test_notice_kinds(self):
        cases = [(["t001"], status(), None), (["t001"], status(byte_only=1), None),
                 ([], status(no_room=1), "omitted"), ([], status(note_cap=1), "omitted"),
                 (["t001"], status(uncounted=1), "uncounted"), (["t001"], status(uncounted=1, no_room=1), "uncounted"),
                 (["t001"], status(invalid=2), "invalid")]
        for used, st, kind in cases:
            self.assertEqual(adapter.decision_from_hook(used, "abc123abc123", st).notice_kind(), kind)

    def test_malformed_hook_results_become_unknown_and_never_raise(self):
        bad = [("t001", status()), (None, status()), (["t001"], None), (["t001"], "CANARY"), (["t001"], {}),
               (["t001"], status(no_room="1")), (["t001"], status(no_room=True)), (["t001"], status(no_room=-1)),
               (["t001"], status(no_room=10**9)), (["t001"], status(byte_only=5))]
        for used, st in bad:
            self.assertEqual(adapter.decision_from_hook(used, "abc123abc123", st).notice_kind(), "unknown")


class CarrierTests(unittest.TestCase):
    def omitted(self):
        return adapter.decision_from_hook(["t001"], "abc123abc123", status(no_room=2))

    def test_nothing_to_show_returns_the_same_request_object(self):
        data = {"model": "m", "messages": [{"role": "user", "content": "hi"}]}
        for decision in (None, adapter.decision_from_hook(["t001"], "abc123abc123", status())):
            self.assertIs(adapter.attach(data, decision, "en"), data)

    def test_carrier_holds_plain_values_only_and_no_note_material(self):
        data = {"model": "m", "messages": [{"role": "user", "content": "question CANARY-REQUEST"}]}
        before = copy.deepcopy(data)
        result = adapter.attach(data, self.omitted(), "ar")
        self.assertEqual(data, before)                                       # input not modified
        self.assertIsNot(result, data)
        self.assertEqual(result["messages"], data["messages"])
        carrier = result[adapter.CARRIER_KEY]
        self.assertEqual(set(carrier), set(adapter.CARRIER_FIELDS) | {"locale", "token"})
        for name, value in carrier.items():
            self.assertTrue(value is None or type(value) in (int, str), name)
        text = json.dumps(carrier)
        for forbidden in ("t001", "abc123abc123", "CANARY", "Be brief"):
            self.assertNotIn(forbidden, text)
        self.assertTrue(adapter.CARRIER_KEY.startswith("_litellm_"))

    def test_a_carrier_planted_by_the_client_is_removed_not_trusted(self):
        planted = adapter.to_carrier(TeachingDecision(store="unavailable"), "en")
        data = {"model": "m", "messages": [], adapter.CARRIER_KEY: planted}
        cleaned = adapter.attach(data, None, "en")
        self.assertNotIn(adapter.CARRIER_KEY, cleaned)
        self.assertIn(adapter.CARRIER_KEY, data)                             # input still untouched
        replaced = adapter.attach(data, self.omitted(), "en")
        self.assertEqual(replaced[adapter.CARRIER_KEY]["omitted_no_room"], 2)

    def test_round_trip_and_shallow_copies(self):
        result = adapter.attach({"model": "m"}, self.omitted(), "ar")
        for request_data in (result, dict(result), copy.copy(result), copy.deepcopy(result)):
            event = adapter.notice_for(request_data).take()
            self.assertIn("بعض الملاحظات", event)

    def test_malformed_or_missing_carrier_gives_no_notice_and_never_raises(self):
        good = adapter.to_carrier(self.omitted(), "en")
        bad = [None, "x", 5, [], {}, dict(good, extra=1), {k: v for k, v in good.items() if k != "locale"},
               dict(good, locale="fr"), dict(good, locale=None), dict(good, store="CANARY"), dict(good, applied=True),
               dict(good, applied="1"), dict(good, omitted_no_room=-1), dict(good, omitted_no_room=10**9),
               dict(good, relevant=99), dict(good, byte_only=50)]
        for carrier in bad:
            self.assertIsNone(adapter.notice_for({adapter.CARRIER_KEY: carrier}))
        for request_data in (None, "x", [], {}, {"model": "m"}):
            self.assertIsNone(adapter.notice_for(request_data))

    def test_unsupported_locale_attaches_nothing(self):
        data = {"model": "m"}
        self.assertIs(adapter.attach(data, self.omitted(), "fr"), data)


class StreamTests(unittest.TestCase):
    CHUNKS = [{"choices": [{"delta": {"content": "```python\n"}}]}, {"choices": [{"delta": {"content": "{\"a\": 1}"}}]},
              "data: raw text chunk", b"bytes chunk", {"choices": [{"delta": {}, "finish_reason": "stop"}]}]

    def request(self, **st):
        decision = adapter.decision_from_hook([], "abc123abc123", status(**st))
        return adapter.attach({"model": "m"}, decision, "en")

    def test_one_event_first_then_every_chunk_untouched(self):
        source = FakeStream(self.CHUNKS)
        items = run(collect(adapter.stream_with_status(source, self.request(no_room=1))))
        self.assertEqual(len(items), len(self.CHUNKS) + 1)
        event = items[0]
        self.assertIs(type(event), str)
        self.assertFalse(event.startswith("data:"))
        self.assertEqual(json.loads(event), {"event": {"type": "status", "data": {
            "description": "Some saved notes were not used for this answer.", "done": True, "hidden": False}}})
        for got, sent in zip(items[1:], self.CHUNKS):
            self.assertIs(got, sent)                                         # the very same objects, in order
        self.assertEqual(source.closed, 1)

    def test_no_notice_is_a_pure_passthrough(self):
        for request_data in (self.request(), {"model": "m"}, None):
            source = FakeStream(self.CHUNKS)
            items = run(collect(adapter.stream_with_status(source, request_data)))
            self.assertEqual(len(items), len(self.CHUNKS))
            self.assertTrue(all(a is b for a, b in zip(items, self.CHUNKS)))

    def test_empty_model_stream_still_shows_the_status_once(self):
        items = run(collect(adapter.stream_with_status(FakeStream([]), self.request(uncounted=1))))
        self.assertEqual(len(items), 1)
        self.assertIn("could not be checked", items[0])

    def test_each_response_attempt_gets_its_own_single_event(self):
        request_data = self.request(no_room=1)

        async def twice():
            first = await collect(adapter.stream_with_status(FakeStream(["a"]), request_data))
            second = await collect(adapter.stream_with_status(FakeStream(["b"]), request_data))
            return first, second
        first, second = run(twice())
        self.assertEqual((len(first), len(second)), (2, 2))                  # a retry is a new attempt
        self.assertEqual(sum(1 for item in first if isinstance(item, str) and "event" in item), 1)

    def test_concurrent_chats_do_not_borrow_each_others_status(self):
        async def both():
            english = adapter.attach({"model": "m"}, adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en")
            arabic = adapter.attach({"model": "m"}, adapter.decision_from_hook([], "unknown", status()), "ar")
            quiet = {"model": "m"}
            streams = [adapter.stream_with_status(FakeStream([f"c{n}-{i}" for i in range(20)]), data)
                       for n, data in enumerate((english, arabic, quiet))]
            return await asyncio.gather(*(collect(s) for s in streams))
        english, arabic, quiet = run(both())
        self.assertIn("were not used", english[0])
        self.assertIn("تعذّر الوصول", arabic[0])
        self.assertEqual(quiet, [f"c2-{i}" for i in range(20)])
        self.assertEqual(english[1:], [f"c0-{i}" for i in range(20)])
        self.assertEqual(arabic[1:], [f"c1-{i}" for i in range(20)])

    def test_upstream_failure_propagates_after_the_status_and_closes_the_source(self):
        source = FakeStream(["a", "b", "c"], fail_at=2)

        async def go():
            got = []
            with self.assertRaises(RuntimeError):
                async for item in adapter.stream_with_status(source, self.request(no_room=1)):
                    got.append(item)
            return got
        got = run(go())
        self.assertEqual(len(got), 3)                                        # status, a, b
        self.assertNotIn("CANARY", got[0])
        self.assertEqual(source.closed, 1)

    def test_client_cancel_closes_the_source_exactly_once(self):
        source = FakeStream([f"c{i}" for i in range(50)])

        async def go():
            stream = adapter.stream_with_status(source, self.request(no_room=1))
            got = [await stream.__anext__(), await stream.__anext__()]
            await stream.aclose()                                            # what a disconnect does
            return got
        got = run(go())
        self.assertEqual(len(got), 2)
        self.assertEqual((source.served, source.closed), (1, 1))

    def test_task_cancellation_closes_the_source(self):
        source = FakeStream([f"c{i}" for i in range(10**6)])

        async def go():
            async def consume():
                async for _ in adapter.stream_with_status(source, self.request(no_room=1)):
                    await asyncio.sleep(0)
            task = asyncio.create_task(consume())
            await asyncio.sleep(0.01)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        run(go())
        self.assertEqual(source.closed, 1)

    def test_source_without_aclose_is_supported(self):
        async def plain():
            yield "a"
            yield "b"

        class NoClose:
            def __init__(self):
                self.inner = plain()

            def __aiter__(self):
                return self

            async def __anext__(self):
                return await self.inner.__anext__()
        items = run(collect(adapter.stream_with_status(NoClose(), self.request(no_room=1))))
        self.assertEqual(items[1:], ["a", "b"])

    def test_number_of_model_chunks_passed_on_equals_number_received(self):
        source = FakeStream([{"n": i} for i in range(137)])
        items = run(collect(adapter.stream_with_status(source, self.request(no_room=1))))
        self.assertEqual((len(items) - 1, source.served), (137, 137))


try:
    from litellm.integrations.custom_logger import CustomLogger
    from litellm.proxy.proxy_server import _format_streaming_sse_chunk
    from litellm.types.utils import is_litellm_owned_kwarg
    from litellm.utils import filter_out_litellm_params
    HAVE_LITELLM = True
except Exception:                                   # the prototype stays testable without the gateway library
    HAVE_LITELLM = False


@unittest.skipUnless(HAVE_LITELLM, "LiteLLM is not installed in this Python")
class InstalledLibraryTests(unittest.TestCase):
    """Checks against the installed library's own functions. Still not the running gateway."""

    def test_event_is_framed_as_one_sse_data_line_that_parses(self):
        request_data = adapter.attach({"model": "m"}, adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "ar")
        event = adapter.notice_for(request_data).take()
        frame = _format_streaming_sse_chunk(event)
        self.assertTrue(frame.startswith("data: ") and frame.endswith("\n\n"))
        self.assertEqual(frame.count("\n"), 2)
        parsed = json.loads(frame[len("data: "):])
        self.assertEqual(parsed["event"]["type"], "status")
        self.assertNotIn("choices", parsed)

    def test_carrier_key_is_classified_as_library_owned_and_filtered(self):
        self.assertTrue(is_litellm_owned_kwarg(adapter.CARRIER_KEY))
        request_data = adapter.attach({"temperature": 0, "stream": True},
                                      adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en")
        kept = filter_out_litellm_params(request_data)
        self.assertNotIn(adapter.CARRIER_KEY, kept)
        self.assertEqual(kept["temperature"], 0)

    def test_override_is_found_on_the_leaf_class(self):
        class Leaf(CustomLogger):
            async def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data):
                async for item in adapter.stream_with_status(response, request_data):
                    yield item

        class Inherits(Leaf):
            pass
        self.assertIn("async_post_call_streaming_iterator_hook", Leaf.__dict__)
        self.assertNotIn("async_post_call_streaming_iterator_hook", Inherits.__dict__)   # why the leaf matters
        request_data = adapter.attach({"model": "m"}, adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en")
        items = run(collect(Leaf().async_post_call_streaming_iterator_hook(None, FakeStream(["a"]), request_data)))
        self.assertEqual((len(items), items[1]), (2, "a"))


class Closable:
    """A source or iterator whose close can be delayed, made to fail, or made to hang."""

    def __init__(self, items=(), delay=0.0, close_error=None, hang=False, fail=None):
        self.items, self.delay, self.close_error, self.hang, self.fail = list(items), delay, close_error, hang, fail
        self.close_started = self.close_finished = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(0)
        if self.fail is not None:
            raise self.fail
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)

    async def aclose(self):
        self.close_started += 1
        if self.hang:
            await asyncio.sleep(3600)
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.close_error is not None:
            raise self.close_error
        self.close_finished += 1


class Iterable:
    """An iterable whose __aiter__ returns a DIFFERENT closable object."""

    def __init__(self, iterator):
        self.iterator = iterator
        self.close_started = self.close_finished = 0

    def __aiter__(self):
        return self.iterator

    async def aclose(self):
        self.close_started += 1
        await asyncio.sleep(0)
        self.close_finished += 1


def omitted_request():
    return adapter.attach({"model": "m"}, adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en")


class LifecycleTests(unittest.TestCase):
    """The three counterexamples from the review of the first prototype, and the stated contract."""

    def test_close_before_the_first_pull_closes_the_source(self):
        source = Closable(["a"])

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            await stream.aclose()
            with self.assertRaises(StopAsyncIteration):
                await stream.__anext__()
            return stream
        stream = run(go())
        self.assertEqual((source.close_started, source.close_finished, stream.cleanup), (1, 1, "done"))

    def test_distinct_iterable_and_iterator_are_both_closed_once(self):
        iterator = Closable(["a", "b"])
        source = Iterable(iterator)

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            items = [item async for item in stream]
            await stream.aclose()                       # a second close does nothing more
            return stream, items
        stream, items = run(go())
        self.assertEqual(items[1:], ["a", "b"])
        self.assertEqual((iterator.close_finished, source.close_finished, stream.cleanup), (1, 1, "done"))
        self.assertEqual((iterator.close_started, source.close_started), (1, 1))

    def test_distinct_iterable_closed_before_first_pull_closes_only_what_exists(self):
        iterator = Closable(["a"])
        source = Iterable(iterator)

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            await stream.aclose()
            return stream
        stream = run(go())
        self.assertEqual((source.close_finished, iterator.close_started, stream.cleanup), (1, 0, "done"))

    def test_upstream_error_survives_a_failing_close(self):
        source = Closable(fail=RuntimeError("upstream PRIMARY"), close_error=ValueError("close CANARY"))

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            await stream.__anext__()                    # the status
            with self.assertRaises(RuntimeError) as caught:
                await stream.__anext__()
            return stream, caught.exception
        stream, error = run(go())
        self.assertEqual(str(error), "upstream PRIMARY")
        self.assertEqual((stream.cleanup, stream.close_errors), ("failed", ["ValueError"]))   # type name only

    def test_delayed_close_is_awaited_to_the_end(self):
        source = Closable(["a"], delay=0.05)

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            items = [item async for item in stream]
            return stream, items
        stream, items = run(go())
        self.assertEqual((len(items), source.close_finished, stream.cleanup), (2, 1, "done"))

    def test_cancellation_during_cleanup_is_raised_keeps_the_upstream_error_and_cleanup_finishes(self):
        source = Closable(fail=RuntimeError("upstream PRIMARY"), delay=0.05)

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            await stream.__anext__()

            async def pull():
                await stream.__anext__()
            task = asyncio.create_task(pull())
            while source.close_started == 0:            # forced interleaving: cancel exactly while close is running
                await asyncio.sleep(0)
            self.assertEqual(source.close_finished, 0)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError) as caught:
                await task
            state_at_cancel = (stream.cleanup, source.close_finished)
            await stream.aclose()                       # waits for the SAME cleanup; does not start another
            return stream, caught.exception, state_at_cancel
        stream, cancelled, state_at_cancel = run(go())
        self.assertEqual(state_at_cancel, ("closing", 0))                       # honestly not finished yet
        self.assertIsInstance(cancelled.__context__, RuntimeError)             # the upstream error is not lost
        self.assertEqual(str(cancelled.__context__), "upstream PRIMARY")
        self.assertEqual((source.close_started, source.close_finished, stream.cleanup), (1, 1, "done"))

    def test_cancelled_consumer_does_not_abandon_cleanup(self):
        source = Closable([f"c{i}" for i in range(1000)], delay=0.05)

        async def go():
            stream = adapter.status_stream(source, omitted_request())

            async def consume():
                async for _ in stream:
                    await asyncio.sleep(0)
            task = asyncio.create_task(consume())
            await asyncio.sleep(0.01)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            await stream.aclose()
            return stream
        stream = run(go())
        self.assertEqual((source.close_started, source.close_finished, stream.cleanup), (1, 1, "done"))

    def test_close_that_never_returns_is_reported_uncertain_after_the_deadline(self):
        source = Closable(["a"], hang=True)
        saved = adapter.CLOSE_TIMEOUT_SECONDS
        adapter.CLOSE_TIMEOUT_SECONDS = 0.05
        try:
            async def go():
                stream = adapter.status_stream(source, omitted_request())
                started = asyncio.get_running_loop().time()
                await stream.aclose()
                return stream, asyncio.get_running_loop().time() - started
            stream, waited = run(go())
        finally:
            adapter.CLOSE_TIMEOUT_SECONDS = saved
        self.assertEqual((stream.cleanup, source.close_started, source.close_finished), ("uncertain", 1, 0))
        self.assertLess(waited, 2.0)                    # a cooperative deadline, not a hard guarantee

    def test_concurrent_close_calls_share_one_cleanup(self):
        source = Closable(["a"], delay=0.02)

        async def go():
            stream = adapter.status_stream(source, omitted_request())
            await asyncio.gather(stream.aclose(), stream.aclose(), stream.aclose())
            return stream
        stream = run(go())
        self.assertEqual((source.close_started, source.close_finished, stream.cleanup), (1, 1, "done"))


class ForgedCarrierTests(unittest.TestCase):
    def test_well_formed_carrier_without_this_process_token_is_rejected(self):
        genuine = omitted_request()[adapter.CARRIER_KEY]
        self.assertIsNotNone(adapter.notice_for({adapter.CARRIER_KEY: dict(genuine)}))
        for token in ("", "0" * 32, None, 5, genuine["token"][:-1] + ("0" if genuine["token"][-1] != "0" else "1")):
            forged = dict(genuine, token=token)
            self.assertIsNone(adapter.notice_for({adapter.CARRIER_KEY: forged}))
        without = {k: v for k, v in genuine.items() if k != "token"}
        self.assertIsNone(adapter.notice_for({adapter.CARRIER_KEY: without}))

    def test_token_is_not_part_of_the_event_shown_to_the_user(self):
        data = omitted_request()
        event = adapter.notice_for(data).take()
        self.assertNotIn(data[adapter.CARRIER_KEY]["token"], event)


@unittest.skipUnless(HAVE_LITELLM, "LiteLLM is not installed in this Python")
class InstalledGeneratorTests(unittest.TestCase):
    """Through the installed proxy's own streaming generator, with the callback REGISTERED the way
    the proxy discovers callbacks. Still no server, no model, no network, and not the running gateway."""

    def frames(self, request_data, source):
        import litellm
        from litellm.proxy import proxy_server
        from litellm.proxy._types import UserAPIKeyAuth
        from litellm.proxy.utils import ProxyLogging

        class Leaf(CustomLogger):
            def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data):
                return adapter.status_stream(response, request_data)

        saved = litellm.callbacks
        litellm.callbacks = [Leaf()]
        try:
            caps = ProxyLogging.callback_capabilities()
            self.assertTrue(caps.has_iterator_override)                     # the framework itself found the override

            async def go():
                out = []
                async for frame in proxy_server.async_data_generator(source, UserAPIKeyAuth(), request_data):
                    out.append(frame if isinstance(frame, str) else frame.decode("utf-8"))
                return out
            return run(go())
        finally:
            litellm.callbacks = saved

    def model_chunks(self):
        from litellm.types.utils import ModelResponseStream

        def chunk(text, finish=None):
            return ModelResponseStream(id="chatcmpl-test", model="local-qwen36-chat", created=1,
                                       choices=[{"index": 0, "delta": {"content": text}, "finish_reason": finish}])
        return [chunk("```python\n"), chunk("x = {\"a\": 1}\n"), chunk("```"), chunk("", "stop")]

    def answer(self, frames):
        text = ""
        for frame in frames:
            body = frame[len("data: "):].strip()
            if body == "[DONE]":
                continue
            parsed = json.loads(body)
            if "choices" in parsed:
                text += parsed["choices"][0]["delta"].get("content") or ""
        return text

    def test_event_frame_then_identical_answer_frames(self):
        plain = self.frames({"model": "local-qwen36-chat", "stream": True}, FakeStream(self.model_chunks()))
        data = adapter.attach({"model": "local-qwen36-chat", "stream": True},
                              adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en")
        noticed = self.frames(data, FakeStream(self.model_chunks()))
        self.assertEqual(len(noticed), len(plain) + 1)
        first = json.loads(noticed[0][len("data: "):])
        self.assertEqual(first["event"]["type"], "status")
        self.assertNotIn("choices", first)
        self.assertEqual(noticed[1:], plain)                                # every answer frame byte-identical
        self.assertEqual(self.answer(noticed), "```python\nx = {\"a\": 1}\n```")
        self.assertEqual(noticed[-1], "data: [DONE]\n\n")

    def test_source_is_closed_when_the_proxy_generator_finishes(self):
        source = FakeStream(self.model_chunks())
        self.frames(adapter.attach({"model": "m", "stream": True},
                                   adapter.decision_from_hook([], "abc123abc123", status(no_room=1)), "en"), source)
        self.assertGreaterEqual(source.closed, 1)


if __name__ == "__main__":
    unittest.main()
