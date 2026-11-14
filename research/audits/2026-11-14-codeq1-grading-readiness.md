# CODE-Q1 independent grading: preparation and current boundary

Review checkpoint: **2026-11-14 21:32 UTC**. Canonical grader/fixtures were inspected at `df660942`; published first-pass drafts are at [`afc71839`](https://github.com/mms20102/Local-AI-tests/tree/afc71839667c0c212787afae982d4e217e6dc1d4/research/coding-quality-v1/drafts-2026-11-14-first-pass). Claude reports direct approval for their publication. No private laptop drafts were retrieved by this review.

**No generated draft was executed by this repository session. Behavioral grading remains unassessed.** The designated grading worker handled input verification/static grading; no duplicate run was assigned here. Its private handoff files remain unpublished.

## Frozen inputs and denominators

| Input | Git identity |
|---|---|
| `grade.py` | `c3d5387cb708354659864bca52ae2e00b5af5040` |
| `manifest.json` | `bf1ac49bb49020767a2f92f3ea7d54b83c23f411` |
| `test_grade.py` | `c13d16eb8cc85e1186b20bd541f78b0a6a050190` |
| Fixtures tree | `56bbc4b1b0866b93690698c0187367128533276c` |
| Published draft index | `3c3b27e0c79750befb166a332c7dc5f1b170d889` |

The separate designated worker reports verifying 91 Git blobs, every fixture-manifest hash, all 12 draft-file hashes and all 12 content hashes. It independently reports **12/12 complete transport and 12/12 structure pass**. Those are relayed static results, not runtime semantic scores or hash computations performed by this document.

This review's read-only preparation independently counted the fixture JSON arrays:

| Group | Tasks | Language | Public | Hidden | Total |
|---|---:|---|---:|---:|---:|
| A | 3 | Arabic | 3 | 23 | 26 |
| B | 3 | English | 3 | 23 | 26 |
| E | 3 | English | 4 | 35 | 39 |
| F | 3 | English | 3 | 22 | 25 |
| **All** | **12** | **3 Arabic / 9 English** | **13** | **103** | **116** |

Arabic has 26 cases; English has 90. There are ten expected-exception and three explicit outer-new-object-identity cases. E02 requires seven functions; E03 spans two files. Preserve all 12 first attempts in the denominator, including future failures/truncations/infrastructure blocks. “Not run” is not a model failure or pass.

## Concrete manual F02 finding — not an executed case result

The published [F02 draft](https://github.com/mms20102/Local-AI-tests/blob/afc71839667c0c212787afae982d4e217e6dc1d4/research/coding-quality-v1/drafts-2026-11-14-first-pass/F02.json), blob `49b2cdc81ee64ce0ea75451925806e5ff48e31d2`, calls `sorted(intervals)`, then retains an original inner row in `merged` and assigns `merged[-1][1]`. Sorting copies the outer list, not the row objects.

For `[[1,3],[2,6]]`, the merge assignment targets the original first row and would change it to `[1,6]`, violating the unchanged-input contract. This is a source-derived counterexample, **not four executed failures or an 11/12 runtime score**. Do not repair or regenerate the frozen first-pass answer. The earlier E02 uncertainty is not a failing result; the designated manual review found no concrete mismatch there, but that is not a case-execution pass.

## Containment is the current execution blocker

The designated worker reports its harmless bubblewrap probe stopped before executing its fixed Python probe:

```
loopback: Failed to create NETLINK_ROUTE socket: Operation not permitted
```

It also reports a read-only Sandbox-provider project lookup returned **403 requiring owner-team authorization**. No resource was created, no alternate credential route was tried, and protection was not weakened. These are worker-reported environment/access facts, not denials produced in this repository session.

Sandbox tools were discovered here, but no sandbox was provisioned or validated. The manifest remains `generated_code_execution_enabled: false`. A cloud label, child process, environment variable or acknowledgment flag does not establish containment. The next run needs a verified disposable environment with denied networking, no host secrets/mounts, bounded resources/output/deadline and confirmed cleanup. The planned owner-enabled Windows Sandbox remains another route after its actual setup checks; owner approval does not mean it is enabled.

A new [GitHub CI run](https://github.com/mms20102/Local-AI-tests/actions/runs/43642451133) independently reports successful Linux and Windows test jobs. That proves the existing CI workflow ran its selected tests, **not containment for arbitrary model output**. A dedicated bounded no-network container/guest path could be assessed by the designated worker; no grading workflow, isolation probe or new run was created by this review.

## CI-containment prerequisite — current coordination

The designated worker completed a read-only GitHub Actions feasibility assessment: a dedicated isolated candidate job is feasible in principle, **not proven or cleared for drafts**. It is now preparing a cloud-workspace-only harmless probe and negative tests. No Actions workflow has been created/edited/run for that work, no gate enabled and no draft executed. This repository session is not implementing a competing probe.

Actual runner/Docker containment must be verified, including denied network, explicit read-only input mounts, finite resources, bounded output and exact cleanup. Unit tests of the probe do not prove the runner boundary. The separate candidate/reporter integrity issue also remains; a successful Docker probe alone must not enable the canonical execution gate.

## Supplied grader limits that the runner must retain or address

- [Semantic gate](https://github.com/mms20102/Local-AI-tests/blob/afc71839667c0c212787afae982d4e217e6dc1d4/research/coding-quality-v1/grade.py#L270) checks declarations but creates/verifies no isolation. Do not flip the shared canonical gate to make a host run proceed.
- [Execution/capture](https://github.com/mms20102/Local-AI-tests/blob/afc71839667c0c212787afae982d4e217e6dc1d4/research/coding-quality-v1/grade.py#L235) accumulates child stdout/stderr before slicing output; ignores child return code and does not establish whole-tree termination. A VM protects the host but does not make these collection limits disappear.
- [Candidate/report driver](https://github.com/mms20102/Local-AI-tests/blob/afc71839667c0c212787afae982d4e217e6dc1d4/research/coding-quality-v1/grade.py#L41) shares the candidate interpreter. Parent-held expected values do not authenticate reported return/exception/mutation observations against adversarial interference. Disclose that distinction separately from host containment.
- Static checks verify syntax/names, not signatures, behavior or all requested formatting. The semantic function can proceed with unknown transport, so complete first-attempt provenance must be enforced separately. Canonical input hashes must be verified externally before execution.

A future report should separate transport, structure, requested-format compliance, manually derived observations, executed authored cases and observer-integrity limits. Report exact per-case failures and first-attempt fully passing tasks out of 12, with 3 Arabic/9 English task breakdowns. Quiet-run timing and representativeness remain separate. No behavioral score is available now.
