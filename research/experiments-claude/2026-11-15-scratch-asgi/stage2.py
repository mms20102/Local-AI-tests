"""Stage 2: completed requests through the REAL LiteLLM proxy ASGI app to a fake upstream.

Transport: httpx ASGITransport, which buffers the whole response. That is right for completed
requests, error serialization and completed SSE framing, and it is NOT a disconnect test (stage 3).

Setup that is real: the proxy's own lifespan and config loader (custom auth, router, callbacks loaded
from the scratch config by name), the published gateway and teach source, the installed OpenAI client
making a real HTTP request over loopback. Handwritten: the config and settings values, the keys, the
notes, the fake upstream, and integration_candidate.py (the candidate wiring under test).
"""
import asyncio
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import httpx

from fixture_common import ANSWER_TEXT, FakeUpstream, Guard, running_proxy, write_scratch_files

MODE = os.environ["SCRATCH_MODE"]
KEY = os.environ["WEBUI_GATEWAY_KEY"]
AUTH = {"Authorization": "Bearer " + KEY}
RESULTS = []
CARRIER = "_litellm_teach_status_v1"


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def frames_of(text):
    out = []
    for raw in text.split("\n\n"):
        raw = raw.strip()
        if not raw:
            continue
        check(raw.startswith("data: "), "frame without data prefix: " + raw[:60])
        body = raw[len("data: "):]
        out.append("[DONE]" if body == "[DONE]" else json.loads(body))
    return out


def answer_of(frames):
    return "".join((f["choices"][0]["delta"].get("content") or "") for f in frames
                   if isinstance(f, dict) and "choices" in f and f["choices"])


def events_of(frames):
    return [f for f in frames if isinstance(f, dict) and "event" in f]


def no_internal_keys(capture):
    text = json.dumps(capture)
    check(CARRIER not in text, "carrier reached the upstream")
    check(not any(k.startswith("_litellm") for k in capture), "internal key reached the upstream: " + str(list(capture)))
    check("token" not in capture, "token field upstream")


