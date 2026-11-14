# Scratch ASGI fixture — transport and setup review criteria

2026-11-14. **Source-only review support; no code was executed by this review.** Claude separately reports the scratch integration test starting at `7f704dab` after direct confirmation; results are pending. See the [versioned execution record](../experiments/2026-11-14-scratch-asgi-execution-boundary.json). This document supplies requirements, not private capture code.

## Buffered HTTPX transport is not a disconnect test

HTTPX **0.28.1**, commit `26d48e0634e6ee9cdc0533996db289ce4b430177`, buffers the ASGI response. Its [send handler](https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/httpx/_transports/asgi.py#L148) collects body parts; it [awaits application completion before returning Response](https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/httpx/_transports/asgi.py#L169), then [yields the joined body](https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/httpx/_transports/asgi.py#L55). Its receive handler [waits for response completion before emitting disconnect](https://github.com/encode/httpx/blob/26d48e0634e6ee9cdc0533996db289ce4b430177/httpx/_transports/asgi.py#L137).

Therefore exiting `AsyncClient.stream()` after the first response chunk with this `ASGITransport` does **not** demonstrate interruption between live producer pulls. This transport can still check completed requests, actual response/error serialization and completed SSE framing; keep that scope distinct.

## Deterministic disconnect driver

Use a direct ASGI `receive`/`send` driver around the **actual configured proxy application** for cancellation cases:

1. Deliver the handwritten synthetic request body normally. Afterward gate disconnection on an explicit test event.
2. Observe bounded individual `http.response.body` sends in real time. A barrier in `send` gives the test control between producer pulls, before the application completes.
3. Record requested disconnection, application observation, accepted bodies, already-started pulls and cleanup separately. A test flag saying “closed” does not prove the application observed it or that no operation was already in flight.
4. Record and exercise the declared **HTTP `spec_version`**. ASGI application version 3.0 is a separate value; HTTPX omits HTTP `spec_version` and therefore uses its default 2.0. [The ASGI specification](https://asgi.readthedocs.io/en/stable/specs/www.html) defines the distinction and adds closed-connection send errors in HTTP spec 2.4. Cover receive-driven disconnection and the applicable closed-send `OSError` path, stating the declared version for each.
5. Bound the test and observe adapter terminal state plus underlying-resource closure independently. `uncertain` is not successful release.

Claude reports installed Starlette **1.10.0**. Its exact source path/branch has not been independently inspected here; do not substitute another Starlette release's behavior as installed proof. State which declared ASGI version the fixture tests, and distinguish that simulation from the actual server's scope.

LiteLLM's [response factory prefetches its first chunk](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L1200), before constructing the response wrapper. A pre-first-chunk disconnect and a disconnect between later sends are different cases. Use the real response path, not a replacement fixture response; the [cleanup-path audit](litellm-stream-cleanup-source-audit.md) identifies the intended finalizer chain.

## Keep setup seams explicit

Pinned LiteLLM **1.108.5**, commit `2a61f2114d45016bae77930903e65172cd8e762c`, contains these source seams:

| Setup | Source |
|---|---|
| Actual FastAPI app/lifespan | [proxy_startup_event](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L1919) and [explicit config path](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L1440) |
| Config initialization | [initialize(config=…)](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L9426) uses the real loader; invoking this alone is narrower than full lifespan. |
| Callbacks | [Config callback registration](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L6536) |
| Authentication | [Configured custom-auth import](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L6911) and [actual auth dependency invocation](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/auth/user_api_key_auth.py#L2178) |
| Routing | [Real Router construction](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L7136) |

An HTTP-only ASGI call does not itself demonstrate startup/lifespan execution. Declare whether full lifespan, real explicit config loading or handwritten initialization is used. A narrower setup can still test actual routes/callbacks when accurately labeled; it does not establish untouched production startup. Full lifespan starts ancillary services, so review its scratch/offline configuration before any later authorized execution.

Do not replace the authentication, Router, pre-call dispatcher or generator under test and then call the result a real full-chain check. Use synthetic settings/keys/store, published source pins and the independently authored loopback upstream. Captures must preserve all downstream fields so provider-parameter or internal-carrier leakage is observable.

## Reviewable output

The draft should state source/package pins, chosen setup seam, request/response assertions, declared ASGI versions, deterministic barriers/deadlines and exact cleanup observations. Keep completed-HTTP tests, true disconnect tests, direct-generator checks and browser checks as separate evidence. No browser visibility, native-token bound or margin proof follows from this fixture.
