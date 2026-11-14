# Project roadmap

Updated 2026-11-14. Ownership and status here reflect the [current checkpoint](../docs/CURRENT_STATE.md); historical plans remain in Git history.

## Completed

- [x] Shared briefing published; real Claude collaboration established.
- [x] Hardware/runtime configuration inventoried by the PC worker and independently checked by Claude.
- [x] Schema-4 preparation package published and independently reviewed.
- [x] CODE-Q1 fixture revision 2 frozen: 12 tasks, 116 authored cases; model execution disabled.
- [x] Teach revision-6 offline persistence milestone: independent Linux pass, 72 passed / 1 skipped of 73.
- [x] Static context input audit: 25 prompt/reference Git blobs matched across 12 tasks.

These checks establish preparation/persistence evidence, not runtime speed or model correctness.

## In progress: highest-value unblocked work

1. **Tokenizer/context preflight — reported measurements complete; engine overhead pending.** Claude reports 118–300 input and 31–137 reference tokens; Codex matched fixture bytes and arithmetic. Keep binary-added tokens null until a later otherwise-authorized engine observation; no special traffic or model loading now.
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

- Teach hook integration and English/Arabic behavior: only a separately authorized scoped trial; hook remains **off**.
- CODE-Q1 model drafts: after preflight/runtime gates; generated code stays unexecuted.
- Semantic grading: reviewed containment, resource limits and trustworthy external observation/judging first.
- Lookup off/on, cap32/48, tier/thread sweeps: separate frozen comparisons after memory clearance and baseline reproduction.
- Alternative coding models or engine 2.1: preserve the baseline. Claude reports a 2.1 first-start check with high memory pressure/effective cap 8, then 2.0 restoration. Independently inspect the worker-owned launcher diff, current identity and checksum first; no default change or speed improvement is established.

Do not reopen completed persistence/planner work without a concrete new defect. A blocked live step does not stop offline source, fixture, contract or documentation work.

## Ownership

PC worker: runtime/operational adapter. Claude: teach/CODE-Q1 implementation and requested tokenizer-only check. Original reviewer: independent teach verification. Codex: evidence, primary-source research and coordination. Mohamed: project scope and live-trial decisions.

Use the [active co-chat](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md), read current heads, append only your own turn with the latest blob SHA, and avoid acknowledgement loops.

## Active runtime reservation

Claude's second-window host-pool-off test is reported intent, with another launcher change. All competing runtime/gateway work remains on hold until the matching closure; the earlier first-window read-only handoff is superseded. Its reported restoration must not be assumed to describe the current second-window state. No runtime test is initiated by this roadmap.
