# Research integration queue — 2026-11-14

This page turns the coordinator's focused research handoffs into shared next steps. Full reports in other chats are not directly readable from this repository session; where only a coordinator summary was available, that is the evidence level below. Independent source checks are identified separately. No research proposal authorizes a PC change or establishes a local performance result.

## Offline streaming-adapter checkpoint — revision 3 component pass

The existing focused review at `1ea5c6f6` passed **41 / 5 LiteLLM skips** under the explicit caller-close contract. Pre-first-pull, ordinary distinct-resource and close-originated cancellation cases pass; cancellation between pulls requires the caller's `finally: await stream.aclose()`. `uncertain` does not confirm release. [Versioned review](teach-status-adapter-review.md).

Pinned source shows the standard LiteLLM response can propagate closure to the adapter, but actual ASGI disconnect/routing remains untested. [Cleanup-path audit](context-preflight/litellm-stream-cleanup-source-audit.md). Reuse the existing capture work for actual proxy/ASGI boundaries; browser, nonstream and accounting remain separate. No duplicate receiver, registration or runtime change.


## Current component reviews and reported operating decision

The existing independent reviews are complete: **reason codes at `be282e3`: 24 passed / 6 tokenizer skips**, plus synthetic checks; **teach15–18 at `8ef7d505`: 104 passed / 5 skips**, plus 45 synthetic matrix cases. No new blocking defect was reproduced in those bounded paths. [Reason review](gateway-reason-codes-review.md) · [teach record](experiments/2026-11-14-teach15-18-independent-offline-review.json). Tests were coordinator-relayed, not rerun here; proxy checks used a stub, not HTTP serialization.

Claude's [later plan/UI report](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/co-chat.md) relays Mohamed retaining absent-counter byte-only notes and accepting the heuristic 32-token margin and launcher-report limitation as stated limits before a separately authorized, coordinated restart after the bounded reviews. This is an attributed policy report, **not proof of a native-token bound, actual process identity, final-payload equivalence, loaded revision or runtime authority for this repository session**.

The pinned UI is reported as Open WebUI 0.13.3 / LiteLLM 1.108.5, plain provider connection, Functions disabled and no response hook. Pinned-source research identified a **streaming provider-event candidate independent of Function enablement**, not a tested integration. [Display contract](teach-status-display-contract.md) · [exact downstream-payload evidence plan](context-preflight/final-payload-evidence-plan.md). Nonstream display and request-scoped transport remain open; manual log/status lookup is not automatic answer-linked disclosure. No PC/model traffic or deployment is made here.

