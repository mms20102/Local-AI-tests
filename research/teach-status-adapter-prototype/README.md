# Teach status adapter: offline prototype

Published by Claude (laptop session) on 2026-11-14 for review. **Not loaded, not registered, not
part of the running gateway.** No gateway, hook or configuration file on the laptop was changed
for it. It follows the handoff in co-chat at `07db9cc`.

| File | What it is |
|---|---|
| `teach_status_core.py` | The tested core from branch `codex/teach-status-core-20261114`, byte-identical (git blob `c07df5220f2064163ed5d11d035f6382fc4a9191`). Not modified. |
| `teach_status_adapter.py` | The adapter: maps teach revision 18's final result to a decision, carries it in request data, and wraps the response stream. |
| `test_teach_status_adapter.py` | 24 tests on handwritten fake streams. Three need the LiteLLM library and are skipped without it. |
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
3. `stream_with_status(response, request_data)`: the body for an
   `async_post_call_streaming_iterator_hook` override on the registered leaf class. It yields one
   JSON status event as text with no `data:` prefix, then every model chunk, the same objects in
   the same order. It closes the model stream once on completion, failure, client disconnect or
   task cancellation.

The locale is an explicit argument, `en` or `ar`. Nothing here chooses it.

## Evidence (measured on the laptop, offline)

- 24 tests pass with the gateway's own Python and LiteLLM 1.108.5; 21 pass and 3 are skipped with
  a Python that has no LiteLLM.
- With the installed library's own functions: the carrier key is classified as library-owned and
  removed by `filter_out_litellm_params`; the event is framed as one `data:` line that parses; the
  override is found on the leaf class and not on a subclass that only inherits it.
- `real_generator_check.py`, through the installed `proxy_server.async_data_generator` with the
  adapter registered as a callback and a fake stream of real `ModelResponseStream` chunks:
  with a notice, 6 frames: the status event (no `choices` key), four answer chunks, `[DONE]`;
  without, 5 frames. The joined answer text, a fenced code block containing JSON, is identical in
  both runs.

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

## Run

```
python -m unittest discover -s . -p "test_*.py"
python real_generator_check.py .        # needs LiteLLM installed
```
