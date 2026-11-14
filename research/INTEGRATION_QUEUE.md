# Research integration queue — 2026-11-14

This page turns the coordinator's focused research handoffs into owned next steps. Full reports in other chats are not directly readable from this repository session; where only a coordinator summary was available, that is the evidence level below. Independent source checks are identified separately. No research proposal authorizes a PC change or establishes a local performance result.

## Immediate handoff

Claude round 28 selected **native token admission**, rather than another generic research choice. [The tagged-source audit](context-preflight/token-admission-audit.md) is now integrated: Qwen36 clamps the answer ceiling to remaining context; the audited text path adds no separate BOS/EOS; external/native tokenizer parity remains unproved. The audit distinguishes no dedicated HTTP route from actual native C/test interfaces and the v2.1 `TOK_ONLY` diagnostic.

Claude completed the round-29 offline saved-usage comparison. The [sanitized artifact audit](context-preflight/saved-usage-parity-audit-2026-11-14.md) recomputes 24/24 matching count pairs (68–261), zero observed net delta, and nine length-ended records at 256. Gateway provenance remains untraced; system-byte metadata and ratio labeling need reconciliation. This is dataset-scoped count agreement, not universal parity or proof of separately added tokens. Codex owns evidence publication. A gateway change remains a separate Claude-owned design decision. The existing PC worker owns the controlled runner and laptop operations; do not build a competing runner or reopen completed planner reviews.

## Current activity and privacy

Latest inspected collaboration checkpoint: **Claude round 29**, on branch commit `f4215ea11ffdf23542bf7c0a2a1321ed6bfb0500`, co-chat blob `2c5ca6049bd9f8e7ba821440c45018c344f0ea90`. Round 29 reports offline reading/counting only and no runtime/gateway change.

Runtime windows 1–6 were subsequently reported closed; the old window-4 hold is historical. This does **not** establish that the PC is idle. Round 28 reports a user-directed 24-question trial and an approximately 419 GB GLM-5.3 download underway, not loaded or adopted. Reported trial aggregates: 24 responses, nine length-ended, author grading 1/24. These are not independently verified scores, a CODE-Q1 semantic result or a diagnosed cause. Questions/answers stay local and restricted; do not retrieve or publish them. Recheck newer reservations and actual activity before any live work.

Callback enabled was reported after window 6; rev10 is offline/published and was explicitly not loaded through round 27. Exact currently loaded revision, middleware/wire equivalence and current user notes are independently unverified. Do not infer an empty store or edit/purge it.

## Owned queue

| Priority / work | Evidence now | Owner and next acceptance check |
|---|---|---|
| 1. Token admission | Tagged-source audit and round-29 sanitized saved-count comparison integrated: 24/24 matching totals; zero observed net delta in this near-ASCII dataset. Gateway path untraced. | Claude: reconcile 168-vs-182 system bytes and ratio label without exposing raw text. Gateway design/implementation remains separately authorized and Claude-owned; no new traffic. Historical CODE-Q1 native fields remain unknown. |
| 2. Existing operational adapter | Worker previously reported 109 isolated component tests; full owned Windows run and restoration readiness remain unestablished. Driver-safety and methodology chats supplied source-level requirements. | PC worker: capability matrix against owned PID/identity, fail-closed physical/commit/GPU gates, sampler failure, cancellation, journal/save failure and verified restore. Test offline with synthetic services first. Publication of the rejected components remains blocked; no alternate route. |
| 3. Coding evaluation | `6af88eb5-f168-8191-8b7a-49decbdab0f3` reports static grader gaps: unbounded read before size check, callable kind/signature, provenance gate. Not independently reproduced here. | Claude: assess current exact source and bound reads before loading; define callable/signature contract and immutable input/output provenance. Blinded human review can inspect drafts without executing them. Semantic execution still needs reviewed isolation and external observation. |
| 4. Teach latency, counts and wording | New source checks below, distinct from the completed rev10 logging/privacy pass. No live latency measurement. | Claude accepted these offline follow-ups in round 29, not yet started: reproduce malformed-ID count mismatch on a throwaway store, inspect synchronous read/retry/log paths, and narrow absolute docs. Any later behavioral matrix uses disposable synthetic stores. No unsolicited restart. |
| 5. Memory explanation | `6af88edf-32f8-8191-8577-dc31deb4f0e2` hypothesis; source path independently found below. | Runtime/source owner: first correlate existing binary/config/log evidence, including interleaving and populated slot count. Do not rerun merely to confirm the story. No causal verdict from size similarity. |
| 6. Smaller-cache / lookup study | `6af88eae-b1f8-8191-9a5c-52f7a4dd00c2` proposes cap24 vs32, then lookup controls. No local result. | PC worker/coordinator: separate frozen design only after runner/identity/headroom gates. Larger caps remain deferred; earlier samples are not current admission. |
| 7. Model candidates | `6af88ece-5fc8-8191-8ac0-ef365172b0f1` proposes Qwen3.5-4B/9B and Qwen2.5-Coder-7B GGUF. Official base/instruct cards exist; no selected quantization/runtime fit or local test. | Future model owner: pin actual artifact/license/runtime support, then one model at a time with complete-output Arabic/coding quality, latency and peak memory. No install or download follows from this shortlist. |
| 8. Teach evaluation | `6af88ed5-ff58-8191-bab3-b8f300d330ea` proposes synthetic bilingual/conflict, empty-store and nonempty-store matrix; no execution. | Claude + independent reviewer: define exact payload equivalence separately from timing/model adherence; disposable stores, explicit provenance and runtime coordination. |
| 9. Documentation consistency | `6af88ee7-417c-8191-b3fa-cb617e4690ea` flags stale worker/roadmap/manifest and CODE-Q1 wording; current-facing main docs reconciled in this integration. | Each source owner: describe fixture manifest disabled separately from already generated exploratory drafts. Historical source remains unchanged. |

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
