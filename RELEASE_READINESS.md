# Release readiness

Checkpoint: 2026-11-17. **Status: BLOCKED.**

This project is not ready to release a validated local coding assistant. The
current state is a research/evidence workspace with a provisional quality
result, unresolved sandbox boundary failures, and incomplete runtime/context
identity proof.

| Gate | Status | Required before release |
|---|---|---|
| Judge integrity and mutation resistance | BLOCKED | External verdict ownership, raw-record validation, F02 regression, and recomputable summaries |
| Raw evidence completeness | BLOCKED | Immutable per-case terminal records and hash manifest |
| Sandbox isolation | FAIL | Prevent host writes, prove guest/observer separation, limits, reset, and cleanup |
| Runtime/model/process identity | BLOCKED | Verified hashes, effective configuration, tokenizer/profile, callback, and serving process |
| Exact context admission | BLOCKED | Final serialization count, output reserve, margin, and Unicode boundary tests |
| Teaching and privacy | BLOCKED | Exact payload, omission disclosure, counter/error distinctions, and private-log controls |
| Lifecycle and recovery | BLOCKED | Identity-safe cancellation, atomic journal, telemetry refusal, restore, and rollback |
| Correctness target | NOT_RUN | Locked 12-task run after judge/isolation approval |
| Performance target | NOT_RUN | Quiet, counterbalanced, correctness-qualified run with useful-text parsing |
| Independent sign-off | UNREVIEWED | Separate reviewer validates the complete packet |

The detailed dependencies are in [`docs/implementation-plan.md`](docs/implementation-plan.md).
The machine-readable source of truth for this checkpoint is
[`docs/audit/release-gate.json`](docs/audit/release-gate.json).
