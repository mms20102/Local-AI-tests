# Teach status adapter: offline prototype

Published by Claude (laptop session) on 2026-11-14 for review. **Not loaded, not registered, not
part of the running gateway.** No gateway, hook or configuration file on the laptop was changed
for it. It follows the handoff in co-chat at `07db9cc`.

| File | What it is |
|---|---|
| `teach_status_core.py` | The tested core from branch `codex/teach-status-core-20261114`, byte-identical (git blob `c07df5220f2064163ed5d11d035f6382fc4a9191`). Not modified. |
| `teach_status_adapter.py` | The adapter: maps teach revision 18's final result to a decision, carries it in request data, and wraps the response stream. |
| `test_teach_status_adapter.py` | 46 tests on handwritten fake streams. Five need the LiteLLM library and are skipped without it. |
| `real_generator_check.py` | A script that pushes a fake model stream through the installed LiteLLM proxy generator with the adapter registered, and prints the frames. |

## What it does

1. `decision_from_hook(used, fingerprint, status)`: the hook's final result from one store
   snapshot becomes a `TeachingDecision`. Fingerprint `not-read` gives no notice at all; `none` or
   12 hex digits means the store was read; `unknown` means it could not be read; anything
   malformed gives the "could not be verified" decision. It never raises.
2. `attach(data, decision, locale)`: puts a carrier of integers and two fixed words under
   `_litellm_teach_status_v1`. No note text, entry ids or fingerprint. A carrier already present in
   the incoming request is removed, so a client cannot plant one. With nothing to show, the same
   request object is returned.
3. `status_stream(response, request_data)`: what an
   `async_post_call_streaming_iterator_hook` override on the registered leaf class returns. It is an
   object, not an async generator, so closing it before the first pull still closes the source. It yields one
   JSON status event as text with no `data:` prefix, then every model chunk, the same objects in
   the same order. It closes the model stream when it ends or fails, and when the caller calls
   `aclose()`. **The caller must call `aclose()`**: an object iterator is not told when its consumer
   stops between two pulls. LiteLLM's proxy does this in a `finally`.

The locale is an explicit argument, `en` or `ar`. Nothing here chooses it.

## Evidence (measured on the laptop, offline)

- 46 tests pass with the gateway's own Python and LiteLLM 1.108.5; 41 pass and 5 are skipped with
  a Python that has no LiteLLM. Each was run several times in a row.
- With the installed library's own functions: the carrier key is classified as library-owned and
  removed by `filter_out_litellm_params`; the event is framed as one `data:` line that parses; the
  override is found on the leaf class and not on a subclass that only inherits it.
- `real_generator_check.py`, through the installed `proxy_server.async_data_generator` with the
  adapter registered as a callback and a fake stream of real `ModelResponseStream` chunks:
  with a notice, 6 frames: the status event (no `choices` key), four answer chunks, `[DONE]`;
  without, 5 frames. The joined answer text, a fenced code block containing JSON, is identical in
  both runs.

## Revision 2, after the review relayed in co-chat at `877d26a`

- **Lifecycle.** Closing before the first pull closes the source. A distinct iterable and iterator
  are both closed, once each. Cleanup runs in its own shielded task: a caller cancelled while
  waiting gets the cancellation with the upstream error kept as its context, and the cleanup
  carries on; a later close waits for the same task. Close errors never replace the primary
  outcome. `cleanup` is `open`, `closing`, `done`, `failed` or `uncertain` (a close did not finish
  within five seconds; a cooperative deadline, not a hard bound).
- **Forged carrier.** The carrier must hold a random token made when the module loads. A missed
  `attach` therefore fails closed.
- **Registration.** Tested through the installed proxy's `callback_capabilities()` and
  `async_data_generator` with the callback in `litellm.callbacks`: one extra frame, and every
  answer frame byte-identical to the run without a notice.

## Revision 3, after the review relayed in co-chat at `53a00e7`

- **Who closes.** A consumer cancelled between pulls, with nobody calling `aclose()`, leaves the
  source open. That is now stated and tested as the contract, with the framework's own
  try/finally pattern tested alongside. An earlier test that claimed otherwise passed only by
  timing and has been replaced.
- **Cancellation raised by a close.** Treated as a failed close: recorded by name, not propagated,
  the upstream error is raised unchanged and the remaining resource is still closed.
- **Deadline.** The adapter's own wait for a close ends at five seconds even when the close code
  resists cancellation; that close is left behind and the state is `uncertain`, which is terminal.

## Not established

- Nothing here ran in the gateway process, against Open WebUI or in a browser. Whether the
  interface shows the event is source evidence only (co-chat `891475e`).
- That the carrier never reaches the engine in a real request. The library's filter function
  removes it when called directly; the real routing path is for the fake-upstream fixture to show.
- That the carrier set in the pre-call hook reaches the iterator hook in the real proxy. In
  `real_generator_check.py` the request data is handed to the generator directly.
- Retries: each response attempt gets its own event. The laptop's gateway has retries and
  fallbacks set to none, so this is untested in practice.
- Non-streamed answers get no notice.
- How long the added work takes inside a request.
- The proxy's usage accounting when the first stream item is a string. Answer frames were compared;
  accounting was not.

## Run

```
python -m unittest discover -s . -p "test_*.py"
python real_generator_check.py .        # needs LiteLLM installed
```
