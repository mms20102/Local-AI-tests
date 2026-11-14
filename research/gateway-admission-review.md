# Gateway admission: scoped independent review and repair checks

2026-11-14. **The existing scoped independent review is complete: 15 passed / 3 real-tokenizer tests skipped at the source below. No restart or live-work clearance.** The test result is coordinator-relayed; this repository session performed the separately labeled static source intake and did not rerun tests or start a second review.

## Published reason-code implementation: focused review pending

Claude’s published reason-code implementation at `be282e303283d3b18bed77ddd51531adfc2ebc4a` (reported local `094b373`) is offline/not loaded. Static intake confirms the fixed reason/type allowlists and unchanged `token_count.py` blob. The author reports 30 admission passes on the laptop, 24 passed / 6 skipped from publication, and installed exception-class checks; **HTTP serialization remains unverified**. [Focused existing-reviewer scope](gateway-reason-codes-review.md) · [intake record](experiments/2026-11-14-gateway-reason-implementation-intake.json). No independent result for this source is confirmed yet, and no duplicate review or acknowledgment was started. The private diff remains unpublished/unapplied. Absent-counter teaching, profile/fallback/margin/final-payload evidence and user-visible omission remain open; no restart clearance.

## Later reported teach rev18: configured failure and absent counter differ

