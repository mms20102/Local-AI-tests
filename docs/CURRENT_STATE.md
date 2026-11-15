# Current project state

Checkpoint: 2026-11-15. This page supersedes the early 27-test/incomplete-inventory status. The [earlier checkpoint](https://github.com/mms20102/Local-AI-tests/blob/3701d34729efb8fe7a174d2b48957709692fdfdb/docs/CURRENT_STATE.md) remains in history.

## Latest reviewed checkpoint — 2026-11-15 UTC

- **CODE-Q1 Windows experiment:** Claude now reports executing the 12 frozen first-pass drafts in Windows Sandbox, **11/12 tasks and 112/116 cases** passing (Arabic 3/3; English 8/9). The independent reviewer verifies input/source identities and recomputes the published totals, but cannot independently re-grade without raw per-case records. **This is a provisional author-reported experiment, not an independently accepted release grade.** A source-confirmed judge false-pass path, collection/lifecycle defects and the shared candidate/reporter boundary remain. The four reported F02 mutation failures agree with prior manual analysis. [Review](../research/audits/2026-11-15-windows-sandbox-grading-review.md) · [intake](../research/experiments/2026-11-15-windows-sandbox-grading-intake.json).
- **Next coding step:** strict parser/judge regression tests and accurate result/cap wording, then reviewed handwritten collection/lifecycle and observation checks. Preserve the original experiment and drafts; do not infer that general harness weaknesses prove these 12 drafts exploited them. The private cloud containment probe has 51 author/independent component-test passes but remains private and unlaunched; no competing CI or grading run is underway here.
- **Runtime window 9:** Claude reports it closed with Colibri 2.0/cap32 healthy. This side normalizes seven saved probes: four 200s with matching reported prompt-count pairs, two 422s and one 413. Teach18 loaded identity is still inferred; the status adapter remains reported unloaded. Profile-bound startup was already reported in window 8, so it is not new in window 9. Download contention and reported 61/stop versus 64/length variation preclude clean timing or a reproducibility conclusion. [Observation intake](../research/experiments/2026-11-15-window9-intake.json).
- **Scope:** no model draft, harness or probe was executed by this repository session; no PC/runtime/settings action, private-artifact publication, grading-gate change, PR merge or root-README rewrite was made. The independent review was relayed in [co-chat](https://github.com/mms20102/Local-AI-tests/blob/38e883281cc4abec27188f9d714e86603eb52d61/research/co-chat.md). Browser disclosure, stream accounting, live nonempty teaching and quiet correctness-qualified speed remain open.

Sections below preserve dated evidence and are historical where this checkpoint supersedes them.

## Historical reviewed checkpoint — 2026-11-14 UTC

Producer artifacts use the label 2026-11-15; source refs below define the checkpoint.

- **Scratch ASGI:** revision 2 at `bd7f005e` corrects settings-before-import bootstrap and guard placement. This side recomputed 27 saved assertion groups / 34 captures / zero detected internal-key captures; no independent rerun. Pre-first cancellation and spec-2.4 secondary error remain; the stage-3 exit gate is now corrected at `6ae83f76` as a source-only change with no rerun. [Completion review](../research/audits/2026-11-14-scratch-asgi-completion-review.md).
- **CODE-Q1:** the 12 first-pass drafts are approved/published at `afc71839`. The designated worker reports matching input hashes and **12/12 complete transport / structure pass**. Behavioral execution is **unassessed, denominator 12**, blocked by containment, not missing drafts. F02 has a source-derived mutation defect; no runtime score is inferred. [Readiness](../research/audits/2026-11-14-codeq1-grading-readiness.md).
- **Repository/CI:** the landing-page direction is accepted; dated updates stay here and in linked audits. GitHub run `43642451133` reports successful Ubuntu/Windows jobs, which is not arbitrary-candidate isolation. [Maintenance review](../research/audits/2026-11-14-repository-maintenance-review.md).
- **Scope:** no private capture artifact was rehosted, no draft executed by this repository session, no live settings changed, and PR #1 is not merged by this review. Browser status, streamed accounting, quiet timing and the remaining owner checks stay open.

Earlier checkpoint sections below remain historical where this summary supersedes them.


## Offline streaming-adapter checkpoint — revision 3 component pass

The existing focused review at `1ea5c6f6` passed **41 / 5 LiteLLM skips** under the explicit caller-close contract. Pre-first-pull, ordinary distinct-resource and close-originated cancellation cases pass; cancellation between pulls requires the caller's `finally: await stream.aclose()`. `uncertain` does not confirm release. [Versioned review](../research/teach-status-adapter-review.md).

Pinned source shows the standard LiteLLM response can propagate closure to the adapter, but actual ASGI disconnect/routing remains untested. [Cleanup-path audit](../research/context-preflight/litellm-stream-cleanup-source-audit.md). Reuse the existing capture work for actual proxy/ASGI boundaries; browser, nonstream and accounting remain separate. No duplicate receiver, registration or runtime change.


## Current integration checkpoint — after bounded teach15–18 review

The [checked shared-log source](https://github.com/mms20102/Local-AI-tests/blob/8ef7d5057aef98bc1d5c59a938b5b36c7cf2e897/research/co-chat.md) reports Colibri 2.0/cap32, the gateway token counter active since window 7 and teach rev11 loaded by inference from source present at startup. Later revisions remain reported offline/not loaded at this checkpoint. This is shared-log evidence, not a new PC observation; an absent window notice does not prove the service idle.

- **Bounded independent reviews:** reason codes at `be282e3`: **24 passed / 6 tokenizer skips**; teach15–18 at `8ef7d505`: **104 passed / 5 skips**, plus 45 synthetic matrix cases. These coordinator-relayed results found no new blocking defect in the tested paths. Proxy checks used a stub rather than HTTP serialization.
- **Reported operating decision:** Claude relays Mohamed retaining absent-counter byte-only notes and accepting the 32-token margin and launcher-report limitations, with one coordinated restart after the bounded review. Policy acceptance does not prove a native-token bound or engine identity, and does not independently authorize this session to operate the laptop.
- **Visible status:** Open WebUI 0.13.3 / LiteLLM 1.108.5 and plain provider configuration are Claude-reported. Functions are disabled; no response hook or omission notice is implemented. The pinned transport is being checked before choosing a bridge.
- **Coding progress:** 12 exploratory CODE-Q1 answers reportedly stopped and passed static structure checks; semantic grades and first-useful-text/correctness-qualified timings remain unmeasured. [Aggregate record](../research/experiments/2026-11-14-codeq1-exploratory-first-pass.json).
- **Still unverified:** actual loaded engine/callback identity, real tokenizer/profile agreement, exact final enriched wire payload, user-visible omission disclosure, live equivalence/adherence and the release quality/speed checks.

The remaining sections preserve earlier evidence and historical checkpoints. Their round-27 current-state or pending-policy wording is superseded here. **Latest coordination notice:** [runtime window 8 closure](https://github.com/mms20102/Local-AI-tests/blob/370b6765feb4a1a5507334143eeaa575ad064092/research/co-chat.md) is Claude-reported. [Artifact normalization](../research/window8-observation-intake.md) recomputes **20 session + 5 probe + 3 network-request records**, not a 20-request total for the whole window. Stop-file cycles/session and selected HTTP/count observations advanced; exact loaded hook, live nonempty notes, Ctrl+C, semantic quality and clean speed remain unverified. Closure is not a request for new traffic.

Pinned-source research has since found a streaming provider-event candidate that may work without enabling Functions; [contract](../research/teach-status-display-contract.md). It is not a deployed/tested bridge, and the nonstream path remains open. No runtime, hook, configuration or user-note change was made by this reconciliation.

## Earlier completed evidence milestones

- The sanitized briefing is published and Claude has supplied genuine responses through round 29. The [active co-chat](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md) is on Claude's branch, not main.
- The original independent reviewer checked teach revision 6 at [015a2ec](https://github.com/mms20102/Local-AI-tests/tree/015a2ecd63468445b9ebed1f01b95291fa577177/research/teach-store). Source hashes were verified and AST comparison found no executable changes from revision 5. Linux/Python 3.12.14: **73 collected, 72 passed, 1 skipped** on disposable synthetic stores, including POSIX separate-process lock/recovery and killed-holder cases. The skipped test requires unpublished private gateway configuration. This is the offline persistence milestone only.
- Claude independently ran **65 planner tests** on [schema 4](https://github.com/mms20102/Local-AI-tests/tree/974e667cfdcc389a56797f042dcb61cc13d435be/research/planners/cap4-cap32-schema4). It plans and validates evidence; `--run --maintenance` refuses.
- CODE-Q1 fixture revision 2 contains 12 tasks and 116 authored cases. Claude reports 31 grader tests passing. The semantic command consults the disabled manifest gate. A child process/acknowledgement flag is not a verified sandbox; behavioral reporting still shares the candidate process.
- The [context input audit](../research/context-preflight/README.md) matches 25 CODE-Q1 prompt/reference Git blobs. Claude's external preflight reports 118–300 input and 31–137 reference tokens; its native fields remain unknown. A separate round-29 [sanitized saved-usage audit](../research/context-preflight/saved-usage-parity-audit-2026-11-14.md) recomputes 24/24 matching totals (68–261), zero observed net delta, and nine length-ended rows at 256. This near-ASCII, two-message Colibri 2.0 dataset does not establish gateway provenance, universal parity, separate added-token counts or the location of the output cap. System-byte metadata and ratio labeling remain unresolved; no restricted trial text was read.

Independent test outcomes above were relayed by the coordinator. This repository session read the source/messages and published evidence; it did not perform those Python runs.

## Laptop observations, with provenance

The PC worker's read-only inventory and Claude's independent observations report Windows, Ryzen 9 7940HS, 23.22 GiB usable host RAM and RTX 4070 Laptop 8188 MiB. Modules are 16 + 8 GB DDR5. See [I001](../research/experiments/2026-11-14-pc-inventory.json) and the active co-chat.

At the last verified configuration checkpoint: Colibri 2.0.0/Vulkan; `--ctx 2048 --cap 32 --ngen 256 --no-think --temp 0 --max-queue 1 --kv-slots 1 --no-tune-profile`; tier 3 GiB and OMP threads 8. Historical comparison arm is cap 4. The model is reported as `Kreuzzelg/qwen36-35b-a3b-colibri-i4-gs64`, mutable revision main. An independently pinned installed model/engine identity is still a run prerequisite.

Host-wide snapshots showed roughly 5.85 GiB available RAM but only 0.94–0.96 GiB commit headroom. Those are dated samples, not current live clearance or peak attribution. Check **commit, physical and GPU** headroom; free RAM alone does not approve cap/context/tier increases.

## Operational implementation: progress is not run readiness

The PC worker reported read-only collection/admission, bounded SSE deadlines/cancellation and retained partial output, and immutable before-send/result journals. Its 109-test checkpoint included stalled-socket tests; these are worker-reported and not independently rerun here.

A later 18-file local commit is reported preserved. Publishing benchmark components was denied because automatic approval review could not verify authorization context, including after direct approval. No branch was created; **do not retry or upload those components by another route**. This documentation update contains none of that code.

The latest explicit implementation checkpoint still had one-arm lifecycle/identity gates underway and the full benchmark disabled. Obtain a new worker checkpoint rather than inferring completion from test totals. This session has no usable PC/local execution shell; a shell check still reports no usable execution environment.

## Remaining evidence gaps

- The frozen schema-4 study has not completed, and no causal lookup speedup is established. The separately audited exploratory cap4/cap32 result below exists; its recorded timing reduction is not a semantic-quality or controlled general-workload result.
- No current full-stack UI call-count result; the previous UI attempt was blocked before input.
- Claude reports the hook enabled and gateway invocation observed in windows 5–6. Independent current live configuration, exact loaded callback code, whole-pipeline/wire equivalence and broad adherence remain unverified; the former hook-off checkpoint is superseded as a current-state claim.
- Renderer-only token fit is reported; binary-added tokens and full-engine overhead/context fit remain unverified.
- No independently accepted CODE-Q1 semantic release grade; the later Windows experiment is reported and audited above.
- No power-loss guarantee; broader crash scenarios remain outside the tested scope.
- No larger cache/context, replacement model, RAM purchase or dependency upgrade adopted from research alone.

## Historical preparation checkpoint — rounds 22–24

This section records what was known before the later runtime windows. In particular, round 24's “not started” applies to that checkpoint only; subsequent windows 1–3 report 2.1 starts and restoration. Current teach status is summarized above.

Claude completed the **tokenizer-only preflight** in rounds 22–23 using existing assets. The installed nonthinking renderer adds four tokens beyond his earlier plain-ChatML assumption. The reported maximum input plus a 256-output reservation is 556; binary-added tokens remain null. See the [normalized observation](../research/context-preflight/reported-renderer-preflight.json). Do not generate traffic just to fill that field; validate against usage during a later otherwise-authorized request. This repository session contributes source/fixture review and project-map updates; the PC worker coordinates runtime work.

At round 24, Claude additionally reported Colibri 2.1.0 extracted beside 2.0.0 and not yet started, plus a launcher version selector added to worker-owned workbench.py at local commit cf4d369. This changes that file's previous checksum. The PC worker must reconcile the local diff/manifest before use. The published release asset size/digest matches Claude's report, but laptop installation/source behavior was not independently checked here. No update was installed or run by this session; [version/security verification](../research/VERSION_VERIFICATION_2026-11-14.md) records the boundaries.

Follow the [current worker packet](../research/PC_TEST_REQUEST.md). Offline progress does not authorize live activation.

## Historical window 1 — first-start observations, not a comparison

Claude explicitly closed the window in co-chat at commit 6570684cc325930263645797888483db37fac18d. He reports a 2.1 startup check and two completed small synthetic drafts, followed by stopping 2.1, restoring 2.0 and completing one draft. These outcomes have not been independently verified by this repository session.

The reported 2.1 snapshot was 34.64/35.29 GiB committed and 2.49 GiB available, with requested cap 32 reduced to effective cap 8 and a roughly 5 GiB host pool in the engine log. The restored 2.0 snapshot was 28.14/32.22 GiB committed and 9.16 GiB available. They are single samples from different cache/warm-up states, not peaks or a speed/memory benchmark. A changed commit limit alone does not independently establish pagefile growth. See the [sanitized reported observation](../research/experiments/2026-11-14-colibri-2.1-first-start-reported.json).

After window 1, a coordinator-scoped read-only inspection handoff covered the launcher/working-tree diff, native executable identity, stale workbench checksum, existing test evidence and a resource snapshot. Later runtime reservations superseded that handoff; the dated independent inspection after window 3 is below. The hook was **off at this pre-trial checkpoint**; windows 5–6 later reported activation. This historical entry is not current port/runtime clearance, and this repository session still has no usable PC shell.

## Historical independent PC checkpoint — after window 3, 14:22 UTC

The PC worker independently inspected after confirming window 3 closed. At that inspection the running native engine was **Colibri 2.0.0**, its binary hash matched the prior verified baseline, and no 2.1 process remained. Ports 8000/4001/8080 were listening. The local working tree was clean at `7111656`; launcher changes were in `cf4d369`, `d9aadbf` and `7111656`. Original launchers were unchanged, matched recorded hashes and selected 2.0; the separate 2.1 launcher selected host-pool-off. These are dated findings, not a claim about later source/configuration state.

At **14:22 UTC**, available RAM was **6.10 GiB** and commit headroom **1.33 GiB**. These are single samples, not peaks or clearance for a larger configuration. No tests were rerun and no laptop changes were made. This is independent PC-worker evidence relayed by the coordinator, not a local execution performed in this repository session.

**Trust metadata is still pending:** workbench's actual SHA-256 is `00576b971bd7b9b8e8a70fe77c9ac9563a24e5e36705beeb39f02f2d6b7f8512`, versus manifest `7385b3966d99380ffea826a4bbd99335a6f32f4a170073627f8f70fd56c1f462`. The separate 2.1 launcher has no manifest entry. Do not blindly replace these hashes: the [review packet](../research/MANIFEST_REVIEW_2026-11-14.md) scopes baseline/diff review and a local candidate only. See [machine-readable evidence](../research/experiments/2026-11-14-post-window3-independent-inspection.json).

Claude's preceding short 2.1 tests remain preliminary author observations. Window 3's flat sampled memory does not prove a leak or its absence, and fixed-order repeated tasks do not establish a controlled speed difference. Independent restoration/hash inspection does not turn those timings into a benchmark.

The hook was off at that window-3 checkpoint, before the reported window-5 activation. No further runtime test, restart, version switch, manifest rewrite or rejected-publication retry is authorized by that historical inspection. Recheck the active co-chat for any later reservation before local work.

## Historical offline launcher-diff review follow-up

The independent review of captured `7111656` diffs found the intended constrained/default-2.0 choices, child-only 2.1 override and unchanged original launchers, with no new command-injection, credential or network issue apparent in that scope. It supplies the missing new-launcher digest as a **snapshot candidate**. No PC access or write occurred during window 4, and no independent test pass is tied to the exact commit. See [the review evidence](../research/experiments/2026-11-14-launcher-diff-review-7111656.json).

Source/binary trust is not renewed automatically: file existence is not binary identity. After window 4 explicitly closes, recheck current source/commits/hashes against that snapshot and review any drift before applying anything. The live manifest remains unchanged.

## Historical window 4 — exploratory result audit

The [independent offline audit](../research/audits/cap4-cap32-exploratory-audit-2026-11-14.md) reproduces 962.24 s at cap4 versus 704.99 s at cap32, a 26.7345% reduction in recorded helper completion time. All 48 scored rows record complete/stop/not-truncated and static pass; those grades were not independently rerun because outputs are not published.

The observation is AB followed by a separate BA invocation: the first artifact remains aborted with restoration false after the UI hang; the second reports complete/restoration true. Current published driver contains a fallback reportedly added between invocations. This is not one clean batch or the full schema-4 plan, and no semantic quality/token-throughput/general-workload claim is established. Post-run cap32 commit-headroom samples were 0.62 and 0.81 GiB; no peaks/per-request surveillance were recorded. Original artifacts are preserved.

## Historical window 5 — reported teach activation and rev7 findings

At [the window-5 closure snapshot](https://github.com/mms20102/Local-AI-tests/blob/619f21764409fd9f80d6111011554f16fc934f9c/research/co-chat.md), Claude reports 2.0/cap32 healthy and the hook **enabled with an empty store**, local revision-7 commit 0783706. This supersedes the historical hook-off status for future identity records; actual current hook/store/live-pipeline state is not independently verified here. Check for any newer runtime reservation before PC work.

The coordinator relayed independent rev7 offline review: 74 tests collected, 72 passed, 2 skipped; a separate reproduced logging path raises BrokenPipeError into requests even with empty notes, outside the intended fail-open guard. A concurrent store edit can make the log fingerprint disagree with the snapshot actually selected/injected. A direct empty-store callback returned the identical request object, which does not establish full live pipeline invariance. “Nothing added” logs and similar answers alone are insufficient for that claim.

The findings were sent to Claude for a focused offline fix and exact-diff independent review. No runtime/hook/configuration change or additional probe is requested by that handoff. Preserve all real user notes and backups; do not assume emptiness or purge to prepare a repair. Future benchmark identity must include callback configuration, hook source and store snapshot. The repository session has no PC shell and has performed no activation or candidate-code execution.

## Historical revision-8 offline review — not deployment

The original reviewer checked published rev8 at acd56099794edab9da4b2200a521e23b9150321f: 76 passed, 4 skipped offline, plus synthetic broken/closed stdout and concurrent-edit snapshot checks. The previous two findings are fixed in the tested normal-store scope. Remaining limits: log-line formatting is outside safe_log and malformed non-string ids can raise; blocked stdout can still delay the callback; live LiteLLM configuration/deployment is unverified and the snapshot README has contradictory hook status. At that offline checkpoint, Claude reported the gateway still running rev7. The later window-6 restart report supersedes that report, without independently establishing the exact loaded code. Offline hardening/documentation was requested without restart, configuration change or touching user notes. No live fix is claimed.

## Reported window-6 closure and revision-9 offline checkpoint

Claude explicitly reports window 6 closed, 2.0/cap32 healthy, callback enabled and no active notes, claiming rev9 loaded. This supersedes earlier “still rev7” reports as a deployment claim, **not** as independent loaded-code verification. A store-hash line can be consistent with rev8 or rev9 and does not identify exact callback code. Actual loaded revision, live configuration and whole-pipeline invariance remain independently unverified.

The original reviewer checked rev9 at 3ac4a3e460cfbfcf8f501edd154be4def1e032db: **77 passed, 5 skipped** offline, with targeted malformed-id, broken/closed-stream and snapshot checks passing; formatting and output are guarded. Remaining limits: arbitrary malformed ids coerced with str() can disclose unexpected diagnostic text; synchronous I/O can delay callbacks; snapshot status documentation needs reconciliation. Focused offline ID validation/redaction and documentation were requested through co-chat. No duplicate review, runtime restart, hook/configuration change or user-note edit/purge was requested.

The exploratory cap audit and its original hook-off evidence remain unchanged. Future benchmarks must record actual callback configuration, source/loaded-identity evidence and store snapshot. Always check for a later runtime reservation before local work.

## Revision-10 independent offline checkpoint

The original reviewer checked exact published source fd962cc2060c5bde7b1cce01f85991d7acaf16e7: **78 passed, 5 skipped** offline. Targeted canary, malformed-id/fingerprint and logging checks passed; no blocking regression was found within that scope. See [the review record](../research/experiments/2026-11-14-teach-rev10-independent-offline-review.json).

The validation restricts diagnostic output shape; it does not prove an id was actually issued. Invalid values are counted rather than echoed. Synchronous writes may still block. This offline result does not test live LiteLLM configuration or prove whole-pipeline/wire invariance.

Rounds 26–27 last report rev10 as published/on disk but not loaded, with no further runtime change in round 27. Exact active callback identity remains independently unverified; the review does not authorize or perform a restart/deployment. The qualified result was relayed to Claude without another code-change or live-test request. All user notes, source and prior evidence remain preserved.
