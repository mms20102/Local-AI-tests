# Shared finish line for the local AI workbench

Status: **proposal for joint agreement**, 2026-11-14. Built from Mohamed's instruction and [Claude's six-check proposal](https://github.com/mms20102/Local-AI-tests/blob/5479e9e104f4a2d9d8ab177ec850dd8aa8fe55db/research/co-chat.md), with the amendments below. The [later offline-progress report](https://github.com/mms20102/Local-AI-tests/blob/829d3228438034b3126a2eac419517d1760db239/research/co-chat.md) is considered separately from deployment. Claude has not yet accepted these amendments. Numeric thresholds are proposed first-release targets, not demonstrated results or vendor standards. Mohamed can change the scope and targets.

## One final goal

**Give Mohamed a private local assistant he can use every day for routine coding in Arabic or English: complete, reviewable answers; demonstrated correctness on a declared task set; useful response times; editable teaching notes; and simple, recoverable operation on his existing laptop, without a required inference subscription.**

The first release is bounded to the tested languages, tools, request shapes and context. It makes its limits visible. A request beyond those limits receives a clear response rather than an invented success.

The laptop checkpoint is 23.22 GiB usable RAM and an RTX 4070 Laptop with about 8 GiB VRAM. Installed model/runtime identity and current resource headroom still need evidence before a controlled live check. This goal does not assume more hardware or a replacement model.

## Six proposed completion checks

| Check | Proposed first-release acceptance |
|---|---|
| **1. Useful context, with a complete answer allowance** | Count the exact rendered request, including system/helper text, history, tools and active notes, for every supported profile. Reserve the full requested output allowance. Test English and Arabic, below/at/above the actual admission boundary; a supported approximately 1,700-token prompt with a 256-token answer allowance is an example at context 2,048, subject to the declared uncertainty allowance. Unknown profiles/counts are refused clearly. Never silently rely on engine output clamping or promise unlimited history. |
| **2. Demonstrated coding usefulness** | Freeze the 12-task CODE-Q1 revision, grading rules, output budgets and run identity before drafts. Proposed bar: **at least 9/12 fully passing on the first attempt**, with no task category entirely failing; publish first-attempt and any repair results separately. Each pass requires all declared static and behavioral checks for that task, using reviewed isolation/external judging. Truncations, refusals, errors and timeouts remain in the 12-task denominator. Report Arabic/English results separately. A pass-rate table alone is insufficient if the target is missed. |
| **3. Useful measured speed** | On the same declared task set and quiet, admitted hardware profile: proposed **median first useful text ≤15 seconds**, **median end-to-end task time ≤60 seconds**, and **at least 9/12 correct complete outputs within 120 seconds each**. Failures/no useful text receive the 120-second penalty in release summary calculations rather than disappearing. Report raw durations, p90, queue time, cold startup and retry costs separately; do not mix cold/warm or partial outputs. Choose a configuration meeting the bar; do not claim globally best speed. |
| **4. Everyday start, stop and recovery** | Three recorded start–stop–start cycles and a 20-request bounded synthetic session, including cancellation and a deliberate refusal: no unhandled crash, hung request, unrelated-process termination or lost user notes. Verify expected executable/process/service identities and documented recovery. Deliver a short guide so Mohamed can operate it without an assistant. Deadlines and recovery checks must be explicit before the session. |
| **5. Teaching with visible limits** | Verify the actual loaded callback revision independently. Close the concrete malformed-ID count and synchronous-I/O/documentation findings. Freeze a disposable-store matrix with at least four English and four Arabic teaching cases plus empty-store and conflicting/untrusted-note cases. All declared contract checks must pass; report model adherence separately from payload equivalence, timing and persistence. Notes remain inspectable/editable; historical deletion/backups/purge limits are explained accurately. No real user store is used for these tests. |
| **6. Private, bounded operation** | The tested inference path uses the intended local endpoint, with no external model fallback or automatic upload of prompts, code, notes or raw logs. Use synthetic canaries/configuration review and observed destination evidence for the tested path; state the scope. Generated code is never executed on the normal host. Reviewed isolated grading and explicit resource/timeout checks come first. Preserve the prior working configuration and user data; no blind checksum renewal or broad process killing. |

These thresholds are small-workload release checks, not statistical proof of general intelligence or arbitrary-repository reliability. If the model misses the quality/speed bar, report the failure and try a bounded improvement; do not lower the bar after inspecting results merely to declare completion.

## Admission when the count is uncertain

For a supported, pinned profile, let `P` be the exact native-compatible count or a **proven conservative upper bound**, `R` the full desired output reservation, `U` a justified bounded uncertainty allowance, and `C` the effective context capacity. Admit only when `P + R + U ≤ C`.

- If tokenizer/renderer/model identity, middleware contribution, history/tool/note serialization or uncertainty is unsupported/unbounded, refuse before sending with an actionable message: this profile cannot yet be counted safely; shorten it or use a validated profile.
- Do not invent `U`, divide bytes by an average, silently drop context/notes or reduce `R`. A known conservative fallback must be labeled; it is not a measured exact count.
- Validate boundary/Unicode/whitespace/special-token cases offline. The [24 saved pairs](context-preflight/saved-usage-parity-audit-2026-11-14.md) support net agreement only for the near-ASCII two-message profile, not universal native parity.
- A later ordinary or coordinated synthetic request can provide additional evidence; no traffic is created by this document.

## Prioritized path to the finish line

1. **Agree this contract, then stop expanding it.** Claude can amend the targets/profile and record agreement. Record the remaining user choices below rather than treating a proposal as permission for live changes.
2. **Review the prepared gateway/teaching improvements offline.** Claude now reports proposed gateway commit `28753be` written locally, unpublished and not loaded, awaiting Mohamed's publication approval. This document neither obtains nor reviews that restricted unpublished source. A byte-first path/fallback needs its own conservative-bound proof for the final serialized request, and an arbitrary 32-token margin does not establish Arabic/history/notes safety. Verify counting relative to actual hook injection when an authorized diff is available. Claude also reports teach rev11 (`d5b6c16`) published, not loaded. The coordinator relays the [independent rev11 review](experiments/2026-11-14-teach-rev11-independent-offline-review.json) pinned at `829d3228438034b3126a2eac419517d1760db239`: 80 passed / 5 skipped offline, with targeted exclusion/preservation/logging/snapshot checks passing. Three attempts add at most 100 ms programmed sleeps, not a filesystem/logging wall-time bound. Shape validation is not issued-ID provenance; 10-digit IDs are filtered and other corrupt fields may fail-open the entire injection. No live loading is verified; no duplicate review or restart is requested. Keep both changes distinct from the running system.
3. **Review one concrete Windows grading design.** See [the Windows isolation proposal](WINDOWS_ISOLATION_PROPOSAL.md). Prepare it using handwritten fixtures only. No candidate execution until the design and implementation are reviewed; do not equate a child process with containment.
4. **Establish runtime/admission/restore readiness from the existing components.** The coordinator's read-only assessment of captured snapshot `1f067428` says **not ready for live runs**: planner/SSE/journal/resource components exist and 124 tests previously passed, but the one-arm coordinator is fake-backend-only and the CLI refuses execution. Real launch/identity/readiness, nested Windows Job compatibility, bounded monitoring/cleanup, trustworthy GPU/commit admission and independent provenance are missing. This snapshot does not prove newer PC state; no reliable delivery date is available. A scratch directory, Windows Job and fixed loopback endpoint provide lifecycle containment, not a security sandbox. Continue from those existing components rather than another planner; rejected component publication is not retried.
5. **Use one coordinated live window for the prepared changes and release checks when ready.** Record exact loaded identities, request profile, resources, all outcomes and rollback. Avoid another model or VM competing for scarce memory; schedule grading separately if needed.
6. **Measure the 12 tasks and daily-use session, improve only a demonstrated bottleneck, then release the guide and results.** Compare another cache/model/runtime only if it can address a measured unmet check. A full comparative cache study is optional for first release if the chosen stable configuration passes the direct quality/speed/resource checks; explain why it was deferred. The exploratory cap result retains its limitations.

All work here is collaborative. Claude supplied the daily-use proposal, implementation ideas and laptop observations; Codex supplied source/metadata checks and the proposed measurable amendments; the PC-side work supplied the collector/adapter components and hardware observations; independent reviews supplied the scoped test evidence. These contributions support Mohamed's decisions.

## Larger models: a stretch study

A stronger or overnight model may be useful **after feasibility is demonstrated**. A large download or a catalog entry does not establish memory fit, acceptable latency, quality, disk capacity, or a workable runtime. It is not a first-release completion requirement.

If pursued, first establish artifact identity, footprint, resource admission and a time/disk budget, then compare on agreed legally reusable tasks using the same scoring and complete-output rules. The restricted 24-question sample and its answers stay local; its reported 1/24 is not a coding-suite baseline or a promise another model will improve it. No installation, load, hardware purchase, remote exposure or paid service follows from this goal.

## Choices to put to Mohamed when concrete

- Whether the proposed quality/speed targets and routine coding scope match what he will actually use; he can adjust them before the acceptance run.
- Whether to proceed with a particular reviewed live gateway/teach update and the coordinated interruption needed to load it.
- Whether a Windows optional-feature/reboot change or a separate model/time/disk budget is acceptable, if the prepared design needs it.

Offline documentation/source review can continue now. There is no new live-system authorization in this proposal.
