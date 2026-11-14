# Align context admission and teaching-note budgets

2026-11-14. **Source analysis and collaborative remediation proposal only.** No gateway/hook change, model request, store edit or PC operation is made or authorized here. The gateway source remains unpublished and has not been sought or inspected. Claude's explanation of gateway ordering is an author report.

## Revision 13 — scoped offline review, not cleared

The independent review pinned at `cb987269300198b8b00adfca02c198d4b55cd34e` reports **97 passed / 5 skipped**. The earlier oversized-note omission and ordinary missing-field isolation improved, but two cases remain reproduced: a second diagnostic store read can mix a new invalid-entry count with an old fingerprint, and lone-surrogate text can pass validation then suppress valid neighboring notes during strict UTF-8 rendering. [Review record](../experiments/2026-11-14-teach-rev13-independent-offline-review.json).

The constructive next checks are one captured snapshot for entries/counts/fingerprint and per-entry renderability validation, with deterministic disposable fixtures. The source is reported not loaded. User-facing omission disclosure, real-counter/profile evidence and uncertainty remain open; passing offline tests do not clear integration. This session did not repeat the review or edit source/runtime.

## Revision 12 — final scoped offline review, not cleared

Claude [reports revision 12](https://github.com/mms20102/Local-AI-tests/blob/eaf6016953fc5b6578ed707afef238fceca034b0/research/co-chat.md) published from local `f939b54`, explicitly **not loaded**. The existing independent reviewer completed the final scoped offline review: **92 passed / 5 skipped** at that pinned source. **Token-budget integration is not cleared**; this session does not duplicate the review. [Final review record](../experiments/2026-11-14-teach-rev12-review-pending.json) (existing path retained for link compatibility).

The reported long path counts the whole enriched candidate after byte-route failure and drops whole notes with bounded attempts. The short path still uses the byte rule and does not call the counter. The 32-token allowance is unproven and the actual counter source is unpublished; later-system/history-marker edge cases remain unresolved. The real-tokenizer examples reported are English; Arabic-with-notes uses a stand-in counter. No live nonempty-note result or deployment is established.

Claude relays Mohamed's policy as **answer with notes left out when they do not fit**. The current omission report is **gateway-log-only**; the user-facing notice required by the design is still missing. A single omitted count also cannot distinguish no room from unavailable counting. Final review confirms the previously relayed reproductions: a relevant **294-character note** excluded by the **320-byte wrapped cap** reports `omitted=0` because `wanted` was already budget-filtered; malformed `when` metadata beside a valid note returns the original request / unknown fingerprint / omitted=0. These mask distinct reasons for missing notes. Preserve the relevant eligible set before budget selection and assess per-entry validation/status reporting. These are reviewer-reported cases, not executions by this session. Stand-in tests validate complete-candidate construction/counting calls and bounded note dropping, not real token counts or the installed renderer/profile. Missing counters fail closed for new widening, but a plausible stale positive count is indistinguishable from a valid one at this interface; no overflow was reproduced. The actual counter source, profile identity, uncertainty allowance and legacy byte-bound proof remain unverified. Do not mark the integration/teaching acceptance check complete from implementation or passing-test counts.

## The concrete gap at revision 11

Window 7 reportedly admitted requests using the token counter, while the teaching hook still uses its earlier byte-based budget. Published teach source at `829d3228438034b3126a2eac419517d1760db239` corroborates the latter mechanism:

- [`request_units`](https://github.com/mms20102/Local-AI-tests/blob/829d3228438034b3126a2eac419517d1760db239/research/teach-store/teach_store.py#L661-L664) sums UTF-8 content bytes, message overhead and reserved output.
- [Remaining room / selection](https://github.com/mms20102/Local-AI-tests/blob/829d3228438034b3126a2eac419517d1760db239/research/teach-store/teach_store.py#L688-L697) subtracts those units and the policy addition from `context_tokens`; an empty selection returns the original messages.
- [Final defensive check](https://github.com/mms20102/Local-AI-tests/blob/829d3228438034b3126a2eac419517d1760db239/research/teach-store/teach_store.py#L698-L708) uses the same arithmetic. [The callback](https://github.com/mms20102/Local-AI-tests/blob/829d3228438034b3126a2eac419517d1760db239/research/teach-store/teach_hook.py#L42-L59) returns unchanged data when nothing is selected.

Conditionally on the reported 2,048 limit and this code path, a long request with 7,417 content bytes already has negative byte-room before any note is added, even though its reported prompt count is 1,641. Relevant notes cannot be selected by this path. This is a **teachability/integration limitation**, not evidence that this path caused an overflow.

The live probes reportedly had no active notes, so they do not themselves exercise nonempty-note behavior. The exact loaded rev11 identity and full gateway/middleware ordering are not independently verified here.

## Proposed common contract

Use the **same supported serialization/count evidence and output reservation** for note selection and final admission. Treat an enriched request as a complete candidate, not as an independently estimated note cost.

1. Validate the supported request profile and preserve its desired output allowance. Snapshot the store once and select/rank whole notes deterministically, preserving existing data-role boundaries and idempotence.
2. Build a complete candidate containing the actual note block, delimiters, any policy/system insertion, message frames, history and nonthinking prefix. Count that final rendered candidate with pinned profile evidence. Do not simply add separately tokenized note counts; boundaries and wrappers matter.
3. Retain only a candidate whose prompt count plus full output reservation and a justified uncertainty allowance fits. Recount after any note/subset change. Bound the number/size of candidate attempts and account for counter/read/log latency.
4. Apply one final admission decision to exactly the candidate that will be sent. Use explicit statuses for applied notes, no relevant notes, notes omitted for budget, unsupported counting and store unavailability. Do not log note text or arbitrary malformed IDs.
5. When optional notes do not fit, propose preserving the original question/history and disclosing that saved preferences were omitted. If Mohamed wants particular notes always applied, a no-room request must instead ask for a shorter conversation or another explicit choice. **Claude later relays Mohamed's choice to answer with notes left out; rev12's log-only notice still leaves the user-facing disclosure gap. This document implements no policy.**
6. Unknown or unsupported counting must not enlarge acceptance on a guessed margin. A byte fallback requires its own proof for the entire final serialization; an average ratio or an unvalidated 32-token allowance is not that proof. Do not silently drop history or shrink the answer allowance.

A short UI message explaining that preferences were not applied helps the user make a decision. Detailed diagnostic hashes/implementation terms belong in bounded local evidence, not the normal conversation.

## Offline acceptance matrix before a proposed live change

| Case | Expected design property |
|---|---|
| Empty store / no matching notes | Original payload remains unchanged; status distinguishes the reason. |
| Base request passes token admission but fails old byte budget; a small note fits in real tokens | Note can be included by the shared token budget, with actual wrapper/policy costs counted. |
| Same long request; notes would exceed context | Full requested output and original question/history remain protected; optional omission is disclosed, or a required-note policy gives a clear refusal. |
| Arabic, combining marks, whitespace, raw special-token text and assistant history | Exact supported renderer/profile rules are checked; source-derived bounds and observed parity are labeled separately. Two Arabic samples do not establish every case. |
| Multiple/later system messages or nontext/media/extra fields | Claude now reports later system turns are accepted by the gateway but refused downstream, while media/extra fields are rejected. A candidate gateway validation correction should give a clear local refusal for the unsupported role order; no change is made here. |
| Assistant history containing `</think>` | Claude reports this is accepted, with different renderer treatment inferred from source. The claimed direction/size of count differences is untested; do not use it as a proven error bound. |
| Tools | Preserve the reported current refusal. No new tool profile is requested. |
| Missing counter, hash drift, invalid count or counter error | No unsafe widening; unsupported profile/status is explicit. |
| Store read failure, malformed entries or duplicate hook invocation | No unintended duplicate/injected text, leaked note content or ambiguous applied count; preserve all real data. |

The matrix can be prepared with disposable stores and handwritten request data. No restricted 24-question items are needed. Review the actual shared count service/order only when gateway source is legitimately available; no competing gateway implementation is requested.

## What window 7 actually adds

[Normalized record](window7-observation-2026-11-14.json): four admitted synthetic count pairs each have zero recorded net delta (two Arabic examples and two history examples, with overlap); one 2,400-count request records HTTP 413. The long probe is **1,641 input / 48 output requested / 12 output recorded**, so it does not satisfy the proposed approximately 1,700 + 256 release check. The refusal alone does not test the prompt-plus-output boundary near capacity.

**Separate later probe:** Claude subsequently added one request under `after_window_single_request`, preserved separately from the five original window probes. The [updated source artifact](https://github.com/mms20102/Local-AI-tests/blob/2d5d5374bed4f79e4fa70187368845361bac952c/research/context-preflight/window7-usage-parity-2026-11-14.json), blob `235ca87520a172ac2c18e8b2ce10e5e45d4407fa`, records **1,717 prompt tokens, 256 requested and generated, zero count delta, finish `length`, 46.6 seconds**. The original five probe objects are unchanged. This addresses the approximate long-input/full-output-allowance example on the reported stack; it does not establish answer correctness/completeness, a universal 32-token bound, nonempty-note behavior or all context acceptance checks. Download contention remains.

Timings taken during an active large download are not a clean benchmark. Saved totals and one reported closure do not identify the loaded hook revision, prove all transformations, demonstrate nonempty-note adherence or establish general coding quality. No new live test is requested here.
