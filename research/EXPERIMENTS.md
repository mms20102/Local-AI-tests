# Experiment register

Checkpoint: 2026-11-14. No raw prior-run artifacts are present in this repository at this checkpoint.

## Historical reports

| ID | Change | Prior report | Evidence status / limitation |
|---|---|---|---|
| H001 | Expert-cache configuration | One coding answer: 13.95 s baseline, 7.98 s candidate (42.8% less elapsed time for that single trial) | Reported; exact prompts, tokens, config and cache state unavailable. Not the later paired average |
| H002 | Tuned cache, reverse-order comparison | About 34% average latency reduction on short coding, 18% on a tool request | Reported; small tests, sample count/details absent. I001 now clarifies cap 4 versus 32, same model/Vulkan; raw paired evidence remains missing. Do not claim universal improvement |
| H003 | Shorter coding instructions | Faster first visible text in three paired tests | Reported; timings and correctness results not available |
| H004 | Native prompt lookup | Helped a repetitive code edit | Reported improvement remains unproven. I001 confirms Vulkan/lookup engagement and tokens-per-forward logs, but no lookup-off A/B timing table |
| H005 | Full local stack | Real generation, streaming, saved chat across restart and launcher checks passed | Reported; rerun live smoke test before tuning |
| H006 | Structured tools | Later model requests parsed into structured tool calls | Reported; not an end-to-end autonomous coding test |

The arithmetic in H001 is calculated from the two reported numbers; it does not replace missing run evidence. H001 and H002 are different observations.

## Proposed reproduction queue

| ID | Test | Status | Gate |
|---|---|---|---|
| P001 | Recover exact hardware, installed versions and effective settings | Pending PC access | Sanitized inventory, no credentials |
| P002 | Working baseline smoke test | Pending PC access | Direct and gateway calls, UI streaming, cancellation, restart persistence |
| P003 | Baseline versus confirmed 32 expert cap | Pending P001/P002 | Paired held-out prompts; no correctness/memory regression |
| P004 | Concise versus existing coding prompt | Pending P002 | Same requested deliverable, token/quality checks |
| P005 | Lookup off/on for code edit and non-repetitive tasks | Pending version/backend verification | Prove active flag/acceptance telemetry; include negative result |
| P006 | Qwen coding specialist side-by-side | Pending resource/format check | Fit, time-to-correct-answer, tool schema and Arabic checks |

## Record format for each new experiment

- ID, author, date, status and hypothesis.
- Hardware, power/thermal state and OS/driver.
- Engine commit/version, actual executable and model identity/quantization.
- Baseline/candidate effective configuration; one variable changed.
- Prompt-set version, seeds/sampling, input/output tokens and length limits.
- Cache state and ordering; cold start separate from warm repeated use.
- Every run's end-to-end first visible answer latency, completion time and correctness.
- RAM/VRAM, disk reads/cache hit if available, errors and cancellation behaviour.
- Sanitized artifacts, limitations and rollback.
- Decision: proposed / reproduced / rejected / adopted.

Use [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md). Never fill absent measurements with plausible numbers.

## R001 — Output-budget completeness (new worker report)

[Machine-readable report](experiments/2026-11-14-output-budget.json): a 32-token ceiling truncated a seven-function task after 18.28 s; 192 completed in 30.41 s with first text at 10.22 s and a reported expected-AST match. No generated code was executed. Minimum sampled free RAM: 5.62 GiB. This is one reported run per ceiling, not a repeated speed benchmark or a semantic test.

## I001 — Installed inventory and test boundary

[Worker-verified inventory relayed by the coordinator](experiments/2026-11-14-pc-inventory.json): Colibri 2.0.0, Vulkan, Qwen gs64 container, cap 4 versus 32, context 2048, one KV slot. Full model hashes/revision remain missing. Lookup engagement is demonstrated by reported logs; speed benefit is not yet isolated.

The worker's planner is partial: three isolated files, 23 synthetic harness tests, known Arabic fixture encoding defect and incomplete immediate-stop tests. The connection recovered after a disconnect and offline corrections are in progress. No full cache A/B, inference run or live-setting change is reported in flight at this checkpoint.

See [optimization review](OPTIMIZATION_REVIEW.md) and [specific worker request](PC_TEST_REQUEST.md).

Later checkpoint: the offline planner corrections were completed, with 27 tests and ZIP/credential validation reported passed. Its 10,641-byte preparation archive is recorded in I001. This package only plans/validates: it does not launch models, collect telemetry, write run checkpoints or perform semantic evaluation. No new cache A/B ran.
