# Final request and running-profile evidence plan

2026-11-14. **Offline source-based plan, not an executed integration test.** Collaborating read-only research checked the published snapshot `8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897`. No PC/model request, runtime change, real-store action or new generated-code execution occurred.

## Next bounded test

Run a disposable gateway instance against a **handwritten fake upstream HTTP endpoint** with synthetic requests and a disposable note store. Observe what the endpoint actually receives. Comparing the teach callback's return dictionary alone does not establish what the engine receives.

Do not point this fixture at the live model, import private gateway credentials or mount the user note store. Use separate endpoints and synthetic keys. Preparing this fixture does not authorize launching another laptop stack or reusing the rejected benchmark-publication path.

## Source seams that the test must cross

- [Gateway original admission](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/gateway-admission/gateway_auth.py#L14): environment-derived limits and counter are loaded at lines 14–17; the original parsed body is validated at lines 53–58.
- [Teach initialization and return](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/teach-store/teach_hook.py#L167): settings.json and another counter are independently loaded at lines 167–175. The transformed data is returned at lines 179–185. Sharing the loader function does not mean sharing one immutable configuration instance.
- [Same-store snapshot](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/teach-store/teach_hook.py#L61): preserve the entries/fingerprint/invalid-count snapshot used for the final decision, rather than rereading the store for response status.
- [Candidate admission](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/teach-store/teach_store.py#L768): count fit, count failure, overflow and no-counter byte retention are distinct outcomes.
- [Profile loader](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/gateway-admission/token_count.py#L52): checks a launcher report and files; it does not identify the process currently serving the endpoint.

LiteLLM **v1.108.5** resolves to source `2a61f2114d45016bae77930903e65172cd8e762c`. Its [callback dispatcher](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/utils.py#L3078) adopts callback results. [Later processing](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L2461) and [routing](https://github.com/BerriAI/litellm/blob/2a61f2114d45016bae77930903e65172cd8e762c/litellm/proxy/common_request_processing.py#L2846) remain after the pre-call stage. These are tagged-source findings, not installed-wheel or laptop-path verification.

## Evidence to record

Use one immutable limits/profile/counter snapshot for original admission and teaching where feasible; otherwise explicitly compare their digests and reject mismatched configuration in the fixture. Record the counting mode and source revisions. Internal evidence must not be accidentally serialized as a provider request field.

At the receiving endpoint compare parsed values of ordered message roles and **exact content**, requested output allowance, temperature, stream flag and the declared model mapping. JSON key order and insignificant whitespace need not match. The counted enriched candidate must be the one captured downstream; callback success alone is insufficient.

Keep status associated with the same final candidate/store snapshot and response attempt. A successful HTTP response must not relabel byte-only applied notes as token-verified. Keep real user request/note text and their hashes out of published evidence; handwritten fixtures can be published.

## Synthetic cases

Cover empty store; short request with selected notes; Arabic/history; valid overflow and note withdrawal; configured-counter failure; no-counter retained byte notes; concurrent store replacement; both streaming/nonstreaming; unsupported and malformed requests. Every refused request must yield **zero upstream captures**.

Exercise real LiteLLM HTTP error serialization as well as final successful payloads in this disposable test. The reason-code component pass used a stub exception and does not cover that boundary. Do not reuse a shared mutable global status variable across parallel requests/retries.

## Later coordinated laptop evidence

For a live observation, associate the listening endpoint with the serving process's creation time, executable identity and arguments; record the loaded gateway/callback/package source evidence and limits/profile digest. A matching file on disk or a launcher report is weaker than proof that the serving process loaded it. State the evidence level when stronger attribution is unavailable.

Fake-upstream equality does not prove native tokenizer parity, a universal 32-token margin or the byte bound. The retained fallback and heuristic margin are Claude-relayed operating choices; keep their limits explicit. Native usage comparisons remain a separate scoped observation, and a restart/feature enablement follows the applicable authorization and coordination rather than this document.

## Read-only Sandbox prerequisite check, separate from deployment

Claude reports Windows 11 Pro/build 26300, virtualization active and no Sandbox executable. Treat executable absence as an observation. A candidate feature-state query is:

```powershell
Get-WindowsOptionalFeature -Online -FeatureName "Containers-DisposableClientVM" |
    Select-Object FeatureName, State
```

This query is proposed, **not run here**. If the environment requires elevation, report that boundary rather than enabling a feature as part of the check. [Microsoft's query documentation](https://learn.microsoft.com/en-us/powershell/module/dism/get-windowsoptionalfeature?view=windowsserver2025-ps) describes inspecting the running image; [the Sandbox installation page](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install) identifies this feature and its prerequisites.

The documented 4 GB minimum is a system prerequisite, not evidence that a particular concurrent workload fits or fails. One free-memory sample does not settle concurrent operation. Sequential generation then isolated grading is a candidate to evaluate with physical, commit and GPU admission, rather than a necessity established by the current sample. No feature enablement, reboot or code execution follows from this plan.
