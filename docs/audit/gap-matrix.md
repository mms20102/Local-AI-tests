# Release gap matrix

Status values are deliberately conservative: `PASS`, `FAIL`, `BLOCKED`,
`NOT_RUN`, and `UNREVIEWED`.

| ID | Gate | Severity | Evidence | Required fix | Test/closure evidence | Dependency | Status |
|---|---|---|---|---|---|---|---|
| G-01 | External judge integrity | CRITICAL | `docs/CURRENT_STATE.md:10-14`; `research/audits/2026-11-15-windows-sandbox-grading-review.md` | Separate candidate, observer, and grader; reject malformed/missing/partial records | Trusted correct, wrong, timeout, crash, refusal, spoof, and mutation fixtures; raw-to-summary recomputation | None | BLOCKED |
| G-02 | Candidate isolation | CRITICAL | `docs/CURRENT_STATE.md:14`; `research/audits/2026-11-15-windows-sandbox-grading-review.md:4-15` | Prevent host mappings and export only after termination through an allowlist | Handwritten hostile probes plus reset/cleanup verification | G-01 threat model | FAIL |
| G-03 | Runtime identity | HIGH | `docs/CURRENT_STATE.md:57-63`; `README.md:9-17` | Capture executable/model/config/tokenizer/callback hashes and process creation identity | Doctor JSON compared with human report and serving process | None | BLOCKED |
| G-04 | Context admission | HIGH | `research/FINAL_GOAL.md:86-105`; `research/context-preflight/` | Count final serialized payload with verified tokenizer/profile; reject unknowns | English, Arabic, Unicode, and N-1/N/N+1 boundary fixtures | G-03 | BLOCKED |
| G-05 | Teaching/privacy | HIGH | `docs/CURRENT_STATE.md:29-40`; `research/FINAL_GOAL.md:68-79` | Verify exact final payload, omission disclosure, counter failures, and nonblocking logging | Disposable multilingual store matrix and redacted evidence assertions | G-03, G-04 | BLOCKED |
| G-06 | Lifecycle/recovery | HIGH | `research/INTEGRATION_QUEUE.md`; `research/FINAL_GOAL.md:60-67` | Fail closed on telemetry/identity/journal errors; use process identity, atomic checkpoints, rollback | Fake-backend state-machine, stale PID, cancellation, corruption, and restore tests | G-03 | BLOCKED |
| G-07 | Quality result | HIGH | `docs/CURRENT_STATE.md:10-11`; `research/audits/2026-11-15-windows-sandbox-grading-review.md` | Preserve raw records and rerun only after G-01/G-02 closure | Locked 12-task run with all failures in denominator | G-01, G-02, G-04 | NOT_RUN |
| G-08 | Performance result | HIGH | `research/FINAL_GOAL.md:41-58`; `research/BENCHMARK_PROTOCOL.md:38-57` | Quiet counterbalanced run with useful-text parsing and correctness-qualified latency | AB/BA repetitions, resource telemetry, rollback, cold/warm split | G-01 through G-07 | NOT_RUN |
| G-09 | Independent sign-off | HIGH | Master review prompt; no separate sign-off in this checkout | Produce review packet and obtain a separate reviewer decision | Reviewer validates claims, hashes, commands, and unresolved risks | G-01 through G-08 | UNREVIEWED |

## Interpretation

The provisional `11/12` result cannot promote G-07 or G-08 because the judge
and isolation gates are not closed. A successful unit-test count or a report
written by the candidate is not evidence of a passing release gate.