**Latest coordination notice:** [runtime window 8 closure](https://github.com/mms20102/Local-AI-tests/blob/370b6765feb4a1a5507334143eeaa575ad064092/research/co-chat.md) is Claude-reported. [Artifact normalization](window8-observation-intake.md) recomputes **20 session + 5 probe + 3 network-request records**, not a 20-request total for the whole window. Stop-file cycles/session and selected HTTP/count observations advanced; exact loaded hook, live nonempty notes, Ctrl+C, semantic quality and clean speed remain unverified. Closure is not a request for new traffic.

The earlier source/revision checkpoints below are historical; their pending-review or pending-policy wording is superseded by this section.

## Historical rev18 intake — before the bounded pass

Claude’s [rev18 report](https://github.com/mms20102/Local-AI-tests/blob/da0db284590c718fb74558fc464dff7048ed78ec/research/co-chat.md), local `9514353`, is offline/not loaded and not independently reviewed here. A configured counter that fails or returns an invalid count now withdraws notes, preserves the admitted base and reports `uncounted`; successful over-limit counts remain `no_room`. **No counter configured is a separate unresolved case:** byte-rule notes are still injected with `kept-byte-rule-only`, without a demonstrated bound. Claude plans to ask Mohamed about disabling teaching in that case; no answer is recorded. Profile trust, independent auth/teach loads, exact final-payload evidence, heuristic margin, unpublished report-carrier edits and user-facing omission remain open. Reported publication tests: 109 run / 5 skipped; these are not an independent integration pass.

## Historical coding and successor intake

[CODE-Q1 exploratory first pass](experiments/2026-11-14-codeq1-exploratory-first-pass.json): Claude reports 12/12 transport stops and static-structure passes, median completion 34.9 s and first text 16.1 s during download contention. No behavioral grades, first-useful-text or clean-speed result; goal checks 2/3 stay incomplete. F02/E02 concerns are ungraded author reading; drafts remain on the laptop.

Rev17 (`83a6f58`, source `631b1ec1`) reportedly corrects type ordering and labels retained note fallback `byte_only`; it is not loaded or independently reviewed here. The label does not prove fallback safety: establish the supported byte bound or omit notes on uncertainty. No published reason-code-only delta link is available to this session, and the older full patch is not applied.

## Historical focused candidate review

At `b111a647` (reported local `d8d25e2`, teach rev16), the existing independent review is complete: **gateway 21 passed / 6 skipped; teach 104 passed / 5 skipped**. [Record](experiments/2026-11-14-gateway-revision16-independent-offline-review.json). The two urgent reproduced cases were relayed once: malformed assistant content raises `TypeError` before the string check; failed final counting retains notes with `uncounted=0`. Profile report trust, independent auth/teach loads, exact post-hook validation, heuristic margin, missing carrier-source evidence and UI disclosure remain unresolved. No restart clearance or duplicate review.

Do not apply the older parallel full patch. Current role/marker guards already overlap it; only distinct counter-reason propagation remains a useful delta. Source activity is reportedly offline/unloaded; current-stack static-only CODE-Q1 requests may occur without a restart/window notice, so no competing PC traffic is sent and no result is inferred.

## Published gateway and decision update

Claude’s [6c129837 relay](https://github.com/mms20102/Local-AI-tests/blob/6c1298375d265680313424c36dcecf32a6c4c71f/research/co-chat.md) quotes “Yes to all” for source publication, the primary 9/12 and 15s/60s targets, and a conditional rev14 restart after counter review. These are attributed reports, not independent runtime authorization here. The source is visibly [published](https://github.com/mms20102/Local-AI-tests/tree/6c1298375d265680313424c36dcecf32a6c4c71f/research/gateway-admission). The existing review is complete: **15 passed / 3 real-tokenizer tests skipped; no restart/live clearance**. [Review and repair matrix](gateway-admission-review.md) · [record](experiments/2026-11-14-gateway-admission-independent-offline-review.json).

Claude’s subsequent `87351dea` turn reports unloaded teach rev15 `uncounted` status and a later-system-message rejection at local `7dd479f`; no independent result for that successor is claimed. Actual profile binding, assistant-history handling, shared counter/profile validation of the exact post-hook payload, and real-tokenizer boundaries remain next offline work. User-visible omission and distinct counter-unavailable/no-room status stay open. The Sandbox choice is reportedly deferred. No window is open in the checked shared log, and loading stays held with findings unresolved. Claude reports a planned approximately 12-request static-only CODE-Q1 exploration on the current stack without a restart; no completion/result is inferred and this session avoids competing traffic. No duplicate review was started. This update supersedes earlier pending-publication/target-decision checkpoints below; older revision/source reports remain historical.

## Shared finish line

[FINAL_GOAL.md](FINAL_GOAL.md) records the shared bounded-check direction. Claude relayed Mohamed's coding-scope acceptance; primary targets and gateway publication were later relayed as accepted; see the current update above. The new [context/teaching alignment analysis](context-preflight/note-budget-alignment.md) is the immediate offline contribution. Routine Arabic/English coding usefulness remains the first-release goal on that attributed scope report. Larger/overnight models are a stretch. The [Windows isolation proposal](WINDOWS_ISOLATION_PROPOSAL.md) is a design for review, not a tested sandbox. Captured runner `1f067428` is not ready for live use; no delivery date or current-PC claim is inferred.

## Revision 14 status

Scoped independent repair review at `fce46151`: **100 passed / 5 skipped offline**, with no blocking regression in the tested snapshot/UTF-8 repair paths. The coherent-snapshot and valid-neighbor cases passed. [Record](experiments/2026-11-14-teach-rev14-independent-offline-review.json). This closes those source-repair cases; it does not clear real counter/profile/margin, user-visible disclosure or live loading. Counter failure still shares `no_room`. Rev14 remains reported not loaded; no runtime change or duplicate review is requested.

## Revision 13 status

The existing independent review at `cb987269` reports **97 passed / 5 skipped offline**; no live-integration clearance. Previous oversized-note omission and ordinary missing-field handling improved. Two reproduced cases—cross-snapshot diagnostic evidence after concurrent edit, and lone-surrogate text suppressing valid neighbors during UTF-8 rendering—were [relayed once](https://github.com/mms20102/Local-AI-tests/commit/f5d7aec07abfab5f006552f9d029fddddf25e709). [Record](experiments/2026-11-14-teach-rev13-independent-offline-review.json). Suggested offline repair checks retain one snapshot and isolate unrenderable entries. UI disclosure is still log-only; actual counter/profile and margin are unverified. No new live test or duplicate review is requested.

## Revision 12 status

Claude reports teach rev12 published, **not loaded**; the existing independent review is final at `eaf6016`: **92 passed / 5 skipped**, without token-budget integration clearance. The [pending record](experiments/2026-11-14-teach-rev12-review-pending.json) keeps short byte-route behavior, unpublished counter, unproven 32-token margin, later-system/history edge cases and log-only omission explicit. Whole enriched-request counting is reported only for the long fallback path. Confirmed review cases show a relevant 294-character note outside the 320-byte wrapped cap reports omitted=0, and malformed `when` alongside a valid note gives original/unknown/omitted0. The concrete findings were relayed once. Stand-in tests establish whole-candidate control flow and bounded note dropping, not real-counter/profile/renderer/margin or legacy-byte safety. Missing counters block new widening; stale plausible positive counts are not distinguishable at the interface. No integration/deployment clearance or duplicate review follows.

## Immediate handoff

**Window-7 follow-up:** the closure reports four admitted count matches and one refusal. [Arithmetic record](context-preflight/window7-observation-2026-11-14.json). Published teach source still budgets bytes, so long token-admitted conversations can omit saved notes; an empty-store probe cannot validate note behavior. Use the [shared-budget contract](context-preflight/note-budget-alignment.md) for design discussion before any separately authorized change. Exact loaded rev11 is inferred, not independently verified.

Claude round 28 selected **native token admission**, rather than another generic research choice. [The tagged-source audit](context-preflight/token-admission-audit.md) is now integrated: Qwen36 clamps the answer ceiling to remaining context; the audited text path adds no separate BOS/EOS; external/native tokenizer parity remains unproved. The audit distinguishes no dedicated HTTP route from actual native C/test interfaces and the v2.1 `TOK_ONLY` diagnostic.

Claude completed the round-29 offline saved-usage comparison. The [sanitized artifact audit](context-preflight/saved-usage-parity-audit-2026-11-14.md) recomputes 24/24 matching count pairs (68–261), zero observed net delta, and nine length-ended records at 256. Gateway provenance remains untraced. In round 30 Claude corrected system size to 168 bytes and relabeled the ratio as message-text bytes per prompt token; the corrected artifact preserves all row counts. This is dataset-scoped count agreement, not universal parity or proof of separately added tokens. Codex contributes evidence publication/review. A gateway change remains a separate decision; Claude offered implementation and Codex can help review. PC-side work is developing the existing runner and supplying laptop observations; do not build a competing runner or reopen completed planner reviews.

## Earlier activity and privacy checkpoint

Latest checked shared log: branch `2d5d5374bed4f79e4fa70187368845361bac952c`, co-chat blob `17a5bfb787db3f290b0441d6729b5d5a0218750c`. Window 7 is reported closed; coding-scope acceptance is relayed by Claude, while numerical targets and gateway-source publication remain pending. No new PC inspection or runtime traffic was performed by this session. Claude separately reports a later 1,717-input/256-output request, recorded outside the original window batch; its length-ended timing during the download is not a quality/speed result.

Previous inspected collaboration checkpoint: **round 30, goal proposal and offline progress**, on branch commit `829d3228438034b3126a2eac419517d1760db239`, co-chat blob `27717d07dfc327f68f6cb882a94e4be736511569`. It reports gateway `28753be` unpublished/not loaded pending publication approval and teach rev11 published/not loaded with independent review now relayed: 80 passed / 5 skipped offline at the same pinned source, not live deployment. No new request or runtime change is reported. Earlier task-control wording was withdrawn; all prior turns remain intact.

Runtime windows 1–6 were subsequently reported closed; the old window-4 hold is historical. This does **not** establish that the PC is idle. Round 28 reports a user-directed 24-question trial and an approximately 419 GB GLM-5.3 download underway, not loaded or adopted. Reported trial aggregates: 24 responses, nine length-ended, author grading 1/24. These are not independently verified scores, a CODE-Q1 semantic result or a diagnosed cause. Questions/answers stay local and restricted; do not retrieve or publish them. Recheck newer reservations and actual activity before any live work.

Callback enabled was reported after windows 6–7. Claude reports rev11 on disk at window-7 startup; the loaded identity remains inferred. Earlier rev10-not-loaded statements describe rounds 26–27. Exact currently loaded revision, middleware/wire equivalence and current user notes are independently unverified. Do not infer an empty store or edit/purge it.

## Wake coordination check

The PR-update automation and hourly fallback were privately checked **enabled**. The PR task records last run time 2026-11-14 17:28:58 UTC, while its detailed delivery status is **unknown**; no fresh end-to-end delivery guarantee follows. No already enabled task was toggled. Claude's substantive reply to `2cd8dce` is visible and Claude reports its Monitor delivered the turn about a minute after publication, with 30-minute rearming and a 10-minute session fallback. These are Claude-observed mechanism claims, not independently traced host events; they end with the desktop session. No model-stack restart is needed to check this watcher.

## Shared next steps

| Priority / work | Evidence now | Next contribution and acceptance check |
|---|---|---|
| 1. Token admission | Tagged-source audit and round-29 sanitized saved-count comparison integrated: 24/24 matching totals; zero observed net delta in this near-ASCII dataset. Gateway path untraced. | Round-30 metadata corrections are recorded without exposing raw text. Claude offered gateway implementation and Codex can help review a concrete proposal; live changes remain a separate decision. No new traffic. Historical CODE-Q1 native fields remain unknown. |
| 2. Existing operational adapter | Captured snapshot `1f067428`: 124 prior tests, but fake-backend-only coordinator and refusing CLI; not ready for live runs. Newer PC state and a delivery date are unknown. Driver-safety and methodology chats supplied source-level requirements. | PC worker: capability matrix against recorded process identity, fail-closed physical/commit/GPU gates, sampler failure, cancellation, journal/save failure and verified restore. Test offline with synthetic services first. Publication of the rejected components remains blocked; no alternate route. |
| 3. Coding evaluation | `6af88eb5-f168-8191-8b7a-49decbdab0f3` reports static grader gaps: unbounded read before size check, callable kind/signature, provenance gate. Not independently reproduced here. | Claude: assess current exact source and bound reads before loading; define callable/signature contract and immutable input/output provenance. Blinded human review can inspect drafts without executing them. Semantic execution still needs reviewed isolation and external observation. |
| 4. Teach latency, counts and wording | New source checks below, distinct from the completed rev10 logging/privacy pass. No live latency measurement. | Claude reports teach rev11 published/not loaded, with malformed-ID filtering and reduced retry sleeps. Independent review at `829d322` passed 80 / skipped 5 offline; programmed sleeps ≤100 ms but filesystem/log wall time is unbounded. ID shape is not provenance; no live loading verified. No duplicate review or restart. Any later behavioral matrix uses disposable synthetic stores. No unsolicited restart. |
| 5. Memory explanation | `6af88edf-32f8-8191-8577-dc31deb4f0e2` hypothesis; source path independently found below. | Runtime/source review: first correlate existing binary/config/log evidence, including interleaving and populated slot count. Do not rerun merely to confirm the story. No causal verdict from size similarity. |
| 6. Smaller-cache / lookup study | `6af88eae-b1f8-8191-9a5c-52f7a4dd00c2` proposes cap24 vs32, then lookup controls. No local result. | PC worker/coordinator: separate frozen design only after runner/identity/headroom gates. Larger caps remain deferred; earlier samples are not current admission. |
| 7. Model candidates | `6af88ece-5fc8-8191-8ac0-ef365172b0f1` proposes Qwen3.5-4B/9B and Qwen2.5-Coder-7B GGUF. Official base/instruct cards exist; no selected quantization/runtime fit or local test. | Future model comparison: pin actual artifact/license/runtime support, then one model at a time with complete-output Arabic/coding quality, latency and peak memory. No install or download follows from this shortlist. |
| 8. Teach evaluation | `6af88ed5-ff58-8191-bab3-b8f300d330ea` proposes synthetic bilingual/conflict, empty-store and nonempty-store matrix; no execution. | Claude + independent reviewer: define exact payload equivalence separately from timing/model adherence; disposable stores, explicit provenance and runtime coordination. |
| 9. Documentation consistency | `6af88ee7-417c-8191-b3fa-cb617e4690ea` flags stale worker/roadmap/manifest and CODE-Q1 wording; current-facing main docs reconciled in this integration. | Contributors: describe fixture manifest disabled separately from already generated exploratory drafts. Historical source remains unchanged. |

## Existing cache result and driver: deduplicate, do not reuse

Driver review `6af88ec5-3584-8191-92aa-a8ff8bc930ce` and methodology review `6af88ea7-fef8-8191-bfdf-40f3a977e0f9` agree with the [existing pinned audit](audits/cap4-cap32-exploratory-audit-2026-11-14.md). The 26.7345% arithmetic is reproducible in published metadata. Split invocations, an aborted first lifecycle, missing raw output, unknown semantic quality and low sampled commit headroom limit the interpretation.

Freeze `cap_ab.py` as evidence. Broad command-pattern killing, permissive sampler defaults, missing commit/GPU gates, save-before-restore failure paths and UI-health-only restoration are **source risks**, not evidence that an unrelated process was actually killed. Map these requirements onto the existing worker adapter; do not use that exploratory driver for the controlled study. Full-workload admission and restoration checks are project requirements; proposed numeric thresholds are not vendor standards.

## New teach source findings, pinned to rev10

Source revision `fd962cc2060c5bde7b1cce01f85991d7acaf16e7`; this session read text only.

- The async callback [calls injection synchronously](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/teach_hook.py#L115-L120). [Snapshot reading](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/teach_store.py#L582-L606) performs a full file read and up to 19 explicit 50 ms retry sleeps (0.95 seconds), in addition to unbounded I/O time. Synchronous diagnostic output can also delay it. These paths contradict an absolute nonblocking guarantee; no production stall was measured here.
- Snapshot active-entry filtering does not validate ID shape. [Selection/rendering/application](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/teach_store.py#L623-L695) can include an otherwise selected malformed ID and return it, while [the diagnostic counts only canonical IDs](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/teach_hook.py#L77-L86). Therefore reported entry count can differ from injected entries. This is a static path finding, not a reproduced/live incident. Redaction tests passing does not establish selection integrity.
- [Hook introductory wording](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/teach_hook.py#L10-L15) and [TEACH's empty-store wording](https://github.com/mms20102/Local-AI-tests/blob/fd962cc2060c5bde7b1cce01f85991d7acaf16e7/research/teach-store/TEACH.md#L109-L110) should distinguish returning unchanged request data in a direct check from live wire, latency and behavior equivalence.

The independent rev10 review remains 78 passed / 5 skipped within its tested scope. Do not reopen its completed redaction work without a concrete new regression.

## Extra 2.1 memory: plausible path, unproved cause

At upstream v2.1 `704a3f68184b78367a04cb5526e428dc2f90f05b`, [interleaved CPU slot allocation](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/qwen36.c#L4289-L4305) keeps `pw`; [`vk_slot_src`](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/qwen36.c#L5359-L5388) can additionally allocate persistent planar `t8` weights and `t8s` scales for that slot. This independently corroborates the **conditional allocation mechanism**, not its use by the installed release binary.

Illustrative geometry from the research handoff: 40 populated expert layers × cap32 × (3 × 2048 × 512 / 2 packed bytes + 3 × 2048 × 512 / 64 × 4 scale bytes) = **2,264,924,160 bytes = 2.109375 GiB**. Geometry and all slots being populated are assumptions for this estimate, not independently measured installed metadata. Similarity to Claude's reported roughly 2.21 GiB extra private memory is hypothesis-generating, not attribution or a leak diagnosis. Host-pool-off does not by itself establish that this distinct allocation path is disabled.

The upstream Windows planner [explicitly bounds physical availability by grantable commit when the pagefile value is supplied](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/resource_plan.py#L2027-L2039); [the normal Windows collection path passes both values](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/resource_plan.py#L2516-L2531). Correct any broad claim that upstream budgeting universally ignores commit. This source fact does not prove every explicit-cap/fallback path or the installed binary enforces our full-workload safety gates.

## Official model-card checks

Existence checked against [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B), [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) and [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct). These mutable cards do not identify a chosen GGUF, prove Colibri compatibility, or predict laptop performance. Preserve the current model.

## Coordination rule

Post one substantive next handoff after checking current branch heads, and request another concrete unblock only after meaningful work or a new blocker. Do not produce acknowledgement loops. Keep Claude's existing turns intact and keep the draft coordination PR open/unmerged.
