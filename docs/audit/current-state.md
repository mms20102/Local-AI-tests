# Audit current state

Checkpoint: 2026-11-17. This is a repository-level inventory, not an independent
runtime or sandbox certification.

## System boundary

The intended local path is:

`Open WebUI -> LiteLLM -> Colibri -> Qwen`

This checkout contains sanitized evidence, research protocols, fixture metadata,
audits, and one small co-chat watcher. It does not contain the laptop runtime,
model weights, private notes, credentials, or a runnable candidate-execution
grader.

## Component inventory

| Component | Repository evidence | Classification | Safe action now |
|---|---|---|---|
| UI/gateway/inference stack | `docs/ARCHITECTURE.md`, `README.md` | External/local runtime; not present here | Static review only |
| Teaching store/callback | `research/teach-*.md`, `research/experiments/*teach*.json` | Source/evidence reported; live identity unverified | Review synthetic evidence |
| Context admission | `research/context-preflight/`, `research/gateway-admission-review.md` | Partial design and saved observations | Review; no live request |
| CODE-Q1 fixtures/grader | `research/coding-quality-v1.proposed.json`, linked historical artifacts | Frozen research scope; semantic result provisional | Do not rerun candidates |
| Sandbox/VM boundary | `research/WINDOWS_ISOLATION_PROPOSAL.md`, sandbox audit | Design candidate with recorded failures | Handwritten review only |
| Benchmark planner/worker | `research/BENCHMARK_PROTOCOL.md`, `research/PC_TEST_REQUEST.md` | Planner/worker evidence; live runner readiness unproven | No laptop benchmark |
| Lifecycle/recovery | Research reports and worker handoffs | Partial, provenance mixed | Require identity and restore evidence |
| Repository tooling | `tools/watch_cochat.py` | Local coordination helper | Trusted static/unit checks only |

## Current safety decision

Generated candidate execution, live model benchmarking, runtime changes, VM or
security-setting changes, model downloads, and private-artifact publication are
disabled for this repository session. Missing proof is recorded as
`BLOCKED`, `NOT_RUN`, or `UNREVIEWED`; it is never promoted to `PASS`.

## Highest-priority blockers

1. Judge integrity and raw per-case evidence are not independently closed.
2. The tested host-share boundary allowed writes; sandbox cleanup and observer
   separation remain unresolved.
3. Exact runtime, model, tokenizer, profile, and loaded teaching identity are
   not consistently verified.
4. Final serialized token admission and omission disclosure are incomplete.
5. Correctness-qualified, quiet-window performance evidence is absent.

See [`gap-matrix.md`](gap-matrix.md), [`evidence-provenance.md`](evidence-provenance.md),
and [`../../RELEASE_READINESS.md`](../../RELEASE_READINESS.md).
