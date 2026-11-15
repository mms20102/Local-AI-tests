# Windows Sandbox CODE-Q1 experiment: independent evidence review

Checkpoint: **2026-11-15 UTC**. Source: [`377fae14`](https://github.com/mms20102/Local-AI-tests/tree/377fae14ce8940f0f1595d658b7493198a881a79/research/coding-quality-v1/sandbox). This document integrates the designated independent reviewer's portable findings. That reviewer performed read-only source, hash and result-arithmetic checks, with a second source reviewer confirming the priority findings. This repository session also read the critical judge branch. **Neither review executed candidates, the harness or probes, or accessed the PC/VM/runtime.** The private workspace report/code is not copied or published.

## Result supported by the available evidence

Claude reports enabling/running through Windows Sandbox after Mohamed's own actions and direct instructions in Claude's session. Its earlier notice at `1b4edb5` announced handwritten probes only; the later completion additionally reports all 12 drafts executed before independent harness review. This is an attributed action/authorization report, not retrospective clearance from this session.

| Evidence | Outcome and limit |
|---|---|
| Original inputs | Reviewer verifies all 91 CODE-Q1 input blobs unchanged, four published source hashes and all 12 draft hashes matching. |
| Published score arithmetic | **11/12 tasks; 112/116 cases; Arabic 3/3, English 8/9.** All first attempts remain in the denominator. |
| F02 | Reported failures at combined case indexes **0, 3, 4, 6**, matching the earlier source-derived input-mutation finding. |
| E02 | Author reports 21/21; this is not independently re-executed here. |
| Re-grading | Raw guest per-case observations are not published, so the reviewer cannot rerun the judge over them. |
| Probe repeats | One saved probe session is published; the second same-outcome run is an author report. |
| Acceptance | **Provisional author-reported experiment.** Identity/arithmetic checks do not independently validate behavioral observation integrity or the release criterion. |

No general weakness below proves these particular unchanged drafts exploited it. The reviewer manually inspected the simple drafts and found no corresponding attack. Preserve the experiment and original first-attempt bytes.

## Critical judge false pass

The source at [grade.py:101–108](https://github.com/mms20102/Local-AI-tests/blob/377fae14ce8940f0f1595d658b7493198a881a79/research/coding-quality-v1/grade.py#L101) accepts:

```python
case = {"call": "m.f", "args": [1], "expect": 999}
record = {"status": "raised", "args_after": [1]}
```

After accepting the status and unchanged arguments, missing `raises` and missing `error` compare as `None == None`. The record can pass without a return value or expected-value comparison. This is a source-derived counterexample, **not an executed candidate**. It contradicts the general claim that withholding expected values alone prevents a false pass.

Repair with strict, status-specific required fields/types; a raised record needs a valid explicit exception expectation and error. Test missing returned value against a null expectation, duplicate JSON keys, nonzero exits with valid-looking records and forged/truthful mutation/identity fields. Fixing one conditional is insufficient for the separate observer boundary.

## Other confirmed source/evidence findings

1. **Behavioral observer:** candidate and reporter share an interpreter and guest administrator account. Parent-held expected answers do not authenticate `args_after`, exceptions or identity claims. The candidate can interfere with the runner or request guest shutdown. The spoof probe covers invalid/self-declared reports, not well-shaped forged observations.
2. **Result validation:** `guest_runner.py:64–66` marks a nonzero exit finished; `sandbox_host.py`'s `judge_entries:165–170` ignores exit code and can accept a valid-length record list despite `stdout_capped`. `read_report:150–153` accepts `network={}`; default JSON parsing permits duplicate keys.
3. **Output bounds:** `guest_runner.py:60–79` writes child output to a file while the child runs, then reads at most 1 MiB. This is a **read cap, not a file/disk-growth cap**: the saved flood probe records **20,971,608 bytes written**. No enforced quota for the writable mapped report is demonstrated.
4. **Lifecycle:** ordinary child exit does not establish descendant cleanup. Host/guest process-list and kill calls lack bounded calls and verified statuses. A process-name PID scan is not recorded VM/process ownership; failed inspection may look empty. Launch/cleanup is not protected by a cancellation `finally`.
5. **AST scan:** `reach_of` misses `__builtins__` string subscripting. The `plain=True` grouping is an inspection aid, not a containment or observation-authenticity boundary. No such attack was found in the actual frozen drafts.
6. **Isolation evidence:** requested `.wsb` settings and guest self-reports are not independent proof of the full boundary. Failed network samples lack healthy owned controls and IPv6 evidence; actual runtime/configuration identity and independent enforcement evidence are not archived.

## Next bounded work

Send the concrete findings to Claude, keep the original artifacts and correct current score/cap wording. First repair pure parser/judge handling with regression tests; then review handwritten output/lifecycle and observation validation before more candidate grading. Any broader isolation proof remains distinct from parser correctness. Do not claim this review created an execution restriction in Claude's session or retrospectively approved its action.

The private cloud containment candidate has **51 author and independent component-test passes**, but no Docker/Actions run, actual canary validation or draft execution. It remains private/unlaunched while this Windows path is assessed. No competing harness is being implemented here. Canonical manifest flags remain false; Claude reports using the parser/driver/judge directly outside the gated semantic entry. Those flags therefore do not imply no project execution occurred.

Window 9 is a later, separate runtime report; [normalized intake](../experiments/2026-11-15-window9-intake.json). No clean speed, repeated-sample quality, browser status or streamed accounting result follows from this grading experiment.