async def main():
    import integration_candidate as ic
    import teach_store as ts
    import token_count
    guard = Guard()
    guard.install()
    upstream = FakeUpstream()
    port = await upstream.start()
    config = write_scratch_files(port)
    store_dir = ts.DEFAULT_DIR
    check("asgi-scratch" in str(store_dir), "store is not in the scratch folder: " + str(store_dir))
    real_counter = token_count.load_counter()

    def reset_store(*notes):
        shutil.rmtree(store_dir, ignore_errors=True)
        store = ts.Store(store_dir)
        for note in notes:
            if isinstance(note, tuple):
                store.add(note[0], when=note[1])
            else:
                store.add(note)
        return store

    def body(messages, max_tokens=64, stream=False):
        return {"model": "local-qwen36-chat", "temperature": 0, "max_tokens": max_tokens, "stream": stream,
                "messages": messages}

    async with running_proxy(config) as proxy_server:
        import gateway_auth
        limits = gateway_auth.LIMITS
        transport = httpx.ASGITransport(app=proxy_server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://scratch.invalid", timeout=60) as client:

            async def post(payload, headers=AUTH, raw=None):
                before = len(upstream.captures)
                if raw is not None:
                    r = await client.post("/v1/chat/completions", content=raw, headers=headers)
                else:
                    r = await client.post("/v1/chat/completions", json=payload, headers=headers)
                return r, upstream.captures[before:]

            async def case(name, fn):
                try:
                    detail = await fn()
                    RESULTS.append({"case": name, "result": "pass", "detail": detail})
                    print("PASS", name, "|", detail or "", flush=True)
                except Exception as error:  # noqa: BLE001
                    RESULTS.append({"case": name, "result": "FAIL", "detail": type(error).__name__ + ": " + str(error)[:300]})
                    print("FAIL", name, "|", type(error).__name__, str(error)[:300], flush=True)
                    traceback.print_exc(limit=2)

            # ---------------------------------------------------------------- shared cases
            async def empty_store_nonstream():
                reset_store()
                messages = [{"role": "user", "content": "hi"}]
                r, caps = await post(body(messages))
                check(r.status_code == 200, r.text[:200])
                check(len(caps) == 1, f"{len(caps)} captures")
                cap = caps[0]
                check(cap["messages"] == messages, "messages changed with an empty store")
                check(cap["model"] == "qwen3.6-colibri", cap["model"])
                check(cap["max_tokens"] == 64 and cap["temperature"] == 0, "output fields changed")
                check(not cap.get("stream"), "stream flag set")
                no_internal_keys(cap)
                check(r.json()["choices"][0]["message"]["content"] == ANSWER_TEXT, "answer text changed")
                check(r.json()["usage"] == {"completion_tokens": 7, "prompt_tokens": 11, "total_tokens": 18}, "usage changed")
                check(ic.DECISIONS[-1][0] == [] and ic.DECISIONS[-1][1] in ("none",) or len(ic.DECISIONS[-1][1]) == 12, "decision")
                return "upstream keys: " + ",".join(sorted(cap))

            async def empty_store_stream():
                reset_store()
                r, caps = await post(body([{"role": "user", "content": "hi"}], stream=True))
                check(r.status_code == 200, r.text[:200])
                frames = frames_of(r.text)
                check(not events_of(frames), "event with nothing to report")
                check(answer_of(frames) == ANSWER_TEXT, "answer text changed")
                check(frames[-1] == "[DONE]", "no DONE")
                check(len(caps) == 1 and caps[0].get("stream") is True, "stream flag")
                no_internal_keys(caps[0])
                state["plain_stream_text"] = r.text
                return f"{len(frames)} frames"

            async def rejected_shapes_zero_captures():
                reset_store("Be brief.")
                ok = [{"role": "user", "content": "CANARY-REQUEST-TEXT"}]
                cases = [
                    ("later system", body([{"role": "user", "content": "a"}, {"role": "system", "content": "b"},
                                           {"role": "user", "content": "c"}]), None, AUTH, 422, "local_chat_policy"),
                    ("reasoning tag", body([{"role": "user", "content": "a"}, {"role": "assistant", "content": "t</think>x"},
                                            {"role": "user", "content": "c"}]), None, AUTH, 422, "local_chat_policy"),
                    ("tools", dict(body(ok), tools=[]), None, AUTH, 403, "local_chat_policy"),
                    ("null content", body([{"role": "user", "content": None}]), None, AUTH, 422, "local_chat_policy"),
                    ("list content", body([{"role": "user", "content": [{"type": "text", "text": "x"}]}]), None, AUTH, 422,
                     "local_chat_policy"),
                    ("wrong model", dict(body(ok), model="other"), None, AUTH, 403, "local_chat_policy"),
                    ("extra field", dict(body(ok), top_p=1), None, AUTH, 422, "local_chat_policy"),
                    ("planted carrier", dict(body(ok), **{CARRIER: {"store": "unavailable"}}), None, AUTH, 422,
                     "local_chat_policy"),
                    # Observed: the framework refuses malformed JSON itself, before the gateway's custom auth runs,
                    # with its own error type. The gateway's "Invalid JSON request." path is therefore not reached.
                    ("bad json", None, b"{not json", dict(AUTH, **{"Content-Type": "application/json"}), 400, "invalid_request_error/request_body"),
                    ("wrong content type", None, json.dumps(body(ok)).encode(), dict(AUTH, **{"Content-Type": "text/plain"}),
                     415, "local_chat_policy"),
                    ("bad key", body(ok), None, {"Authorization": "Bearer wrong"}, 401, "local_chat_policy"),
                    ("no key", body(ok), None, {}, 401, None),
                ]
                seen = []
                for name, payload, raw, headers, status, error_type in cases:
                    r, caps = await post(payload, headers=headers, raw=raw)
                    check(len(caps) == 0, f"{name}: reached the upstream")
                    check(r.status_code == status, f"{name}: HTTP {r.status_code} {r.text[:120]}")
                    if error_type is not None:
                        err = r.json()["error"]
                        want_type, _, want_param = error_type.partition("/")
                        check(err["type"] == want_type and err["param"] == (want_param or "request"), f"{name}: {err}")
                        check("CANARY-REQUEST-TEXT" not in r.text and KEY not in r.text, f"{name}: leak")
                    seen.append(f"{name}={r.status_code}" + ("" if error_type is None else "/" + r.json()["error"]["type"]))
                return "; ".join(seen)

            async def selected_note_nonstream():
                reset_store("Be brief.")
                messages = [{"role": "user", "content": "hi"}]
                expected, used, left = ts.apply_with_status(messages, ts.Store(store_dir).entries(), limits, 64,
                                                            count_tokens=real_counter if MODE == "bound" else None)
                r, caps = await post(body(messages))
                check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                cap = caps[0]
                check(cap["messages"] == expected, "upstream messages differ from the candidate that was built and counted")
                check([m["role"] for m in cap["messages"]] == ["system", "user"], "role order")
                check(cap["messages"][1]["content"] == "<saved_notes>\n- Be brief.\n</saved_notes>\n\nhi", "user content")
                check(cap["messages"][0]["content"] == ts.POLICY, "system content")
                check(cap["max_tokens"] == 64, "output allowance changed")
                no_internal_keys(cap)
                if real_counter is not None:
                    counted = real_counter(cap["messages"])
                    check(counted + 64 + 32 <= limits["context_tokens"], "final request over budget")
                    extra = f"; final prompt {counted} tokens"
                else:
                    extra = ""
                check(ic.DECISIONS[-1][0] == used == ["t001"], "decision ids")
                return f"status {ic.DECISIONS[-1][2]}{extra}"

            async def arabic_history_note():
                reset_store("أجب بإيجاز.")
                messages = [{"role": "system", "content": "أنت مساعد."}, {"role": "user", "content": "ما عاصمة مصر؟"},
                            {"role": "assistant", "content": "القاهرة."}, {"role": "user", "content": "وما أكبر مدينة بعدها؟"}]
                r, caps = await post(body(messages))
                check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                got = caps[0]["messages"]
                check([m["role"] for m in got] == ["system", "user", "assistant", "user"], "role order")
                check(got[0]["content"] == "أنت مساعد.\n\n" + ts.POLICY, "policy not appended to the existing system message")
                check(got[1] == messages[1] and got[2] == messages[2], "history changed")
                check(got[3]["content"] == "<saved_notes>\n- أجب بإيجاز.\n</saved_notes>\n\n" + messages[3]["content"], "last user")
                no_internal_keys(caps[0])
                return "history preserved, note in the latest user message only"

            async def note_over_cap_stream_shows_one_event():
                reset_store(("word " * 58).strip())                       # relevant, but over the notes size cap
                r, caps = await post(body([{"role": "user", "content": "hi"}], stream=True))
                check(r.status_code == 200, r.text[:200])
                frames = frames_of(r.text)
                events = events_of(frames)
                check(len(events) == 1 and frames[0] is events[0], "exactly one event, first")
                check(events[0] == {"event": {"type": "status", "data": {
                    "description": "Some saved notes were not used for this answer.", "done": True, "hidden": False}}}, str(events[0]))
                check("choices" not in events[0], "event carries choices")
                check(r.text.split("\n\n", 1)[1] == state["plain_stream_text"], "answer frames differ from the run without a notice")
                check(answer_of(frames) == ANSWER_TEXT, "answer text changed")
                check(caps[0]["messages"] == [{"role": "user", "content": "hi"}], "request changed although the note was left out")
                no_internal_keys(caps[0])
                check(ic.STREAMS[-1].cleanup == "done", "cleanup state " + ic.STREAMS[-1].cleanup)
                return f"status {ic.DECISIONS[-1][2]}; cleanup {ic.STREAMS[-1].cleanup}"

            async def note_over_cap_nonstream_has_no_notice():
                reset_store(("word " * 58).strip())
                r, caps = await post(body([{"role": "user", "content": "hi"}]))
                check(r.status_code == 200, r.text[:200])
                check("event" not in r.json() and r.json()["choices"][0]["message"]["content"] == ANSWER_TEXT, "body changed")
                return "non-streamed answer carries no notice (known limit)"

            async def concurrent_streams_keep_their_own_status():
                reset_store(("when python " + "word " * 56).strip() and ("Use tabs " + "word " * 56, ["python"]))
                with_note = body([{"role": "user", "content": "python question"}], stream=True)
                without = body([{"role": "user", "content": "unrelated question"}], stream=True)
                results = await asyncio.gather(*(post(p) for p in (with_note, without, with_note, without)))
                counts = [len(events_of(frames_of(r.text))) for r, _ in results]
                check(counts == [1, 0, 1, 0], f"event counts {counts}")
                check(all(answer_of(frames_of(r.text)) == ANSWER_TEXT for r, _ in results), "an answer changed")
                return f"event counts {counts}"

            shared = [("empty store, non-streamed", empty_store_nonstream), ("empty store, streamed", empty_store_stream),
                      ("rejected shapes reach no upstream", rejected_shapes_zero_captures),
                      ("selected note, exact upstream body", selected_note_nonstream),
                      ("Arabic with history and a note", arabic_history_note),
                      ("left-out note, streamed: one event, answer frames identical", note_over_cap_stream_shows_one_event),
                      ("left-out note, non-streamed: no notice", note_over_cap_nonstream_has_no_notice),
                      ("four concurrent streams", concurrent_streams_keep_their_own_status)]
            state = {}
            for name, fn in shared:
                await case(name, fn)

            long_text = "The harbour town kept a ledger of every ship that arrived. " * 110        # about 1,400 tokens

            if MODE == "bound":
                async def measured_overflow():
                    reset_store("Be brief.")
                    r, caps = await post(body([{"role": "user", "content": long_text * 2}], max_tokens=256))
                    check(r.status_code == 413 and len(caps) == 0, f"{r.status_code} {len(caps)}")
                    check(r.json()["error"]["type"] == "local_chat_context_budget_exceeded", r.text[:200])
                    return r.json()["error"]["type"]

                async def long_request_gets_note_by_tokens():
                    reset_store("Be brief.")
                    messages = [{"role": "user", "content": long_text}]
                    check(ts.request_units(messages, limits, 256) > limits["context_tokens"], "not over the byte rule")
                    r, caps = await post(body(messages, max_tokens=256))
                    check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                    got = caps[0]["messages"]
                    check(got[-1]["content"].startswith("<saved_notes>\n- Be brief.\n</saved_notes>\n\n"), "note missing")
                    check(got[-1]["content"].endswith(long_text.strip()) or got[-1]["content"].endswith(long_text), "question changed")
                    counted = real_counter(got)
                    check(counted + 256 + 32 <= limits["context_tokens"], f"over budget: {counted}")
                    check(caps[0]["max_tokens"] == 256, "output allowance changed")
                    no_internal_keys(caps[0])
                    return f"final prompt {counted} tokens + 256 + 32 <= 2048; status {ic.DECISIONS[-1][2]}"

                async def no_room_leaves_note_out_and_says_so():
                    filler = "The harbour town kept a ledger of every ship that arrived. "
                    text = filler * 100
                    while real_counter([{"role": "user", "content": text + filler}]) + 256 + 32 <= limits["context_tokens"]:
                        text += filler
                    reset_store("Be brief.")
                    messages = [{"role": "user", "content": text}]
                    base = real_counter(messages)
                    r, caps = await post(body(messages, max_tokens=256, stream=True))
                    check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                    check(caps[0]["messages"] == [{"role": "user", "content": text}] or caps[0]["messages"][0]["content"].strip() == text.strip(),
                          "request changed although there was no room")
                    events = events_of(frames_of(r.text))
                    check(len(events) == 1 and "were not used" in events[0]["event"]["data"]["description"], str(events))
                    check(ic.DECISIONS[-1][2]["no_room"] == 1, str(ic.DECISIONS[-1][2]))
                    return f"base prompt {base} tokens; status {ic.DECISIONS[-1][2]}"

                async def configured_counter_failure_withdraws_notes():
                    reset_store("Be brief.")
                    saved = ic.teach.count_tokens

                    def broken(messages):
                        raise RuntimeError("tokenizer fault CANARY")
                    ic.teach.count_tokens = broken
                    try:
                        messages = [{"role": "user", "content": "hi"}]
                        r, caps = await post(body(messages, stream=True))
                    finally:
                        ic.teach.count_tokens = saved
                    check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                    check(caps[0]["messages"] == messages, "notes were sent although the final count failed")
                    events = events_of(frames_of(r.text))
                    check(len(events) == 1 and "could not be checked" in events[0]["event"]["data"]["description"], str(events))
                    check("CANARY" not in r.text, "exception text leaked")
                    check(ic.DECISIONS[-1][2]["uncounted"] == 1, str(ic.DECISIONS[-1][2]))
                    return f"status {ic.DECISIONS[-1][2]}"

                for name, fn in [("measured overflow is refused with its reason", measured_overflow),
                                 ("long request gets its note by token budget", long_request_gets_note_by_tokens),
                                 ("no room: note left out, one event", no_room_leaves_note_out_and_says_so),
                                 ("configured counter fails: notes withdrawn, one event", configured_counter_failure_withdraws_notes)]:
                    await case(name, fn)
            else:
                async def absent_counter_refuses_long_request_with_its_reason():
                    reset_store()
                    r, caps = await post(body([{"role": "user", "content": long_text}], max_tokens=256))
                    check(r.status_code == 413 and len(caps) == 0, f"{r.status_code} {len(caps)}")
                    check(r.json()["error"]["type"] == "local_chat_counter_unavailable", r.text[:200])
                    return r.json()["error"]["type"]

                async def absent_counter_keeps_note_on_byte_rule_and_labels_it():
                    reset_store("Be brief.")
                    r, caps = await post(body([{"role": "user", "content": "hi"}], stream=True))
                    check(r.status_code == 200 and len(caps) == 1, r.text[:200])
                    check(caps[0]["messages"][-1]["content"].startswith("<saved_notes>"), "note missing")
                    check(ic.DECISIONS[-1][2]["byte_only"] == 1, str(ic.DECISIONS[-1][2]))
                    check(not events_of(frames_of(r.text)), "byte-only is a label, not an omission notice")
                    return f"status {ic.DECISIONS[-1][2]}"

                check(gateway_auth.COUNT_TOKENS is None and ic.teach.count_tokens is None, "counter present in nocounter mode")
                for name, fn in [("absent counter: long request refused with its reason", absent_counter_refuses_long_request_with_its_reason),
                                 ("absent counter: note kept on the byte rule and labelled", absent_counter_keeps_note_on_byte_rule_and_labels_it)]:
                    await case(name, fn)

        counter_state = (gateway_auth.COUNT_TOKENS is not None, gateway_auth.COUNT_REASON)
    await upstream.stop()
    shutil.rmtree(store_dir, ignore_errors=True)
    summary = {"mode": MODE, "counter": counter_state, "passed": sum(r["result"] == "pass" for r in RESULTS),
               "failed": sum(r["result"] != "pass" for r in RESULTS), "upstream_captures": len(upstream.captures),
               "upstream_port": port, "guard_violations": guard.violations, "loopback_ports_connected": sorted(guard.loopback_ports),
               "proactor_guarded": getattr(guard, "proactor_guarded", None), "results": RESULTS}
    Path(f"stage2-{MODE}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print("SUMMARY", json.dumps({k: v for k, v in summary.items() if k != "results"}), flush=True)
    return 1 if summary["failed"] else 0

sys.exit(asyncio.run(main()))
