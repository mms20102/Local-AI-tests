# Synthetic proxy/ASGI fixture: source and results

Run by Claude (laptop session) on 2026-11-15, after Mohamed's direct confirmation. Offline and
synthetic: no model, no live service, no real key, setting or note. **Nothing here is loaded in the
laptop's gateway.** The scratch folder used for the run has been deleted; these are the files.

## Files

| File | What it is |
|---|---|
| `launch.py` | Starts a stage as a new process with an explicit synthetic environment. Mode `bound` reports the pinned served profile so real token counting is used; mode `nocounter` reports none. |
| `fixture_common.py` | The fake upstream (a small HTTP server on a fresh loopback port that returns fixed text), the network guard, the handwritten settings and proxy config, and the proxy lifespan. |
| `app/integration_candidate.py` | The candidate wiring under test: one leaf class with teach revision 18's pre-call hook, the status carrier, and the iterator override. Fixture only. |
| `stage2.py` | Completed requests through the buffered ASGI transport. |
| `stage3.py` | Client disconnects through a direct ASGI `receive`/`send` driver. |
| `stage2-bound.json`, `stage2-nocounter.json`, `stage3.json` | Results as written by the runs. Site-package paths shortened; nothing else edited. |

The source under test is not duplicated here. The run copied it from this branch at `7f704da`:
`gateway-admission/` (`chat_contract.py` blob `fe34991ee90e`, `gateway_auth.py` `6451b2c4e6b6`,
`token_count.py` `a0305173fe6d`), `teach-store/` (`teach_store.py` `695b3e981381`, `teach_hook.py`
`5b8070cc290a`) and `teach-status-adapter-prototype/` (`teach_status_core.py` `c07df5220f20`,
`teach_status_adapter.py` `a9a141769b19`).

Packages, read-only from the gateway environment: Python 3.12.16, litellm 1.108.5, openai 3.49.0,
tokenizers 0.23.3, fastapi 0.162.5, starlette 1.10.0, httpx 0.28.1, anyio 4.16.0, uvicorn 0.54.0
(uvicorn itself was not used; the fake upstream is plain asyncio).

## What is real and what is handwritten

Real: LiteLLM's proxy ASGI application, started through its own lifespan and config loader; custom
auth, router and callbacks loaded by name from the config; the published gateway and teach source;
the installed OpenAI client making a real HTTP request over loopback to the fake upstream; Starlette's
streaming response and LiteLLM's closing wrapper around it.

Handwritten: the config and settings values (same shape as a text-only gateway), the keys, the notes,
the fake upstream, the candidate wiring, and in stage 3 the ASGI server side (`receive`/`send`).
One real file is read: the model's `tokenizer.json`, for the profile-bound counter.

## Results

Stage 2, completed requests: **12 of 12 cases pass with the counter bound; 10 of 10 with no counter.**
Stage 3, disconnects: **5 of 5 cases meet their assertions**, two of them recorded as observed
outcomes that differ from what the library's source suggested (below). Stage 3 was run three times
with the same outcome; stage 2 twice per mode.

Network guard, every run: zero refused connections; the only port connected to was the fake upstream's.

### Stage 2 (`stage2-*.json`)

- Empty store: the upstream body is exactly the request's messages, model mapped to
  `qwen3.6-colibri`, `max_tokens` and `temperature` as sent; upstream keys are `max_tokens`,
  `messages`, `model`, `temperature` (plus `stream` when streaming). No internal key.
- Selected note: the upstream messages equal, item for item, the candidate built and counted by
  `apply_with_status`; the output allowance is unchanged; the final prompt fits with it reserved.
- Arabic with history: roles in order, policy appended to the existing system message, history
  untouched, note only in the latest user message.
- Left-out note, streamed: exactly one status event as the first frame, no `choices` in it, and
  **the rest of the response body is byte-identical to the run with no notice**.
- Left-out note, non-streamed: no notice. Known limit.
- Four concurrent streams, two with a notice and two without: each gets its own.
- Twelve refused requests reach no upstream: later system message, reasoning tag in history, tools,
  null content, list content, wrong model, extra field, a planted carrier, malformed JSON, wrong
  content type, wrong key, no key. Real HTTP statuses and error types are recorded per case.
- Counter bound: a measured overflow is refused with `local_chat_context_budget_exceeded`; a long
  request over the byte rule gets its note by token budget (final prompt 1,383 tokens); with no room
  the note is left out and one event says so; a failing configured counter withdraws the notes,
  one event says they could not be checked, and the exception text does not appear.
- No counter: a long request is refused with `local_chat_counter_unavailable`; a short request keeps
  its note on the byte rule, labelled `byte_only`, with no event.

### Stage 3 (`stage3.json`)

Declared for every case: ASGI application version 3.0. HTTP `spec_version` 2.3 unless stated.

| Case | Application call | Disconnect seen via `receive` | Bodies accepted | Adapter cleanup | Upstream closed before finishing |
|---|---|---|---|---|---|
| Complete stream | returned | — | 7 | `done` | no (completed) |
| Disconnect while `send` is blocked between pulls | returned | yes; the parked send was cancelled | 2 | `done` | yes |
| Disconnect during a backend pull | returned | yes | 3 | `done` | yes |
| Disconnect requested before the first chunk | returned after 30.5 s with HTTP 408 | **no** | 1 (the error body) | no adapter stream was created | yes, at the upstream timeout |
| HTTP spec 2.4: `send` raises `OSError` | **raised `ModuleNotFoundError`** | — | 2 | `done` | yes |

After every case the proxy served a normal request.

## Findings that are not about the adapter

1. **Malformed JSON is refused by the framework before the gateway's custom auth runs**, with type
   `invalid_request_error` and param `request_body`. The gateway's own "Invalid JSON request." path
   is not reached on this route.
2. **A disconnect before the first chunk was not observed by the application in this fixture.** It
   never called `receive` again; the request ended when the upstream call hit its timeout (30 s in
   the scratch config). The fake upstream had sent response headers and was holding the first event.
   Whether this is the fixture's shape or the library's behaviour on this path is not settled here.
3. **Under HTTP spec 2.4 the application call ended with `ModuleNotFoundError: No module named
   'prisma'`**, raised from the proxy's exception handling after the framework reported the
   disconnect. The adapter and upstream were still cleaned up. The installed uvicorn declares HTTP
   spec 2.3, so the running gateway does not take this path.

## Not established

- Display in Open WebUI or any browser.
- Token or usage accounting for a stream that begins with the status event. Non-streamed `usage`
  passes through unchanged; streamed accounting was not examined.
- Anything about the running gateway: this was a separate process with its own config.
- Native tokenizer equivalence or the basis of the 32-token allowance.
- Retries and fallbacks (set to none), and more than four concurrent requests.
- Timing: no latency was measured.

## Run

```
set SCRATCH_PYTHON=<python with LiteLLM 1.108.5>
python launch.py bound stage2.py
python launch.py nocounter stage2.py
python launch.py bound stage3.py
```

The stages expect an `app/` folder holding copies of the seven source files listed above beside
`integration_candidate.py`, and they create and delete a throwaway store under `app/.runtime/`.
