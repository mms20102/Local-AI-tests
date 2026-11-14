# Streaming teaching-status adapter: focused review

## Latest revision-2 check — repair required

The published successor is [`82a560519bcb72c10482dc3d779184e10f85b161`](https://github.com/mms20102/Local-AI-tests/tree/82a560519bcb72c10482dc3d779184e10f85b161/research/teach-status-adapter-prototype). The existing independent initial check reports **31 passed / 1 failed / 5 LiteLLM skips**. Claude separately reports 37 installed-library passes and 32 passed / 5 skipped without it; these reports must not be substituted for the failing independent observation.

The failing existing `test_task_cancellation_closes_the_source` leaves **`source.closed == 0`** when cancellation occurs in the consumer body between pulls. The new `test_cancelled_consumer_does_not_abandon_cleanup` explicitly calls `await stream.aclose()` afterward; it does not establish automatic cleanup of a cancelled consumer. The caller/framework responsibility must be explicit and exercised at the actual integration seam.

A second reproduced case has source `aclose()` raise `CancelledError`, masking the upstream `RuntimeError` and leaving cleanup incomplete. Distinguish cancellation of cleanup itself from cancellation of the waiting consumer; test terminal state, primary-outcome/context policy, subsequent close and the remaining resource.

Pre-first-pull and ordinary distinct source/iterator closure **are repaired in the reviewed paths**. The shielded shared cleanup and states are structural progress, not a complete lifecycle pass. The new source also uses `asyncio.wait_for`; cancellation-resistant close code can extend waiting beyond its nominal timeout, so the uncertain-state/deadline contract needs a specific test.

Five files are now published, including [`real_generator_check.py`](https://github.com/mms20102/Local-AI-tests/blob/82a560519bcb72c10482dc3d779184e10f85b161/research/teach-status-adapter-prototype/real_generator_check.py). The unchanged core remains `c07df52`. The generator fixture supplies data directly and modifies callback globals in its standalone process; it is not actual auth/pre-call/routing or browser evidence. The process-random carrier token is defense in depth, not request binding or provider-exclusion proof.

Findings were [relayed once](https://github.com/mms20102/Local-AI-tests/commit/53a00e7faa62b8fe6281c14f52b8e797b0ec4214). Full independent details remain to follow at this checkpoint; no duplicate receiver, PC/model traffic or runtime action was started here. The source/review details below describe **revision 1** and remain historical where superseded.

2026-11-14. Source [`f57f2958342d43b5687bf43ca27017c0e8b910e6`](https://github.com/mms20102/Local-AI-tests/tree/f57f2958342d43b5687bf43ca27017c0e8b910e6/research/teach-status-adapter-prototype). **Offline prototype, not registered or loaded.** [Evidence record](experiments/2026-11-14-teach-status-adapter-initial-review.json).

## Evidence levels

Claude reports 24 tests passing with installed LiteLLM 1.108.5, or 21 passed / 3 skipped without it. The coordinator's independent initial review reports **21 passed / 3 LiteLLM skips**, plus the cleanup counterexamples below. This repository session separately read the source; it did not execute Python tests. The full independent report was not yet received at this checkpoint.

Static intake confirms use of the unchanged core, direct mapping from the final snapshot values, strict primitive-carrier shape and fixed status text. The carrier contains no note text, entry IDs or fingerprint. This is useful bounded component progress, not a complete framework pass.

## Reproduced synthetic lifecycle gaps

1. Closing the public wrapper before its first pull can leave the supplied source unclosed.
2. A distinct iterable and closable iterator only close the iterator, despite the broader source-close guarantee.
3. Cancellation during source `aclose()` can replace an upstream error with cancellation and leave cleanup unfinished.

The [source close path](https://github.com/mms20102/Local-AI-tests/blob/f57f2958342d43b5687bf43ca27017c0e8b910e6/research/teach-status-adapter-prototype/teach_status_adapter.py#L149) sets the closed flag before awaiting cleanup and swallows ordinary close exceptions. A subsequent cleanup call can therefore return without confirming resource release. Existing source tests use immediate close operations rather than these forced interleavings.

The repair needs an explicit contract: which layer releases each resource, how unstarted wrappers behave, primary error/cancellation priority, and how completed versus uncertain cleanup is reported. Add delayed/failing close, cancellation during close, distinct iterable/iterator and pre-first-pull cases. Do not promise hard deadlines for arbitrary cancellation-resistant code or infer a live leak from these synthetic counterexamples.

The findings were [relayed once](https://github.com/mms20102/Local-AI-tests/commit/877d26af427af470f712ea3df3aba885ac3baec0). Use the existing reviewer for the focused successor rather than a parallel receiver or another broad review.

## Trust and framework boundaries

`notice_for` alone accepts a well-formed forged carrier. Protection depends on trusted `attach` replacing incoming carrier data on every applicable path, followed by actual provider stripping. This does not mean the current strict gateway accepts that client field; the full route remains untested.

The published leaf test checks the class dictionary and direct invocation, not real callback registration. Pinned source suggests the internal prefix is excluded by normal parameter filtering, but a direct filter-function check does not establish real outbound bodies.

Mixed string/model chunks also take a different [served-output-correction branch](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/litellm_core_utils/served_output_texts.py#L110). Check accounting separately from answer-text equality; this source observation does not establish incorrect billing.

## Generator evidence and remaining work

Claude reports a direct `async_data_generator` experiment: six frames with notice versus five without, and identical joined fenced-code/JSON answer text. The request data was supplied directly, not propagated through auth/pre-call/routing. The referenced `real_generator_check.py` is **absent from the pinned four-file directory**; its result is an author report, not an inspectable/reproduced harness here. A sanitized standalone fixture would make that result reviewable.

Reuse the separate synthetic capture work for a future **actual LiteLLM proxy** boundary test. Its receiver/pure-function composition alone cannot prove actual dispatcher, routing, carrier association/exclusion or HTTP exception serialization. That test still does not establish browser visibility. Nonstream disclosure, retries, accounting and latency remain separate.

No prototype source was modified by this review, and no laptop/engine request, configuration change, registration, restart or real-store action occurred.
