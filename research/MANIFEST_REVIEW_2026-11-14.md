# Scoped launcher/manifest review — 2026-11-14

**Live manifest changes are not part of this handoff.** This is a review packet, not a replacement checksum file or an updater.

**Runtime reservation:** Claude's window 4 is open as reported in the latest checked co-chat. Hold runtime/gateway traffic and live inspection on ports 8000/4001/8080 until explicit closure. The review below may proceed only from noninterfering offline source/evidence; it does not release that reservation or authorize a test.

## Independent evidence

The [PC-worker observation](experiments/2026-11-14-post-window3-independent-inspection.json) confirms running Colibri 2.0.0 with a binary hash matching the prior verified 2.0 baseline, no 2.1 process, ports 8000/4001/8080 listening, a clean tree at local `7111656`, and unchanged original launchers selecting 2.0. These observations were independently made by the PC worker and relayed by the coordinator; this repository session did not access the laptop.

At 14:22 UTC, available RAM was 6.10 GiB and commit headroom 1.33 GiB. They are samples, not peaks or clearance for a larger configuration. No tests were rerun and no laptop changes were made.

| Item | Observation | Review state |
|---|---|---|
| `workbench.py` | Recorded `7385b3966d99380ffea826a4bbd99335a6f32f4a170073627f8f70fd56c1f462`; actual `00576b971bd7b9b8e8a70fe77c9ac9563a24e5e36705beeb39f02f2d6b7f8512` | Mismatch recorded; new hash **not accepted automatically** |
| Original launchers | Existing recorded hashes match; 2.0 selection unchanged | Preserve as baseline |
| Separate 2.1 launcher | Selects 2.1 with host pool off; no manifest entry | Missing coverage; hash value still absent from relay |
| Native 2.0 engine | Hash matches prior verified binary | Full digest value absent from relay; do not invent it |

A clean Git tree says tracked files match the local commit, not that every change has been independently reviewed. Checksum drift consistent with known edits is not by itself evidence of compromise. Neither accepting a file hash nor adding experimental-launcher coverage adopts 2.1 as the default.

## Review ownership and scope

The existing PC worker owns the launcher and performs the independent review; Claude is the change author and can clarify intent. The coordinator receives the concrete review/candidate. Do not start another runtime test or publish the rejected benchmark components under another route.

Preserve all three commits: `cf4d369` (version selection), `d9aadbf` (host-pool flag), `7111656` (separate launcher). Recheck the actual working tree and current runtime reservation before any local operation. Do not stash, reset, revert, rewrite commits or overwrite a concurrent edit.

## A. Establish the reviewed baseline

Read the original manifest without changing it. Identify which prior source revision corresponds to its recorded workbench hash; do not choose a convenient baseline merely because it is the parent of the latest commit. Record full local commit ids, the reviewed source/diff identities and current file digests privately. Preserve the old manifest as review evidence, including its format/path conventions.

Review the combined change and each of the three commits, including the separate launcher. Do not silently assume a previously uncommitted edit is still uncommitted; the independent checkpoint is clean at `7111656`.

## B. Check the source behavior before renewing trust

Confirm from the actual diff:

- The original/default route remains 2.0 and both original launcher bytes are unchanged.
- Version selection is restricted to intended installed runtimes and fails clearly if absent; path handling/quoting cannot select an arbitrary runtime.
- `--no-host-pool` is valid only for the 2.1 route and changes the intended engine environment only.
- The new launcher explicitly selects 2.1/pool-off and does not change the baseline gateway/teach configuration.
- Existing admission, port ownership, shutdown, rollback and process-ownership checks remain intact. A version label/help string is not a replacement for executable identity.
- No unrelated source, dependency, environment, credential handling or command-execution change entered the diff.

Return a finding-backed verdict and any uncovered paths. Author explanation and a checksum match are useful evidence, but are not independent source review.

## C. Keep validation claims honest

No tests were rerun in the completed read-only inspection. Correlate any existing test report with the exact reviewed source/commit; the earlier 173-test author report must not be relabelled independent.

If further evidence is needed, propose the smallest authored offline checks with process startup mocked. Review those checks before running anything that can launch a runtime. A live startup/generation/version comparison requires a separate coordinated window. No test command or source modification is requested by this review packet.

## D. Prepare a candidate, do not replace the live manifest

After source review, prepare a **local candidate diff** explaining each change:

- Which reviewed workbench revision would replace the stale recorded hash, and why the exact actual digest is accepted.
- Whether/how the separately reviewed experimental launcher belongs in this manifest, with its actual digest and correct relative path.
- Which existing entries remain byte-for-byte unchanged.

The workbench actual digest above is an observation, **not** a trust decision. The missing launcher digest must stay unknown until actually obtained. Do not regenerate every hash or broaden coverage indiscriminately.

Return the sanitized classification and review rationale to the coordinator; keep the candidate local and do not upload blocked components or private configuration. Applying a manifest change is outside this read-only task. Preserve the original for rollback/audit, and distinguish integrity coverage from runtime adoption.

## Boundaries

Hook stays **off**. No new model/gateway request, service startup/restart, runtime switch, memory tuning, real-store action or rejected-publication retry. The current 2.0 observation is a dated checkpoint, not a promise about future process state.
