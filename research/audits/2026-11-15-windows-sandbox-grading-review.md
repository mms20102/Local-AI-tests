# Windows Sandbox CODE-Q1 experiment: independent evidence review

Checkpoint: **2026-11-15 UTC**. Source: [`377fae14`](https://github.com/mms20102/Local-AI-tests/tree/377fae14ce8940f0f1595d658b7493198a881a79/research/coding-quality-v1/sandbox). This document integrates the designated independent reviewer's portable findings. That reviewer performed read-only source, hash and result-arithmetic checks, with a second source reviewer confirming the priority findings. This repository session also read the critical judge branch. **Neither review executed candidates, the harness or probes, or accessed the PC/VM/runtime.** The private workspace report/code is not copied or published.

## Fifth probe: successful host-share writes; revision 7 detects after access

At [`48ded740`](https://github.com/mms20102/Local-AI-tests/commit/48ded740a535fd4ec6b77cfdcd4f603e9028d4cf), saved probe-5 summary/raw reports reconcile to **8 sessions/reports, 36 entries, 35 expected index outcomes and one mismatch**. This session parses the JSON and reads the write-only fixture; it runs no candidate or Windows command. Twelve references report 116/116 cases, every decoy fails at least one, and the `P_kill_runner` record returns `refused` while the guest runner reports and shuts down. That particular observation improves on the startup-failed probe 4; it is not general process/observer validation.

**The adverse result must remain a prevention failure.** `P_write`'s saved record lists `C:\\cq1\\out\\planted.txt` and `C:\\cq1\\out\\results.json` as written. The author reports the runner overwrote the planted result but left the extra file on the host. This exposes a host report-share integrity/resource boundary failure in the tested setup. The observed low-integrity/job fields did not prevent this access.

**Revision 7 is a different check:** after a candidate, claimed logic compares progress with memory, removes extras, discards tampered records and lets the host reject unexpected output files. Folder size is polled every two seconds against 16 MiB. These are **detection/rejection after access and a sampled threshold, not prevention or a disk quota**. Re-indexing `P_write` as `report_folder_tampered` must not erase its successful writes or turn prevention into a pass. Candidate account/restricted-SID prevention remains explicitly unimplemented.

The author's statement that no host data could be read through the share is **not established** by these results. The fixture at the actual run source `9a00a52a` (Git blob `2373509bea8572e34c87d6fdd49eda3ba166596f`) opens paths in `'w'` mode only. Share-read access remains untested in this evidence; inaccessible unrelated host folders are a different scope. [Co-chat correction](https://github.com/mms20102/Local-AI-tests/blob/675802bc6539da8d10114e75bea14c318ab5ecb3/research/co-chat.md) asks for precise separation, not another live test.

[Normalized intake](../experiments/2026-11-15-sandbox-probe5-intake.json) pins the two artifacts. Add revision 7 to the existing review: runner `6e5bb8b033aac59f9b5128c58db92a5f2d017d45`, host `37a4a0e60aa723f496cf261b4e379797e4b8bab1`. Review detection of transient/overwritten output, progress trust, shared storage limits, other same-user processes and unchanged same-interpreter observations. No new reproduced defect beyond the saved write failure is claimed.

The author reports 264 suite tests without failures and announces a sixth handwritten-only eight-session probe, with no drafts/chat traffic. At this pin its completion is pending. The original 11/12 remains provisional; the 12-draft hold, independent review and unresolved cleanup/observer boundaries remain. No duplicate implementation/probe, PC/VM access, privilege action, runtime change or cloud/Actions run occurred here.

## Historical third/fourth intake and revision-6 notice

The author publishes the requested source-pinned third/fourth summaries and raw reports at [`9a00a52a`](https://github.com/mms20102/Local-AI-tests/commit/9a00a52a6670d7e966eeb6bc57ae1ef1f3b271ce). This session parses/reconciles their JSON only; it does not run `grade.py`, candidates or Windows. [Normalized intake](../experiments/2026-11-15-sandbox-probes3-4-intake.json) pins all four artifact blobs.

| Saved artifact | Reconciled outcome |
|---|---|
| Probe 3 / runner revision 4 (`a1e3fca9`) | **8 planned sessions / 36 intended entries / 6 raw reports / 34 reporting entries.** Session 6 (`P_kill_runner`) is null after a 902.2-second deadline outcome; session 7 (`P_write`) is null and not started after the 3,161 MB sample. Both are `NOT JUDGED`; `probe_ok: false`. |
| Probe 4 / runner revision 5 (`40b9e3df`) | **8 reports / 36 entries; all 36 exit 3221225794 (`0xC0000142`), zero output and zero per-case records.** The author identifies this as DLL initialization failure. All references lack usable observations; 20 index outcomes mismatch, 16 are recorded expected, `probe_ok: false`. |
| Probe 4 reported protections | All 36 guest records say job/integrity as requested, and all eight sessions report protection fields/self-shutdown. These remain guest/host report evidence, not independent runtime inspection. No successful candidate attack was exercised, so the surviving runner session proves no protection against the prior attack. |

The fourth result is a harness-startup failure, **not a new model score**. Expected decoy failures in a run where references also fail are not a positive control for grading. Nothing is marked trusted in its published host verdict. Original draft observations remain unavailable; the author says they were not kept; preserve the provisional original 11/12.

**Revision 6** removes the Administrators deny-only token adjustment while retaining the runner DACL, low-integrity restricted token, fresh-handle check, progress and host rejection. Source blob: `89f72ff483598a7ca897236b1d46e3c077f98ffd`. The narrow code delta is read; the author's causal explanation is **an inference, not an established guest mechanism**. Host-only harmless checks and 262 suite tests are author-reported and cannot substitute for guest validation.

The fifth notice is handwritten-only, eight sessions and memory permitting; at the pin there is no completion evidence. The 12-draft hold stands, and return of a review is not automatic run clearance. Add this explicit source successor to the existing review, preserving older results at their tested revisions. No duplicate implementation, cloud probe, Actions job, PC/VM traffic, privilege change or candidate execution is performed here. Earlier artifact-request text below is historical now that the four files are published.

## Historical third-probe report and revision-5 notice — before saved artifacts

Claude's [`40b9e3df` turn](https://github.com/mms20102/Local-AI-tests/commit/40b9e3df294e184fee758b94b750d7d4371fd230) reports **`probe_ok: false`** for revision 4 (`a1e3fca9`). This is co-chat evidence, not a result independently rerun here. Eight sessions were planned: sessions 0–5 reported 34 entries with job/integrity fields and the expected reference/decoy outcomes; session 6 (`P_kill_runner`) again produced no report and reached the host deadline at roughly 902 seconds; session 7 (`P_write`) **was not started / not judged** because a 3,161 MB sample was below the 3,584 MB guard. Both unsuccessful outcomes remain in the plan.

Reported pipe collection was 1,048,606 bytes for `P_print_flood` and 1,114,112 for `P_output`. The author withdraws the claim that low integrity by itself protects the runner. Its separate harmless host handle check reportedly allowed terminate/query/synchronize and denied VM-write before the DACL change. These are author-reported observations, not a general Windows access-control conclusion independently established by this intake.

**Revision 5 is source under review:** runner blob `8d977c73fee366f99566aa665c0febcef790238f`; host blob `cc157efe91d9efba6a8205ef95836bb95cf28be3`. The author reports `protect_self` applies `D:P(A;;GA;;;SY)(A;;RC;;;OW)`, refuses candidates unless a fresh terminate-handle check is refused, adds Administrators as deny-only, writes progress traces, and requires the protection fields in the host report. The host-only handle/smoke checks and 262 suite tests without failures remain author reports. Guest efficacy is explicitly unknown; no general ACL, inherited-handle, report-share, collection or cleanup guarantee follows.

The pinned results directory still has only the original and second-probe files. [Co-chat follow-up](https://github.com/mms20102/Local-AI-tests/blob/53201042fd5cfb2d2ab2cb7b40eda7362b6683b9/research/co-chat.md) requests already-recorded third-probe summary/raw or partial reports/progress under distinct names, with the actual revision-4 run identity. Do not overwrite earlier evidence or synthesize reports for the failed/skipped sessions.

Residual `vmmemWindowsSandbox` and `vmwp` processes, empty environment listings and a listing-created server process are author reports. Their relationship to the sessions and full cleanup are unresolved. No elevation, extra inspection or termination follows from this relay. The fourth handwritten-only probe is announced **once memory permits**, not reported complete. Other same-user guest processes and shared-interpreter observation remain unresolved in the author's own account.

Include this explicit successor in the existing review; an older judge/token result does not clear revision 5. Preserve the 12-draft hold, the provisional 11/12 and all failure/skip outcomes. No new implementation, probe, PC/VM/runtime traffic, privilege change or cloud job was performed here.

## Historical runner revision 4 notice — before the failed probe

The author publishes [`a1e3fca9`](https://github.com/mms20102/Local-AI-tests/commit/a1e3fca9f6c21bfda680c5f3330a9bc16f588048) after a reported direct request to continue investigation, while explicitly retaining the no-rerun hold on the 12 model drafts. The commit changes the runner substantially; prior parser/exit-code review does not validate this new Windows lifecycle path. It belongs in the existing review handoff as an explicit successor, without silently treating an older pinned result as coverage.

**Author-reported implementation:** create a restricted token using `DISABLE_MAX_PRIVILEGE`, set low integrity SID `S-1-16-4096`, use `CreateProcessAsUserW`, check the suspended candidate's integrity and `IsProcessInJob` before resuming; host acceptance requires `in_job is True` and an exact integer integrity of 4096. Output now uses pipe collection and job termination at the output threshold, replacing the sampled file-size stop.

**Author-reported smoke only:** four harmless handwritten functions were tested on the host. A normal return reported the job/integrity values; an endless loop timed out; a 2 MiB print ended as output flood with **1,114,112 bytes collected**, equal to 1 MiB plus 65,536 bytes. This is not independently verified here or a general hard-cap guarantee. Distinguish collected, produced and buffered output, termination results and pipe EOF/cleanup. The author reports 261 suite tests without failures, not an independent execution result.

The third notice announces **eight guest sessions, handwritten references/decoys/fixtures only**, with twelve hostile fixtures. `P_kill_runner` now must return refusal while the runner survives, and new `P_write` tries report/work/Windows-temp/own-folder writes. No model drafts are reported staged/run; chat is reported untouched. At this pinned notice there is no completion evidence.

Focused review needs the actual token restrictions and handle inheritance, fail-closed checks before resume, pipe deadlines/EOF and retained-byte bound, job kill/close outcomes, and candidate access to the mapped report share. These are review questions, not claims of reproduced defects. Low-integrity report-share behavior is explicitly unknown in the author's notice; same-interpreter observations and session/process identification remain unresolved. No PC call, privilege change, draft run, cloud probe or duplicate implementation is made here.

## Narrow successor — type-strict exit check; no new Sandbox run

The [`cc2a3937` diff](https://github.com/mms20102/Local-AI-tests/commit/cc2a3937a7d668d3531ef8d4a6ff3f7df0c4bc56) changes only the host clean-exit predicate, its regression values and the append-only co-chat. This session read that exact diff: `type(item.get("exit_code")) is int` now precedes equality to zero; the existing test gains `False`, `0.0` and `"0"`. This addresses the source-level equality issue in the earlier `1f32bb4e` predicate. **No tests were executed here:** the 24 pure-test pass and the original raw reports containing only integer exits are author reports, not independent regression or runtime clearance. There was no new guest run, so the saved probe outcome is unchanged.

Carry this small delta into the existing focused successor review instead of starting another broad audit. Claude reports Mohamed directly instructed no rerun of the 12 drafts until that review returns; preserve the hold, and do not treat a review's return as automatic authorization for another run.

The later cleanup report says `wsb list` showed no running Sandbox while the same `vmmemWindowsSandbox` PID remained at about 1.6 GB. `hcsdiag list` was refused without administrator rights. These are Claude-reported observations; the process's relation to the sessions is unresolved and cleanup remains unverified. Do not infer permission to elevate or kill it. The original 11/12 result stays provisional; no PC or runtime action occurred here.

## Second handwritten probe — closed, with adverse evidence

[Completion artifacts `ca0d4d4a`](https://github.com/mms20102/Local-AI-tests/tree/ca0d4d4aa950aa2ec646ca0acc5cbee3c8bd9cc4/research/coding-quality-v1/sandbox/results) now include the summary and raw guest reports for the **handwritten probe only**. This session parsed/reconciled their JSON without executing any candidate, harness or guest. The original draft guest records were not kept; the author withdraws the inference that their shapes could be checked from the original summary. There is still no independent re-grading of the original 11/12.

- **Reconciled totals:** 7 sessions, 35 distinct intended entries, 6 raw guest reports and 34 reporting entries. The missing entry is `P_kill_runner`. The summary grades 12 references at 116/116 cases and all 12 decoys failing at least one case. Thirty-five `as expected` index outcomes and `probe_ok: true` include the successful denial of the runner; they are not 35 successful security properties.
- **Runner attack:** the author reports `P_kill_runner` used Windows process access to kill the guest runner. The host has no report, records 902.3 seconds to the deadline outcome and refuses that session. Resource jobs do not prevent access to other guest processes. Running non-plain fixtures alone mitigates this declared sample, but AST triage does not authenticate arbitrary candidates.
- **Output:** `P_print_flood` records 8,323,324 bytes, **4,129,020 above** the 4,194,304-byte sampled threshold. `P_output` records 20,971,608 bytes and exits 0 before the stop catches it; the separate read limit rejects its record. These are evidence that the stop is not a strict disk quota.
- **Cleanup/isolation:** six guest shutdowns are recorded. Empty lists for selected process image names do not resolve the author's separately observed `vmmemWindowsSandbox` process. All 34 `confined: true` fields are guest testimony, not independent enforcement observations. The host/guest observation and process-identification limitations remain.
- **Narrow pending source item:** `sandbox_host.py:192` at `1f32bb4e` accepts `exit_code == 0`, including malformed JSON `false` or `0.0`. A strict schema needs `type(exit_code) is int and exit_code == 0`; add pure negative tests. No occurrence of these malformed values is claimed in the saved reports.

[Normalized intake](../experiments/2026-11-15-sandbox-second-probe-intake.json) pins both artifact blobs and separates source/reported evidence. The existing independent reviewer is handling the focused source/regression comparison; no duplicate implementation or run is assigned here. The source repairs are not independently cleared by this intake. No new model run, PC traffic, runtime change, Actions job or cloud probe was performed. The original provisional score is unchanged.

## Historical successor notice — before probe completion

Claude confirms the false pass, withdraws the expected-answer-withholding guarantee, and publishes [`1f32bb4e`](https://github.com/mms20102/Local-AI-tests/tree/1f32bb4e6e0f47ae79d34404cf0816fbd044c7c2/research/coding-quality-v1). The findings below describe `377fae14`, not an independently verified assessment of its successor.

**Author-reported repairs:** strict case/record schemas and JSON parsing; positive exception/value matches; refusal of nonzero exits/capped output; exact four-check network fields; suspended child assigned to a one-process/1024 MB kill-on-close Windows job before resume; 10-second deadline and a polled output stop above 4 MiB; AST triage and eleven retained hostile fixtures. The author reports 261 suite tests without failures. This session source-counted **24 named pure regression methods**, but executed none.

| File | Successor Git blob |
|---|---|
| `grade.py` | `11cbe7f3724439e5fd51247b1c9889d788d1c156` |
| `test_judge_strict.py` | `bb783f34b9a10d0f0ff335b3e2247d1bf7e75fe5` |
| `sandbox/guest_runner.py` | `5eb3ea9ebc165002937b3e572e50f6c06365c774` |
| `sandbox/sandbox_host.py` | `65febbcc4ebefef2e641d949d828813fecfbf93d` |
| `sandbox/source_gate.py` | `59a8d31334a093d3dc279db7b56f2f4b58f94e49` |

The notice announces a second **handwritten-only** probe: 12 references, 12 decoys and 11 hostile fixtures across seven sessions, six non-plain fixtures alone. Chat is reported running but untouched; admission uses a 3584 MB available-memory sample. No model drafts are reported staged or rerun. At this pinned notice no completion evidence is available. A focused successor review should use the existing independent grading reviewer rather than duplicate the first audit.

Two points were returned in [co-chat](https://github.com/mms20102/Local-AI-tests/blob/e379571b6eb18e09ac6cbcc48376eec0ab37cd47/research/co-chat.md). File size is polled every 20 ms: 4 MiB is a **sampled stop threshold that can overshoot, not a strict quota**; the 1 MiB read limit is separate. Also, the original summary lacks raw per-case observations and cannot substantiate that all 112 passing records contained required fields. Archive sanitized original records if available; otherwise retain that claim only as an author-local observation. The original score stays provisional.

Shared-interpreter observations, process identification and guest-reported isolation remain explicitly unresolved. The Windows-job flags and source alone do not establish applied enforcement. The private cloud probe stays paused/private; no competing implementation, CI run or candidate execution occurred here. Claude's window-9 novelty correction is accepted and recorded.

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
