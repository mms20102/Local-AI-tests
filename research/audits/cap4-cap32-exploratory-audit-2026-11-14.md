# Independent audit: exploratory cap4/cap32 run

2026-11-14. **The reported arithmetic reproduces.** Across the 48 recorded scored drafts, cap4 totals **962.24 s** and cap32 **704.99 s**: **26.7345% less recorded completion time**. This is useful exploratory screening evidence for these short tasks, not execution of the frozen schema-4 plan, a clean lifecycle result or semantic-quality evidence.

This audit parsed published JSON and recomputed statistics with auditor-authored JavaScript. It read the driver as text. **No driver, Python source, model output, PC command or model request was executed.**

## Frozen evidence

[Source snapshot](https://github.com/mms20102/Local-AI-tests/tree/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory):

| File | Git blob |
|---|---|
| `cap_ab.py` | `a5571ea0c79fae3d676ddf58e7527b7add0f4fab` |
| `result-pair1.json` | `e290e2e6fcfce4db59e6b37ccc3d00a76037aa65` |
| `result-pair2.json` | `4c38b3f8b42b4dd25ec9de03b6073f3a962c338d` |

All three returned blob identities match the same tree. Original artifacts are unchanged. [Machine-readable calculations](cap4-cap32-exploratory-audit-2026-11-14.json) retain invocation status, denominators, per-task reductions and findings.

## Statistics independently recomputed

Reduction is `100 × (1 − cap32/cap4)`. Pair medians use the twelve task-wise reductions; the aggregate is a ratio of summed helper `elapsed_seconds`. Totals were also checked in integer centiseconds.

| Order pair | Cap4 total | Cap32 total | Median task completion reduction | Median first-text reduction | Cap32 lower completion |
|---|---:|---:|---:|---:|---:|
| 1: A then B | 484.02 s | 351.07 s | 26.3291% | 25.8442% | 12/12 |
| 2: B then A | 478.22 s | 353.92 s | 24.3722% | 23.5706% | 12/12 |
| Summed | 962.24 s | 704.99 s | aggregate reduction 26.7345% | — | 24/24 paired observations |

The published rounded totals/medians/ranges reproduce. “26.7%” describes reduction in recorded completion time, not token throughput. The pooled median of 24 task reductions is 25.3571%, a different statistic.

These totals exclude startup, warm-up, shutdown, the outage and manual recovery. They are not end-to-end availability/turnaround measurements. Driver wall-time totals are slightly larger (967.03/709.76 s); the headline uses helper elapsed time consistently.

There are **12 unique tasks, two order-pair blocks and four stack starts**. The 24 task pairs are correlated repeats, not 24 independent experiments. No significance, confidence-interval or general-workload conclusion is established by the all-positive direction count.

## Complete scored rows; incomplete first invocation

- Every run contains each expected task exactly once. Combined observed order is **A,B,B,A**; each recorded engine header matches cap 4 or 32 as intended.
- All **48 scored rows** record helper exit 0, `stop`, not truncated, complete transport and static pass. Four warm-ups also record complete responses. Each engine log count is 13 chat requests, consistent with one warm-up plus twelve scored rows.
- **Invocation 1 planned ABBA but recorded only AB.** Its status remains `aborted` with a stop-stack exception and `restored_fast_stack: false`. Two planned runs were unstarted there.
- **Invocation 2 separately requested BA**, recorded both, and reports complete/restoration true. Run numbers reset; identify rows by invocation + run/session, not run number alone.
- Reconstructing the intended logical four-run sequence gives 48 observed scored rows. Do not add the superseded unstarted slots as new trials, or change the first file to “complete” because its scored requests finished.

Claude reports that the UI stopped listening without exiting, a timeout left engine/gateway up, manual intervention released cleanup, and a fallback was added before the second invocation. The abort/restoration failure is present in the JSON; the exact outage duration/process actions and first invocation's pre-patch driver identity are not independently reconstructible from these files. Only the post-fallback driver is published. Thus this is **two invocations across an incident and code change**, not one uninterrupted clean batch.

## Output and quality limits

Nine tasks have the same recorded fingerprint/length across all four runs. A03, E01 and F02 vary. Within matched order pairs, 22 of 24 observations have matching recorded fingerprints/lengths; the two mismatches are A03 and F02 in pair 1.

For that **22-pair descriptive sensitivity subset**, cap4 totals 875.30 s and cap32 641.65 s: **26.6937% lower recorded completion time**. This suggests the overall arithmetic is not driven only by the two visibly different-length pair outputs. It does not remove history, resource, order or correctness uncertainty.

The field named `output_sha256` stores only **16 hexadecimal digits (64 bits)**. Outputs are absent, so this audit cannot recompute full hashes, prove exact output identity or rerun static grading. Say “recorded matching fingerprint/length”, not independently verified byte identity.

The published grader checks parsing/names/format structure and reports semantics unassessed; it can accept bare code for a single file. A static pass is not proof of exact answer-format compliance or working code. No model-generated code was executed. Output changes cannot be declared harmless or defective from these metadata alone. No actual input/output token counts are recorded.

## Resource and attribution limits

Cap32's sampled post-run commit headrooms are **0.62 and 0.81 GiB**; cap4's are 2.28 and 2.63 GiB. Available RAM is 5.65–5.68 GiB at cap32 versus 7.56–7.71 GiB at cap4; engine private memory is 10.27 versus 8.42 GiB. These are single samples, not peaks. The exploratory driver's declared pre-start gate was only available RAM; it does not provide ongoing commit/GPU safety evidence.

No per-arm model/binary/config/fixture/history identities or per-request resource traces are pinned. Fresh processes do not clear OS file cache; fixed task order favors repeatable prefix/history effects. ABBA helps expose order sensitivity but does not eliminate these limits or the split-invocation incident.

“Disk loads” are engine counters, not measured physical disk I/O. Scoped/overlapping engine times and matching counters do not isolate the causal bottleneck. Do not infer production tail latency, semantic non-regression or a universal cache gain.

## Driver findings: source review, not reproduced runtime tests

These findings concern future reuse; no driver repair or new run is requested during the current work.

1. **Fail-open resource evidence** ([lines 63–77, 204–205](https://github.com/mms20102/Local-AI-tests/blob/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory/cap_ab.py#L204)). Failed sampling returns an empty map and missing available RAM defaults to 99, allowing startup. There is no commit/GPU admission or per-request pressure stop.
2. **Process ownership** ([lines 80–109](https://github.com/mms20102/Local-AI-tests/blob/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory/cap_ab.py#L80)). Stop selects the newest session. The fallback scans matching Python command lines and force-kills process trees without verifying project/session/PID creation identity. It can target an unrelated matching host; no such event is asserted here.
3. **Failure/attempt accounting** ([lines 131–146, 210–218, 226–260](https://github.com/mms20102/Local-AI-tests/blob/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory/cap_ab.py#L210)). Returned warm-up/row errors do not force abort; in-flight exceptions can occur before a row is appended. Main returns exit 0 after an aborted run. The present scored rows are all successful metadata, but this control flow cannot guarantee future honest fault handling.
4. **Weak restoration proof** ([lines 229–245](https://github.com/mms20102/Local-AI-tests/blob/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory/cap_ab.py#L229)). A partial remaining listener can prevent restoration. Success is UI health only, not verified version/cap/ownership of all services. A save error can precede cleanup. Preserve the first invocation's failed restoration; the second's true flag is not independent executable verification.
5. **Draft correlation** ([lines 131–146](https://github.com/mms20102/Local-AI-tests/blob/d858cb890aa36783993e5cfe7cf13e76c4daebcb/research/experiments-claude/2026-11-14-cap4-cap32-exploratory/cap_ab.py#L131)). The selected draft is a new filename chosen from a shared directory, not a request-id match. Another writer could cause misassociation; the recorded quiet window is not a code-level guarantee.
6. **Provenance/entry points.** Mutable single-result files lack per-run driver/hash provenance. The published fallback reportedly differs from the first invocation's code. Also, `--smoke` sends a real generation request and saves a draft despite its “changes nothing” wording. Do not execute it as an offline/read-only audit.

Use the existing PC worker's owned lifecycle/identity/fault contracts for a future controlled study rather than treating this exploratory script as a production runner. Any repairs/validation should be coordinated after the relevant runtime reservation; no competing implementation is requested.

## Later hook state is a separate identity change

Window 4 precedes the reported window-5 teach activation. Claude now reports the hook enabled with an empty store; live state/invariance was not independently verified by this audit. Independent revision-7 offline review found logging can propagate `BrokenPipeError` and a snapshot/log-fingerprint race; those findings were relayed for an offline fix. A direct empty-store callback returning the same object does not prove pipeline invariance.

Future benchmark identity must record callback configuration, hook revision and store snapshot. Do not silently reuse the historical hook-off baseline, infer current emptiness, purge user notes or change the hook under this audit.

Original evidence is preserved. No PC traffic, runtime/hook/configuration change, new benchmark, candidate-code execution or rejected-component publication was performed.

Subsequent rev8 independent normal-store checks passed offline (76 passed, 4 skipped), but additional diagnostic hardening remains and the gateway is reportedly still on rev7. That later fix is not deployed by this audit and does not retroactively alter window-4 evidence.
