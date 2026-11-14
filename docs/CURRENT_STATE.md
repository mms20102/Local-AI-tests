# Current project state

Checkpoint: 2026-11-14. This page supersedes the early 27-test/incomplete-inventory status. The [earlier checkpoint](https://github.com/mms20102/Local-AI-tests/blob/3701d34729efb8fe7a174d2b48957709692fdfdb/docs/CURRENT_STATE.md) remains in history.

## Completed evidence milestones

- The sanitized briefing is published and Claude has supplied genuine responses through round 24. The [active co-chat](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md) is on Claude's branch, not main.
- The original independent reviewer checked teach revision 6 at [015a2ec](https://github.com/mms20102/Local-AI-tests/tree/015a2ecd63468445b9ebed1f01b95291fa577177/research/teach-store). Source hashes were verified and AST comparison found no executable changes from revision 5. Linux/Python 3.12.14: **73 collected, 72 passed, 1 skipped** on disposable synthetic stores, including POSIX separate-process lock/recovery and killed-holder cases. The skipped test requires unpublished private gateway configuration. This is the offline persistence milestone only.
- Claude independently ran **65 planner tests** on [schema 4](https://github.com/mms20102/Local-AI-tests/tree/974e667cfdcc389a56797f042dcb61cc13d435be/research/planners/cap4-cap32-schema4). It plans and validates evidence; `--run --maintenance` refuses.
- CODE-Q1 fixture revision 2 contains 12 tasks and 116 authored cases. Claude reports 31 grader tests passing. The semantic command consults the disabled manifest gate. A child process/acknowledgement flag is not a verified sandbox; behavioral reporting still shares the candidate process.
- The new [context input audit](../research/context-preflight/README.md) reads all 12 prompts and 13 reference files and matches their Git blobs to one pinned source commit. Claude's subsequent installed-renderer preflight reports 118–300 input and 31–137 fenced-reference tokens including one end token; binary-added tokens remain unknown. The source/size/arithmetic checks are independently cross-checked here, not the tokenizer run.

Independent test outcomes above were relayed by the coordinator. This repository session read the source/messages and published evidence; it did not perform those Python runs.

## Laptop observations, with provenance

The PC worker's read-only inventory and Claude's independent observations report Windows, Ryzen 9 7940HS, 23.22 GiB usable host RAM and RTX 4070 Laptop 8188 MiB. Modules are 16 + 8 GB DDR5. See [I001](../research/experiments/2026-11-14-pc-inventory.json) and the active co-chat.

At the last verified configuration checkpoint: Colibri 2.0.0/Vulkan; `--ctx 2048 --cap 32 --ngen 256 --no-think --temp 0 --max-queue 1 --kv-slots 1 --no-tune-profile`; tier 3 GiB and OMP threads 8. Historical comparison arm is cap 4. The model is reported as `Kreuzzelg/qwen36-35b-a3b-colibri-i4-gs64`, mutable revision main. An independently pinned installed model/engine identity is still a run prerequisite.

Host-wide snapshots showed roughly 5.85 GiB available RAM but only 0.94–0.96 GiB commit headroom. Those are dated samples, not current live clearance or peak attribution. Check **commit, physical and GPU** headroom; free RAM alone does not approve cap/context/tier increases.

## Operational implementation: progress is not run readiness

The PC worker reported read-only collection/admission, bounded SSE deadlines/cancellation and retained partial output, and immutable before-send/result journals. Its 109-test checkpoint included stalled-socket tests; these are worker-reported and not independently rerun here.

A later 18-file local commit is reported preserved. Publishing benchmark components was denied because automatic approval review could not verify authorization context, including after direct approval. No branch was created; **do not retry or upload those components by another route**. This documentation update contains none of that code.

The latest explicit implementation checkpoint still had one-arm lifecycle/identity gates underway and the full benchmark disabled. Obtain a new worker checkpoint rather than inferring completion from test totals. This session has no usable PC/local execution shell; a shell check still reports no usable execution environment.

## What has not been established

- No completed, controlled cap4/cap32 batch or causal lookup speedup.
- No current full-stack UI call-count result; the previous UI attempt was blocked before input.
- Teach hook remains **off**; callback invocation and model adherence are unverified. Renderer-only token fit is reported; full-engine overhead/context fit remains unverified.
- No sandboxed semantic assessment of model-generated code or CODE-Q1 model pass rate.
- No power-loss guarantee; broader crash scenarios remain outside the tested scope.
- No larger cache/context, replacement model, RAM purchase or dependency upgrade adopted from research alone.

## Active next step

Claude completed the **tokenizer-only preflight** in rounds 22–23 using existing assets. The installed nonthinking renderer adds four tokens beyond his earlier plain-ChatML assumption. The reported maximum input plus a 256-output reservation is 556; binary-added tokens remain null. See the [normalized observation](../research/context-preflight/reported-renderer-preflight.json). Do not generate traffic just to fill that field; validate against usage during a later otherwise-authorized request. Codex owns this source/fixture audit and current project map; the PC worker retains runtime ownership.

Round 24 additionally reports Colibri 2.1.0 extracted beside 2.0.0, not started, plus a launcher version selector added to worker-owned workbench.py at local commit cf4d369. This changes that file's previous checksum. The PC worker must reconcile the local diff/manifest before use. The published release asset size/digest matches Claude's report, but laptop installation/source behavior was not independently checked here. No update was installed or run by this session; [version/security verification](../research/VERSION_VERIFICATION_2026-11-14.md) records the boundaries.

Follow the [current worker packet](../research/PC_TEST_REQUEST.md). Offline progress does not authorize live activation.

## Runtime window closed: first-start observations, not a comparison

Claude explicitly closed the window in co-chat at commit 6570684cc325930263645797888483db37fac18d. He reports a 2.1 startup check and two completed small synthetic drafts, followed by stopping 2.1, restoring 2.0 and completing one draft. These outcomes have not been independently verified by this repository session.

The reported 2.1 snapshot was 34.64/35.29 GiB committed and 2.49 GiB available, with requested cap 32 reduced to effective cap 8 and a roughly 5 GiB host pool in the engine log. The restored 2.0 snapshot was 28.14/32.22 GiB committed and 9.16 GiB available. They are single samples from different cache/warm-up states, not peaks or a speed/memory benchmark. A changed commit limit alone does not independently establish pagefile growth. See the [sanitized reported observation](../research/experiments/2026-11-14-colibri-2.1-first-start-reported.json).

Only the coordinator-scoped read-only PC-worker inspection has resumed: actual launcher/working-tree diff, current native executable identity, stale workbench checksum, existing test evidence and a fresh resource snapshot. No new model request, runtime test, restart, version switch or host-pool tuning is requested. This session still has no usable PC shell. Hook remains off; restoration and launcher/test identities await independent worker evidence.

## Latest independent PC checkpoint after window 3

The PC worker independently inspected after confirming window 3 closed. Running native engine is **Colibri 2.0.0**, with its binary hash matching the prior verified baseline; no 2.1 process remains. Ports 8000/4001/8080 listen. The local working tree is clean at `7111656`; launcher changes are in `cf4d369`, `d9aadbf` and `7111656`. Original launchers are unchanged, match recorded hashes and select 2.0; the separate 2.1 launcher selects host-pool-off.

At **14:22 UTC**, available RAM was **6.10 GiB** and commit headroom **1.33 GiB**. These are single samples, not peaks or clearance for a larger configuration. No tests were rerun and no laptop changes were made. This is independent PC-worker evidence relayed by the coordinator, not a local execution performed in this repository session.

**Trust metadata is still pending:** workbench's actual SHA-256 is `00576b971bd7b9b8e8a70fe77c9ac9563a24e5e36705beeb39f02f2d6b7f8512`, versus manifest `7385b3966d99380ffea826a4bbd99335a6f32f4a170073627f8f70fd56c1f462`. The separate 2.1 launcher has no manifest entry. Do not blindly replace these hashes: the [review packet](../research/MANIFEST_REVIEW_2026-11-14.md) scopes baseline/diff review and a local candidate only. See [machine-readable evidence](../research/experiments/2026-11-14-post-window3-independent-inspection.json).

Claude's preceding short 2.1 tests remain preliminary author observations. Window 3's flat sampled memory does not prove a leak or its absence, and fixed-order repeated tasks do not establish a controlled speed difference. Independent restoration/hash inspection does not turn those timings into a benchmark.

Hook stays off. No further runtime test, restart, version switch, manifest rewrite or rejected-publication retry is authorized by this checkpoint. Recheck the active co-chat for any later reservation before inspection.

## Offline launcher-diff review follow-up

The independent review of captured `7111656` diffs found the intended constrained/default-2.0 choices, child-only 2.1 override and unchanged original launchers, with no new command-injection, credential or network issue apparent in that scope. It supplies the missing new-launcher digest as a **snapshot candidate**. No PC access or write occurred during window 4, and no independent test pass is tied to the exact commit. See [the review evidence](../research/experiments/2026-11-14-launcher-diff-review-7111656.json).

Source/binary trust is not renewed automatically: file existence is not binary identity. After window 4 explicitly closes, recheck current source/commits/hashes against that snapshot and review any drift before applying anything. The live manifest remains unchanged.

## Exploratory window-4 audit

The [independent offline audit](../research/audits/cap4-cap32-exploratory-audit-2026-11-14.md) reproduces 962.24 s at cap4 versus 704.99 s at cap32, a 26.7345% reduction in recorded helper completion time. All 48 scored rows record complete/stop/not-truncated and static pass; those grades were not independently rerun because outputs are not published.

The observation is AB followed by a separate BA invocation: the first artifact remains aborted with restoration false after the UI hang; the second reports complete/restoration true. Current published driver contains a fallback reportedly added between invocations. This is not one clean batch or the full schema-4 plan, and no semantic quality/token-throughput/general-workload claim is established. Post-run cap32 commit-headroom samples were 0.62 and 0.81 GiB; no peaks/per-request surveillance were recorded. Original artifacts are preserved.

## Latest reported window-5 teach state and independent offline findings

At [the window-5 closure snapshot](https://github.com/mms20102/Local-AI-tests/blob/619f21764409fd9f80d6111011554f16fc934f9c/research/co-chat.md), Claude reports 2.0/cap32 healthy and the hook **enabled with an empty store**, local revision-7 commit 0783706. This supersedes the historical hook-off status for future identity records; actual current hook/store/live-pipeline state is not independently verified here. Check for any newer runtime reservation before PC work.

The coordinator relayed independent rev7 offline review: 74 tests collected, 72 passed, 2 skipped; a separate reproduced logging path raises BrokenPipeError into requests even with empty notes, outside the intended fail-open guard. A concurrent store edit can make the log fingerprint disagree with the snapshot actually selected/injected. A direct empty-store callback returned the identical request object, which does not establish full live pipeline invariance. “Nothing added” logs and similar answers alone are insufficient for that claim.

The findings were sent to Claude for a focused offline fix and exact-diff independent review. No runtime/hook/configuration change or additional probe is requested by that handoff. Preserve all real user notes and backups; do not assume emptiness or purge to prepare a repair. Future benchmark identity must include callback configuration, hook source and store snapshot. The repository session has no PC shell and has performed no activation or candidate-code execution.

## Revision-8 offline review, not deployment

The original reviewer checked published rev8 at acd56099794edab9da4b2200a521e23b9150321f: 76 passed, 4 skipped offline, plus synthetic broken/closed stdout and concurrent-edit snapshot checks. The previous two findings are fixed in the tested normal-store scope. Remaining limits: log-line formatting is outside safe_log and malformed non-string ids can raise; blocked stdout can still delay the callback; live LiteLLM configuration/deployment is unverified and the snapshot README has contradictory hook status. The gateway is reportedly still running rev7. Offline hardening/documentation was requested without restart, configuration change or touching user notes. No live fix is claimed.
