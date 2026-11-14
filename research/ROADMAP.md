# Project roadmap

Updated 2026-11-14. Ownership and status here reflect the [current checkpoint](../docs/CURRENT_STATE.md); historical plans remain in Git history.

## Completed

- [x] Shared briefing published; real Claude collaboration established.
- [x] Hardware/runtime configuration inventoried by the PC worker and independently checked by Claude.
- [x] Schema-4 preparation package published and independently reviewed.
- [x] CODE-Q1 fixture revision 2 frozen: 12 tasks, 116 authored cases; model execution disabled.
- [x] Teach revision-6 offline persistence milestone: independent Linux pass, 72 passed / 1 skipped of 73.
- [x] Static context input audit: 25 prompt/reference Git blobs matched across 12 tasks.
- [x] Independent post-window-3 read-only inspection: 2.0 native binary matches prior verified baseline; original launcher hashes match; clean local tree at 7111656. No new tests or changes.

These checks establish preparation/persistence evidence, not runtime speed or model correctness.

## In progress: highest-value unblocked work

1. **Native token admission — tagged-source audit integrated; installed parity pending.** [Audit](context-preflight/token-admission-audit.md): normal Qwen36 answers are clamped to remaining context, no separate BOS/EOS is appended in the audited text path, and external/native tokenizer parity remains unproved. Claude owns an offline installed-renderer/already-saved-usage comparison. Keep installed measured fields null without evidence; no new traffic is requested.
2. **Operational components — PC worker.** Continue locally owned, reviewable offline implementation/validation. Return exact lifecycle/identity/stop-gate status. Preserve the 18-file commit; its rejected publication is not being retried.
3. **Shared evidence — Codex.** Keep this roadmap, current state and worker packet aligned with actual artifacts and distinguish author-reported, independently tested and proposed results.

## Gates before a controlled runtime measurement

- [ ] Independently pinned installed model/engine identity.
- [ ] Request serialization/tokenizer fit, with output and special-token overhead recorded.
- [ ] Complete owned-arm lifecycle, checkpoint/stop handling and restoration evidence.
- [ ] Fresh physical/commit/GPU headroom satisfying the frozen admission policy.
- [ ] Coordinated idle maintenance window; one model instance and one runtime owner.
- [ ] Then the existing frozen cap4/cap32 plan, without teach injection or silent plan changes.

The full benchmark remains disabled. Publishing its components is separately blocked by approval review; do not bypass that rejection.

## Later studies, kept separate

- Teach hook: enabled after window 6 is Claude-reported; exact loaded revision/live equivalence remain unverified. Rev10's independent offline pass does not deploy it. Address the [new source-scoped latency/count/docs findings](INTEGRATION_QUEUE.md) through Claude's ownership; no unsolicited restart.
- Controlled CODE-Q1 drafts: after preflight/runtime gates. Exploratory drafts already exist in the separate cap study; a disabled fixture manifest does not mean no model request has ever occurred. Generated code stays unexecuted.
- Semantic grading: reviewed containment, resource limits and trustworthy external observation/judging first.
- Smaller-cache cap24/32 and lookup proposals: separate frozen comparisons after owned-runner/identity/headroom clearance. Larger caps remain deferred; these are hypotheses, not local improvements.
- Alternative coding models or engine 2.1: preserve the baseline. Claude reports a 2.1 first-start check with high memory pressure/effective cap 8, then 2.0 restoration. Independently inspect the worker-owned launcher diff, current identity and checksum first; no default change or speed improvement is established.

Do not reopen completed persistence/planner work without a concrete new defect. A blocked live step does not stop offline source, fixture, contract or documentation work.

## Ownership

PC worker: runtime/operational adapter. Claude: teach/CODE-Q1 implementation and requested tokenizer-only check. Original reviewer: independent teach verification. Codex: evidence, primary-source research and coordination. Mohamed: project scope and live-trial decisions.

Use the [active co-chat](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md), read current heads, append only your own turn with the latest blob SHA, and avoid acknowledgement loops.

## Source-trust follow-up, not a new runtime study

The independent runtime inspection is complete at the recorded checkpoint. Workbench's manifest hash is stale and the separate 2.1 launcher lacks coverage. The [review packet](MANIFEST_REVIEW_2026-11-14.md) calls for independent source/diff review and a local candidate, with no live manifest rewrite or blanket rehash. Keep 2.0 as the confirmed checkpoint; do not infer a speed or memory-leak verdict from the short 2.1 samples. Recheck current reservations before local work.

## Current activity checkpoint

Claude round 28 follows reported closures through window 6. The earlier window-4 reservation is historical. Its [exploratory cap result](audits/cap4-cap32-exploratory-audit-2026-11-14.md) is audited as split-run metadata with lifecycle limitations, not the full schema-4 or semantic study. Round 28 reports a private user-directed trial and an approximately 419 GB download underway, not model adoption. Absence of an open window notice does not imply an idle PC. Check the latest co-chat and coordinate before live work.

The [integration queue](INTEGRATION_QUEUE.md) assigns the focused research handoffs and distinguishes source checks, coordinator summaries and proposals.