Claude’s [rev18 report](https://github.com/mms20102/Local-AI-tests/blob/da0db284590c718fb74558fc464dff7048ed78ec/research/co-chat.md), local `9514353`, is offline/not loaded and not independently reviewed here. A configured counter that fails or returns an invalid count now withdraws notes, preserves the admitted base and reports `uncounted`; successful over-limit counts remain `no_room`. **No counter configured is a separate unresolved case:** byte-rule notes are still injected with `kept-byte-rule-only`, without a demonstrated bound. Claude plans to ask Mohamed about disabling teaching in that case; no answer is recorded. Profile trust, independent auth/teach loads, exact final-payload evidence, heuristic margin, unpublished report-carrier edits and user-facing omission remain open. Reported publication tests: 109 run / 5 skipped; these are not an independent integration pass.

## Subsequent reported rev17 and coding exploration

Claude’s [631b1ec1 report](https://github.com/mms20102/Local-AI-tests/blob/631b1ec1ce17102f0887481005c02067888ee82f/research/co-chat.md), local `83a6f58`, says the content-type check now precedes the marker check and retained fallback notes carry `byte_only`. The successor is offline/not loaded and has no independent review result recorded here. Labeling fallback is diagnostic disclosure, **not proof of its bound**; the requirement remains to prove it for the supported profile or omit uncertain notes while preserving an admissible base. A separate reason-code-only delta has no published link available in this session; the older full patch is not applied.

The [CODE-Q1 first-pass record](experiments/2026-11-14-codeq1-exploratory-first-pass.json) separately captures Claude’s 12/12 transport-stop and static-structure results. Completion median 34.9 s and first-text median 16.1 s are reported aggregates under download contention. No raw rows/drafts were published or independently assessed here. First-useful-text, semantic correctness and release checks 2/3 remain unmeasured/incomplete. F02 input mutation and E02 uncertainty are the author’s ungraded reading, not established grades.

## Subsequent focused review: revision d8d25e2 / teach rev16

The existing reviewer completed the published successor at **`b111a6479adf3901fce5a1651c6f8e55eec40ee7`**: **gateway 21 passed / 6 skipped; teach 104 passed / 5 skipped offline**. [Record](experiments/2026-11-14-gateway-revision16-independent-offline-review.json). These are coordinator-relayed outcomes, not tests rerun by this repository session. No restart/live-work clearance.

Two reproduced defects: assistant content null/integer/boolean hits the `</think>` membership test before string validation and raises uncaught `TypeError`; failed final counting on the short path retains notes with `uncounted=0`, unlike a successful over-limit count which withdraws them. Validate types first, and either establish the supported byte-fallback bound or omit notes on uncertainty; do not label unverified final counting as successful.

The named profile trusts a launcher report, not the identity of the running engine. Authentication and teaching still independently load settings/counters, and exact final post-hook payload validation has no end-to-end evidence. The 32-token allowance remains heuristic, six real-tokenizer tests are skipped, and two launcher/service-starter report-carrier edits are unpublished. User-visible omission notice remains absent.

Separate candidate work reportedly checked 36 tests with 3 skips and 1,092 role sequences. Its old full patch must not be applied: Claude’s successor already has both role/marker guards. Only remaining reason-code distinctions through `ProxyException` are useful to coordinate; actual LiteLLM serialization is unverified. No candidate was deployed or copied over.

Claude reports the current stack remains gateway `6c12983` / teach rev11, with loading held, and plans static-only CODE-Q1 requests. No results are inferred and this session sends no competing PC traffic.

## Earlier reviewed snapshot: 6c129837

Repository `mms20102/Local-AI-tests`, source commit **`6c1298375d265680313424c36dcecf32a6c4c71f`**, folder [research/gateway-admission](https://github.com/mms20102/Local-AI-tests/tree/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission).

| File | Git blob |
|---|---|
| [README.md](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/README.md) | `47f33ac5c44301e24b9a58edf58a9856f4b9f3c6` |
| [changes-since-baseline.diff](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/changes-since-baseline.diff) | `a35325f4b0b9a4d2dd388ac6f294c20b7ec0905e` |
| [chat_contract.py](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/chat_contract.py) | `e4ab938142b460223887cf16358274ec32792212` |
| [gateway_auth.py](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/gateway_auth.py) | `0739bc4c1b312e8f06d0bf05cce64e76c116c422` |
| [token_count.py](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/token_count.py) | `602cdf3e65afc82bce6e4686d673b464ca8c6c87` |
| [tests/test_token_admission.py](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/tests/test_token_admission.py) | `18c34a6aa1b94002b6a549df16652d6143106ddc` |

The tree/fetch identities were checked. README's SHA-256 values and the advertised exact baseline diff were **not independently recomputed/reconstructed here**. Verify the diff's scope/postimage and distinguish original baseline behavior from introduced changes. The original author/source files have not been changed or copied over.

## Subsequent reported offline changes and planned activity

Claude’s later [87351dea turn](https://github.com/mms20102/Local-AI-tests/blob/87351dea9da795b7214f4ddf05653189b612420b/research/co-chat.md), local `7dd479f`, accepts the four findings and reports teach rev15’s `omitted-uncounted` status plus a later-system-message rejection. **Neither is loaded; this successor is not independently reviewed here.** Do not transfer the 15/3 result from `6c129837` to it. The author reports 106 teach tests with five skips in the published folder, 19 admission passes on the laptop, and “16 run” from the published folder; this record does not infer missing pass/skip details.

Assistant `</think>` history, actual profile binding, exact enriched short-path validation and real-tokenizer boundary tests remain next offline work. User-visible omission disclosure stays open and loading remains held. No additional duplicate review was started.

Claude also reports a user-directed exploratory first pass of about 12 CODE-Q1 requests planned on the current running stack, static grading only, without a restart/window notice. This is a reported plan, not requests or authorization observed by this session. Avoid competing PC traffic; static outcomes are not semantic/release passes. No results are inferred.

## Decision and runtime boundaries

Claude [relays Mohamed's words "Yes to all"](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/co-chat.md) for source publication, the primary numerical targets, and one restart to load teach rev14 **after the counter review**. These are attributed conversation reports, not independent authorization for this repository session to operate the PC.

The source is now visibly published. Claude reports the counter active since window 7; exact loaded gateway identity remains unverified here. Teach rev14 is reported not loaded. No runtime window is open in the checked shared log; loading remains held with the counter review findings unresolved; no restart clearance is given. User-visible omission notice and accurate counter-unavailable/no-room status remain open. Windows Sandbox is reportedly deferred; generated-code execution is not enabled.

## What the intake read actually establishes

- [`load_counter`](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/token_count.py#L49-L69) reads a tokenizer file, checks its SHA-256 at load, constructs an in-memory tokenizer and returns a counting closure. No per-request file hash or engine/profile identity check is shown there. Startup-only pinning is not itself evidence of a changed running model; assess how runtime/profile consistency is established.
- [`render`](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/token_count.py#L34-L46) manually constructs frames and an empty thinking block. Claims that a longer form or source-derived treatment cannot undercount need a justified native-tokenizer/render comparison, not character length alone.
- [`validate_chat`](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/chat_contract.py#L103-L134) uses bytes first and invokes token counting only when that route rejects; it adds `TOKEN_MARGIN = 32` to prompt count plus reserved output. The margin is a fixed constant, not a proven error bound.
- [The custom-auth adapter](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission/gateway_auth.py#L14-L58) loads the counter at startup and passes it into request validation. This does not by itself establish the final post-hook payload or the complete response/status path.
- The advertised test result is **18 total with 3 tokenizer-dependent skips** from the publication and **18 passing on the laptop**, as Claude reports. This session ran none. Treat render/admission tests separately from native parity, middleware integration, live identity and resource behavior.

## Existing review outcome and actionable repairs

The review confirms that tokenizer **bytes** are pinned but the served engine/rendering **profile** is not bound. The 32-token allowance remains heuristic. Later system-message and assistant-history `</think>` shapes are accepted despite the renderer mismatch/unsupported-profile questions, and final post-hook validation with shared counter/profile evidence is not demonstrated.

Focused offline follow-up: bind and validate the actual supported engine/renderer/tokenizer/context/thinking profile; reject unsupported shapes before either route; validate the exact final enriched request with the same counter/profile and full output reservation; and exercise below/equal/over boundaries. A model alias, positive integer count, cached tokenizer hash or a few matching live counts is not a substitute for that evidence. User-visible omission disclosure and distinct counter-unavailable/no-room status remain open. No patch, probe or deployment was performed here.

## Review and repair acceptance matrix

| Area | Concrete check / acceptance evidence |
|---|---|
| Reproducibility and baseline | Match source identities, run the available offline tests, report pass/skip counts and missing artifacts. Confirm the baseline diff corresponds to the published postimage; do not infer it from its label. No model load or live request is needed. |
| Byte route and fallback | Prove or refute the claimed conservative bound for the **complete accepted serialization**, configured overheads/reserve/message counts and output allowance. Separate preservation of previous behavior from proof that behavior bounds native input. |
| Counter identity/freshness | Determine what the captured tokenizer/hash guarantees and what it does not bind: actual native tokenizer, engine/renderer version, context, thinking/profile and later model changes. A plausible stale positive count must not be called validated merely because its type is an integer. |
| Renderer/profile agreement | Compare to the pinned native 2.0 renderer/intake. Check later/multiple system turns, assistant-history `</think>`, Unicode/combining marks/whitespace/raw special-token text and the accepted role/content rules. Identify rejected profiles explicitly; do not add new tool/media support. |
| Reservation and boundaries | Check below/equal/over prompt-plus-full-output boundaries, invalid/error/missing counts and no mutation/silent truncation. Establish what the 32-token allowance covers or leave it unproven. Existing matching samples are finite evidence, not a universal bound. |
| Teaching integration | Trace authentication/admission versus teaching order and the final enriched candidate. Assess short byte path and long counter path separately. Keep scoped rev14 repair pass distinct from end-to-end counter validity. |
| Failure/status/UI | Distinguish unavailable/invalid counting from genuine no-room, and separate local logging from a message Mohamed can actually see. Do not mark user disclosure complete from an omitted count in a log. |
| Bounded operation | Assess counter/read/serialization work and error propagation within the existing request limits. Use synthetic/disposable offline fixtures, preserving credentials, real stores and private logs. |

If the exact laptop tokenizer is unavailable, preserve the skips and say which conclusions remain unverified; do not install/download weights or use the private benchmark to fill the gap. No deployment approval follows from a test count.

## Result and future verification boundaries

Any follow-up review should identify the changed source, tests actually run/skipped, reproduced cases, verified claims versus unknowns, and a scoped integration recommendation. Continue with the existing reviewer and avoid duplicate testing. Preserve the previous source and offline repair evidence. No restart, hook/configuration change, live probe, repository merge/PR closure, generated-code execution or rejected-component publication retry is requested.

The existing review result is **15 passed / 3 skipped**, with the exact laptop tokenizer unavailable for the skipped tests. It does not establish native parity, final middleware order or full integration, and it clears no restart. No new review is requested by this record.
