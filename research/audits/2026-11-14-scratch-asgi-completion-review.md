# Scratch proxy/ASGI completion: artifact and source review

Review checkpoint: **2026-11-14 21:32 UTC**. Producer artifact label: **2026-11-15**, preserved as published. Source [`573fa44b`](https://github.com/mms20102/Local-AI-tests/tree/573fa44bcc46e54940fc3243dcf35a8ac18effb8/research/experiments-claude/2026-11-15-scratch-asgi).

**Artifact arithmetic and source inspection completed; no independent rerun.** Claude's reported execution is useful bounded integration evidence. It is not a five-for-five disconnect-success result, a live deployment check or a coding-quality score. [Structured intake](../experiments/2026-11-14-scratch-asgi-completion-review.json).

## What the saved results establish

The three JSON files contain **27 final scenario groups**, not 27 HTTP requests: 12 bound-counter completed groups, 10 no-counter completed groups, and five direct-driver groups. All saved group results are `pass`, matching the reported count fields. There is no separate skipped-count field; the completion reports no skips.

Stage 2 records 13 upstream captures in bound mode and 11 without the counter. Its source uses the actual proxy lifespan/config loader, configured custom auth/Router/callback and installed client HTTP to a fixed-answer upstream. Selected-note and Arabic cases compare exact ordered message values; output reservation, notice framing, byte-only/uncounted/no-room behavior and expected request refusals have explicit assertions. The streamed notice case compares the remaining response body byte-for-byte with its no-notice baseline. This is progress beyond pure-function composition or directly supplying data to the generator.

The captured raw request/response bodies were retained in memory, **not published in the result JSONs**. This review can inspect the assertions and recompute counts, but cannot independently recompute every observed wire comparison from retained raw rows. The expected selected-note candidate is built separately with the same helper; an actual callback counter-call trace is not saved.

Four concurrent responses are checked for expected notice/no-notice counts `[1,0,1,0]`. This demonstrates the selected distinction in that fixture, not unique retry-attempt tracing. Retries/fallbacks are disabled. `no_internal_keys` is called at selected assertion sites rather than globally across every capture, so the blanket “every capture” wording exceeds the independently inspectable assertion coverage. No leakage was observed by this review.

## Five direct-driver groups have different meanings

| Group | Reported observation | Bounded conclusion |
|---|---|---|
| Baseline | Normal return, adapter done, upstream completed | Normal completion/cleanup |
| Disconnect between pulls, spec 2.3 | Disconnect delivered, parked send cancelled, adapter done, upstream closed early | Requested midstream behavior succeeded as reported |
| Disconnect during pull, spec 2.3 | Disconnect delivered, adapter done, upstream closed early | Requested midstream behavior succeeded as reported |
| Before first event | No disconnect delivered; HTTP 408; zero adapter streams; eventual upstream close | Prompt cancellation **not established** |
| Closed-send error, spec 2.4 | Adapter/upstream cleanup; app raised missing-`prisma` import error; next request works | Cleanup evidence, **not clean error handling** |

The pre-first [test assertions](https://github.com/mms20102/Local-AI-tests/blob/573fa44bcc46e54940fc3243dcf35a8ac18effb8/research/experiments-claude/2026-11-15-scratch-asgi/stage3.py#L211) permit zero adapter streams and require eventual return/closure, not observed disconnect or a cancellation deadline. Its `30.5` timing is calculated after an added 0.5-second wait and a recovery request; it is not an isolated application-return duration. The spec-2.4 [assertions](https://github.com/mms20102/Local-AI-tests/blob/573fa44bcc46e54940fc3243dcf35a8ac18effb8/research/experiments-claude/2026-11-15-scratch-asgi/stage3.py#L247) likewise do not require a clean application return. An already-sent status 200 is not a successfully completed response.

## Why the pre-first wait can precede the later disconnect monitor

Pinned LiteLLM 1.108.5 source, `2a61f2114d45016bae77930903e65172cd8e762c`:

- [Common processing](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L2903) awaits the router/provider before `create_response`; monitoring during this phase depends on `cancel_on_disconnect`, default false. The scratch configuration does not enable it.
- [Router completion](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/router.py#L4164) explicitly calls [the first-chunk reader](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/router.py#L760) before returning the stream.
- The [later response-factory monitor](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L1200) cannot monitor a wait that has not yet reached it.

This is a tagged-source explanation consistent with the fixture. It is not an installed stack trace or proof of the live gateway's behavior at a 120-second timeout. A scratch-only `cancel_on_disconnect` comparison would be a separate hypothesis test, not a live setting change approved by this audit.

## Why the spec-2.4 error can reach Prisma

[Starlette 1.10.0](https://github.com/Kludex/starlette/blob/8aa828ceaff764a2e57932fb42fdf105a47c4c83/starlette/responses.py#L270) maps failed sends to `ClientDisconnect`. LiteLLM's [global exception handler](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L2297) invokes database-error classification, which reaches [an unguarded `import prisma`](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/db/exception_handler.py#L180). That matches the published error tail. Installed source hashes were not supplied; this is source correspondence, not independent installed-file attribution.

Tagged Uvicorn 0.54.0 [h11](https://github.com/Kludex/uvicorn/blob/3eb9a9ab9af69005c687728097461c1fd2a95db9/uvicorn/protocols/http/h11_impl.py#L210) and [httptools](https://github.com/Kludex/uvicorn/blob/3eb9a9ab9af69005c687728097461c1fd2a95db9/uvicorn/protocols/http/httptools_impl.py#L228) declare spec 2.3. This corroborates the reported version's scope; it is not a captured scope from the running service. No dependency installation, runtime upgrade or patch follows from this finding.

## Fresh-copy setup and traffic qualifications

There is a reproducibility gap in the published recipe. Both stages import the candidate **before** `write_scratch_files()`. The candidate immediately constructs its hook, whose initializer reads copied-module `ROOT/settings.json`. The launcher sets environment values but does not create that file. With only the documented copies and no preexisting file, initialization can fail before the writer runs; with an old file, the callback can retain earlier limits despite the later rewrite. This static finding does not disprove the reported runs or establish their initial settings. Bootstrap must be supplied or reordered for a reproducible fresh copy.

The connection guard is installed after candidate/dependency imports. It permits loopback connections except the three live ports; it is not an OS network sandbox or an owned-port-only firewall. Saved guarded-interval port sets contain only the declared upstream port and no refused connects. This does not cover import-time traffic, DNS/UDP or all file access. No actual leak is alleged.

The fixture reports no live-service calls, but the operator also reports a **post-run live health check returning 200**. Treat that as a separate read-only probe; do not claim zero live traffic across the entire operator session. Scratch deletion, process/port cleanup and memory samples remain author observations, not independently reproduced here.

Browser display, streamed accounting, native tokenizer/margin proof, quiet-run latency and live loaded identity remain unverified. The earlier fixture-development failures are disclosed; only final result snapshots are published, so repeated passes are author reports rather than independently retained repeat datasets.
