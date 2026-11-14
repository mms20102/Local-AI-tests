# Experiment register

Checkpoint: 2026-11-14. No raw prior-run artifacts are present in this repository at this checkpoint.

## Historical reports

| ID | Change | Prior report | Evidence status / limitation |
|---|---|---|---|
| H001 | Expert-cache configuration | One coding answer: 13.95 s baseline, 7.98 s candidate (42.8% less elapsed time for that single trial) | Reported; exact prompts, tokens, config and cache state unavailable. Not the later paired average |
| H002 | Tuned cache, reverse-order comparison | About 34% average latency reduction on short coding, 18% on a tool request | Reported; small tests, sample count/details absent. Do not claim universal improvement |
| H003 | Shorter coding instructions | Faster first visible text in three paired tests | Reported; timings and correctness results not available |
| H004 | Native prompt lookup | Helped a repetitive code edit | Reported; no timing table or effective-backend log available |
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
