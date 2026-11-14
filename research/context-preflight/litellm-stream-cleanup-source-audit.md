# LiteLLM streaming cleanup path — pinned source audit

2026-11-14. Read-only tagged-source inspection of **LiteLLM v1.108.5**, commit `2a61f2114d45016bae77930903e65172cd8e762c`, alongside adapter rev3 `1ea5c6f60b6124f24597e5347a57629b37133529`. No ASGI test, installed-package execution, PC request or runtime change was performed by this audit.

## What the standard response path does

| Boundary | Source evidence |
|---|---|
| Chat route to generator | [Route](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L12330) supplies `select_data_generator`; [common processing](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L3099) passes its result to the response factory. |
| Response retains the generator | [create_response](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L1296) retains the upstream generator separately from the body wrapper. |
| Consumer disconnect between sends | [`_UpstreamClosingStreamingResponse.__call__`](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L1007) explicitly closes both body iterator and retained generator in a shielded `finally`. |
| Generator to callback wrappers | [GeneratorExit handling](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/proxy_server.py#L10218) closes guarded layers. [ProxyLogging](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L4647) and [layer close helper](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L4907) propagate cleanup. |
| Leaf callback result | [Enrichment wrapper finally](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L3332) checks the returned object for the closable-iterator protocol and awaits `aclose()`. This supports a leaf returning rev3's `StatusStream` object. |

This supports the **explicit caller-close contract on this standard source path**; it does not prove that a deployed request actually takes the path or that all finalizers finish. It is stronger evidence than a handwritten consumer `finally` test, but remains source evidence.

A [separate finalizer](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L4302) also closes the original model response. Consequently global “exactly one close” is not the framework contract: source closure must tolerate multiple layers' cleanup.

A [pre-first-chunk disconnect monitor](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L1046) also cancels a pending fetch and closes its generator. Cancellation during a backend pull and disconnect between pulls exercise different boundaries.

## Remaining targeted integration check

Use the **actual ASGI response**, synthetic model chunks and the existing fake upstream. Block `send` after a yielded chunk, disconnect/cancel between pulls, and observe that the real closure cascade reaches the adapter and original model source. Also cover pre-first-chunk disconnect and cancellation during a backend pull. Do not substitute direct generator iteration or a handwritten try/finally consumer for this test.

Observe adapter terminal cleanup state and original-resource closure separately. `uncertain` means cleanup is not confirmed; the framework currently does not inspect that custom state. Repeated cancellation, cleanup errors, event-loop unresponsiveness or process termination can invalidate successful closure assumptions. The deadline assumes a responsive loop and cannot force arbitrary close code to terminate.

This test should reuse the existing receiver rather than create a second one. Carrier survival/exclusion and actual proxy routing remain separate assertions within that fixture; browser visibility and nonstream disclosure remain later UI checks. No source audit or unit-test pass authorizes loading the prototype.
