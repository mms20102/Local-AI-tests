# Focused check: Claude's reason-code implementation

2026-11-14. **Static intake complete; focused verification by the existing reviewer recommended, not yet confirmed.** No second review or code execution was started by this repository session.

Source: [`be282e303283d3b18bed77ddd51531adfc2ebc4a`](https://github.com/mms20102/Local-AI-tests/tree/be282e303283d3b18bed77ddd51531adfc2ebc4a/research/gateway-admission), reported laptop commit `094b373`. [Intake record](experiments/2026-11-14-gateway-reason-implementation-intake.json).

## Published progress and its scope

Claude reports implementing the shared description independently, without the private diff, offline and **not loaded**. The published source contains the four fixed contract reasons and their fixed `ProxyException.type` mappings. Git blob comparison shows changes to the contract/auth/tests plus README/baseline diff; `token_count.py` is unchanged from the preceding checkpoint. This establishes a narrow intake scope, not a behavior or runtime pass.

Author-reported tests: nine counter cases, **30 admission passes on the laptop**, **24 passed / 6 skipped from the publication**, and project suite 239. The installed LiteLLM exception class was reportedly exercised on the laptop; **HTTP serialization was not**. This session did not rerun those tests. Keep these counts separate from the privately supplied candidate's different test suite.

## Focus for the existing independent reviewer

Use the exact published snapshot and check the error-classification delta, retaining previously identified integration limits rather than reopening the entire project:

1. Missing, raising and invalid counters are distinguished from a successful positive count that exceeds the configured budget. Include bool/nonpositive/noninteger outputs; do not imply the counter's count or margin is thereby a proven native bound.
2. Only allowlisted reasons propagate to fixed proxy types. Unknown reasons preserve generic policy behavior; exception details, request text, credentials and environment values do not leak into messages/metadata.
3. Existing HTTP statuses, route/auth/profile/content guards, output reservation, token arithmetic and request immutability remain intact. Unsupported/malformed requests should fail before counter calls.
4. Check the actual contract-to-auth propagation path with available offline fixtures, and distinguish stubs, installed exception-class checks and HTTP response serialization. If the real framework path is unavailable, report that limit explicitly.
5. Run the available tests and preserve all six native-tokenizer skips unless the exact artifact is legitimately available. Record results for this source, not the parallel private candidate.

No model/server/PC request, restart, real store, generated-code execution or private-diff publication/application is requested. The original private artifact remains untouched. The absent-counter teaching decision, byte/profile/margin proof, final enriched-payload evidence and omission UI remain open; no restart or integration clearance follows from this intake.
