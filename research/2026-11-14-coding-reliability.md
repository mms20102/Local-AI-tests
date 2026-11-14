# Coding reliability and time to a passing patch

Research date: 2026-11-14. Author: Codex/ChatGPT, coding-quality research track.

**Recommendation:** finish the outcome-recording contract before running another performance comparison; preserve the review-only drafting helper; build a separate, initially disabled evaluator for saved synthetic drafts. Optimize accepted behavioral solutions per time budget, with completeness and failure rates visible.

This is a research/design deliverable. It performs no PC change, inference request, model download, restart, generated-code execution or automatic repair. No local execution environment was available to this research session. The runtime helper and planner source are not in the inspected repository tree, so their behavior is reported from the co-chat, not independently audited here.

## 1. Evidence and the immediate blockers

Repository snapshot inspected: [main at 982437c](https://github.com/mms20102/Local-AI-tests/tree/982437cf0ab604a572a1da0c38ed2527d593860e). Read README, briefing, current state, benchmark protocol, PC request, output-budget record and round-3 review. Also read the complete co-chat on main and [Claude's branch at 5dca2bb](https://github.com/mms20102/Local-AI-tests/blob/5dca2bb1755dad4b845cd75d307af1c6821049ad/research/co-chat.md), including round 4.

| Evidence | What it supports | What it does not support |
|---|---|---|
| [R001](experiments/2026-11-14-output-budget.json): worker reported 32 tokens/18.28 s truncated; 192 tokens/30.41 s structurally complete on one seven-function task | A shorter answer can be an incomplete answer; task-specific output allowance matters | A general speedup, 192 as a universal ceiling, behavioral correctness, throughput without actual token counts |
| Latest main co-chat: 100 workbench tests and 30 planner tests reported | Offline preparation checks were exercised | Model quality, cache gains, an operational benchmark runner |
| Claude round 4: independently reports running those 100/30 tests | Corroborates those preparation-suite counts | This research session rerunning them, or any new inference |
| Existing plan: 60 measured rows, 20 exact-fixture / 10 tool-schema / 30 unverified | Explicit assessment coverage | A semantic pass rate across all 60 rows |
| Installed setup recorded in PC request: Colibri 2.0.0/Vulkan, context 2048, output default 256, no-think, temperature 0, one KV slot | A concrete starting profile to pin | A request's effective output budget or immutable weight identity without corresponding records |

Claude's new round-4 planner review is especially relevant. It reports that history equality and schedule-prefix validation are enforced, but identifies missing resolved child-environment evidence, missing finish reason, missing explicit batch-completion/complete-pair results and no summary function. The expected history is taken from the first row rather than a predeclared batch header. These are **Claude-reported source-review findings**, not defects reproduced by this session. Do not repeat older requests as though his review had not happened.

Smallest implementation priority:
1. Persist actual finish reason and streaming completion state, including truncated/error outputs.
2. Emit batch-complete, completed-pair and per-arm planned/attempted/complete/truncated/failed/unverified counts.
3. Pin intended history before the first run; retain resolved, sanitized relevant environment state.
4. Only then connect semantic results through the separate evaluator described below.

The UI call-count test remains untested in the inspected record. Claude's inference pause remains in force until the PC worker explicitly releases it. This plan neither releases nor uses that reservation.

## 2. What to borrow from established evaluations

These are methodology references, not local model rankings or recommendations to run their installers.

| Primary reference, checked 2026-11-14 | Useful method | Application here |
|---|---|---|
| [EvalPlus project](https://evalplus.github.io/) and [maintainer repository](https://github.com/evalplus/evalplus) | Expanded functional tests expose failures missed by sparse examples | Use boundary cases, reference implementations and additional hidden cases; keep raw responses as well as extracted candidates |
| [Aider benchmark method](https://aider.chat/docs/benchmarks.html) and [current benchmark scope](https://aider.chat/docs/leaderboards/) | Measures both valid code edits and tests; distinguishes first attempt from a second attempt with test feedback | Count extraction/application failures; publish first-pass and one-repair outcomes separately |
| [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/) | Applies a patch to a pinned repository and evaluates repository tests in a reproducible environment | Later repository track: pin base commit, test image and patch, include regressions |
| [LiveCodeBench authors](https://livecodebench.github.io/) | Release-date filtering and multiple coding scenarios help examine contamination/generalization | Keep fresh project-specific holdouts; public benchmark scores remain a supplementary signal |

Inference from those methods: start with small synthetic Python fixtures that fit the installed context, then expand to tiny repository edits. A full multi-language or large repository benchmark would add build/runtime/context variables before this project's missing semantic layer is solved. A selected public subset is a local subset score, never the original benchmark's full score. Unknown training cutoff means a dated problem cannot be asserted uncontaminated.

## 3. Keep four kinds of evidence separate

Store these dimensions independently; a single boolean called correct is insufficient.

| Dimension | Example outcomes | Rule |
|---|---|---|
| Transport | complete, truncated, disconnect, provider_error, unknown | SSE needs the expected terminal event and valid finish signal; non-stream JSON has no DONE event |
| Structure/integration | parse_pass, missing_callable, ambiguous_extraction, invalid_patch, schema_only | Python parsing/compilation does not call the generated function; patch application must succeed without unrecorded fixes |
| Behavior | pass, fail, timeout, resource_limit, unverified | Pass requires all declared tests and regressions in the reviewed evaluator |
| Execution integrity | valid, infrastructure_error, containment_failure, incomplete_report | A malformed or missing judge result never becomes pass |

Preserve finish_reason, stream_done_seen and response kind independently. A stop signal does not make missing functions complete; a DONE signal does not repair a length stop. Tool calls are assessed against a task-specific tool-call termination contract and argument schema, not the text-code stop rule.

Required callable checks come from metadata: module, name, synchronous/async/method kind, signature and required files. Do not impose top-level def on every task. Stub/TODO heuristics may explain failures but cannot prove completeness. Bound raw response size before parsing; resource-limit static parsers too.

Extraction is deterministic and versioned. Specify the permitted raw/fenced/patch format for each fixture. Reject ambiguity rather than selecting an arbitrary code block. Retain raw and extracted hashes plus transformation records; no silent repair, import insertion, indentation fixing or sanitizer rewriting.

## 4. Separate isolated semantic evaluation

### Boundary and data flow

The current helper continues to save drafts for human review. It does not gain an eval, exec, import, subprocess, tool-dispatch or automatic-retry path. The proposed evaluator accepts an explicitly selected, hashed synthetic artifact and a ready task manifest. It cannot contact the model.

Proposed flow:

`saved draft + task/base hashes -> bounded extraction/patch staging -> disposable sandbox -> bounded output -> independent judge -> signed-by-controller result record`

"Signed-by-controller" means authenticated result provenance created outside candidate execution; it does not require publishing signing keys or selecting a cryptography implementation in this design. Candidate stdout is data, never a trusted pass certificate.

Prefer a disposable VM/microVM on a separate evaluation host with no access to the user's workbench. This avoids installing a new runtime on the PC or competing for its model memory. Provisioning or uploading to such a service is future work, not performed here. A Linux container may be an inner layer; a new directory, Python venv, AST allowlist or subprocess timeout alone is insufficient isolation. [HumanEval's own execution guard](https://github.com/openai/human-eval/blob/master/human_eval/execution.py) explicitly distinguishes its guard from a security sandbox; its [historical harness](https://github.com/openai/human-eval/blob/master/README.md) should not be copied as a turnkey maintained isolation product.

### Proposed baseline policy, to validate before enabling

- Disposable guest, pinned Python 3.12 patch/runtime image digest and offline dependencies. No package install or network during grading.
- No guest network, credentials, model endpoint, GPU, shared clipboard, user profile, repository credentials, host directory mounts or container-management socket. Only synthetic candidate/task inputs enter.
- Candidate runs as an unprivileged user; guest root and trusted harness files are read-only; writable scratch is ephemeral and bounded.
- Initial small-fixture limits: 1 CPU, 512 MiB guest workload memory, 32 processes, 64 MiB writable scratch, 10 s total candidate evaluation per attempt, at most 2 s per case within that total, 64 KiB combined output. These are proposed calibration values, not proven sufficient or supported by an installed runtime.
- Independent supervisor enforces wall time, output and memory limits, kills the complete guest/process tree and verifies cleanup. Cancellation halts dispatch immediately and saves the checkpoint. A guest watchdog alone is insufficient.
- If a container is used inside the VM, the reviewed profile includes no network, dropped capabilities, no new privileges, read-only root and explicit CPU/memory/process/scratch limits. Validate effective enforcement rather than trusting command text. Docker documents the [controls](https://docs.docker.com/reference/cli/docker/container/run/), [security boundary](https://docs.docker.com/engine/security/) and [lack of default resource limits](https://docs.docker.com/engine/containers/resource_constraints/).
- Fail closed if any required boundary is unavailable. Do not switch to executing in the workbench as a fallback.

A Windows Sandbox route would be a separately validated alternative if already available, not a proposed installation now. Microsoft documents that default [networking and clipboard sharing are enabled](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file); its default launch is therefore not this policy. Local Sandbox RAM/CPU consumption would also confound concurrent laptop timing.

### Keep the judge outside candidate control

For the first pure-function and tiny-module fixtures, send bounded JSON test inputs to the guest callable adapter and compare returned JSON values with trusted expectations **outside the guest**. Allow only declared callable IDs and JSON types; never deserialize pickle or evaluate candidate output on the host. Exact type/value/exception expectations, mutation observations and normalization rules belong in trusted task data. Validate one complete response per case, reject extra/duplicate/malformed data, and associate it with a fresh run/case identity. Candidate output saying tests passed has no grading authority.

The generated program sees inputs supplied to it and can inspect its own guest. "Hidden" means absent from the model prompt/feedback; it is not an assertion that tests mounted in the same interpreter remain secret. Keep expected answers and the pass/fail decision outside that interpreter. Read-only tests alone do not prevent result spoofing or runtime introspection.

For later repository tasks that require in-guest pytest or language tooling, use a pinned trusted harness outside the candidate-writable tree and validate allowed-file diffs, test/harness hashes and structured reports from a protected supervisor. This improves accidental-tampering resistance but does not prove an arbitrary hostile program cannot game in-process tests. Do not call this an adversarially sound judge without a separate review. The first suite deliberately uses observable JSON interfaces so the external judge is feasible.

Patch staging is also untrusted-input handling: only task-allowlisted regular files; reject traversal, absolute/drive/UNC paths, symlinks, hardlinks, submodules, binary changes, test/harness/config modifications and excessive diff size. Apply to an ephemeral pinned fixture without hooks, dependency installation or shell interpolation. No automatic git commit or application to the real project.

### Offline validation before a model candidate is admitted

Use handwritten inert fixtures and deliberate wrong implementations. Required checks:
1. Golden solutions pass; unchanged buggy starters and mutations fail. Each contract clause has a corresponding assertion; include empty/boundary/Unicode/falsy-value cases.
2. Empty, truncated, malformed, missing-function and invalid-path outputs receive their proper outcomes.
3. Infinite loops, excessive allocation/output and leftover child processes are terminated by the external boundary; verify cleanup.
4. Synthetic canary files outside the guest are inaccessible; network is blocked; guest cannot reach the model endpoint; trusted tests/results cannot be overwritten.
5. A candidate printing a forged success record still fails incorrect outputs. Corrupt/duplicate/missing result IDs fail closed.
6. Timeout, disconnect, cancellation and supervisor crash retain a non-passing record; resume does not replay completed inference or silently skip work.
7. Independently review the containment profile and run the containment probes before enabling generated-code execution.

These are future tests to implement, not checks run by this session.

## 5. A bounded twelve-task suite

The companion [proposed manifest](coding-quality-v1.proposed.json) specifies contracts and callable kinds. It is deliberately non-runnable: fixture/test/reference hashes, runtime digest, calibrated output ceilings and execution review are absent. A consumer must reject it until those requirements are supplied and status is explicitly changed after review.

| IDs | Task family | Behavioral coverage |
|---|---|---|
| F01–F03 | New pure functions | Stable deduplication, closed-interval merging, key/value parsing |
| B01–B03 | Repair pinned buggy starters | Sliding windows, falsy cache values, median without mutation |
| E01–E03 | Preserve behavior while editing | Config-unit conversion, seven-function completeness, two-module invoice patch |
| A01–A03 | Arabic coding instructions | Whitespace word counts, both Arabic digit ranges, Unicode code-point chunking |

All twelve are standard-library Python with small JSON interfaces. Every task needs public examples, additional hidden cases, a reference implementation, deliberately wrong variants and a fixed timeout justified by calibration. Freeze prompt, starter, public/hidden tests and reference hashes before comparing arms. The E02 task matches the **shape** of R001; it is not a reconstructed R001 prompt.

Arabic fixtures must be written/read as UTF-8 and have round-trip checks. Define code-point behavior explicitly; do not silently add Unicode normalization or strip diacritics. Arabic prose quality, when requested, gets a separate anchored human rubric; it cannot substitute for the same semantic code tests. Matched English translations can be language probes, but are not extra independent tasks in the twelve-task denominator.

Keep tools as a separate mock track: validate name, JSON arguments, required/extra keys and recovery from a synthetic schema error. The dispatcher records calls to an in-memory fake; it has no shell, HTTP, filesystem or real side effect. Schema-only scores never become code-semantic passes.

## 6. Experiments to run later, in order

Each comparison changes one factor. These are hypotheses, not locally established improvements.

| Order | Comparison | Fixed controls and intended decision |
|---|---|---|
| C1 | Existing prompt vs a concise deliverables/contract prompt | Same model, output allowance, source and tests. Include all required names/files/constraints; optimize excess prose without deleting requirements |
| C2 | Task-specific output allowances | Calibrate on separate development tasks; record requested and effective ceiling, prompt tokens, context clamping and actual output tokens. The existing 192/384 proposal is a probe, not a global default |
| C3 | Whole small file vs strict patch format | Use edit tasks only; compare valid application, regression tests and total output/time. A patch that cannot apply loses its integration score |
| C4 | One attempt vs at most one feedback-guided repair | Separate opt-in research mode, same total task deadline/token budget across arms; report additional calls/time. No silent continuation of a truncated draft |

With recorded context 2048, preflight the fully serialized prompt/source/schema plus output allowance. Reject or redesign an oversize fixture; do not quietly drop source or raise context during a comparison. Temperature 0 and no-think remain fixed initially. Repeat trials can measure runtime variation but are not independent coding problems.

No best-of-N selection, model-generated tests as the sole oracle, judge-model calls, multi-agent voting or broad search is needed for this first stage. Those consume model traffic and complicate attribution before the basic outcome contract is correct.

C4 compares policies under the same maximum total budget; actual calls/tokens can differ and must be reported. Keep the initial-attempt allowance equal and predeclare any remaining repair allowance. Do not describe a policy comparison as equal consumed compute.

For C4, feed back only bounded public-test/static/application errors. Hidden inputs, expected outputs and private logs never enter prompts. If public tests pass but hidden tests fail, record final failure without a hidden-test hint or extra retry. A schema-repair policy is separate from a code repair. Every attempt receives a new ID linked to its parent.

## 7. Metrics that make failed answers visible

Record task run start with a monotonic clock. In a future live integrated evaluation, time to passing patch spans queueing, request/streaming, extraction, application, sandbox dispatch/start, tests and any permitted repair until the independent judge accepts. Record each component too. Do not start timing only after a usable patch exists.

Saved-output replay can establish behavior and grading cost. Without a connected original generation/repair timeline it **cannot establish live time to passing patch**. Retain null for that metric instead of adding unrelated post-hoc timings.

Report:
- First-pass semantic success: passing tasks / all attempted task runs, alongside planned and unrun counts.
- Pass-with-one-repair and recovery rate among eligible first failures; these are policy success rates, not independent-sample pass@2.
- Transport completeness, extraction/application success, semantic pass, and integrity coverage separately.
- Successful latency median/spread on a disclosed paired pass set; all failures remain in the table.
- A predeclared all-task deadline score: observed acceptance time for passes; the fixed task deadline D for every non-pass. Lower is better. Call it a capped budget score, not mean TTPP. Terminal early failure still receives D; keep actual elapsed time separately.
- Total model calls/tokens, grading time, repair count, sampled RAM/VRAM/paging and cancellation/infrastructure counts.

Suggested pilot: four separate development fixtures for calibration, then twelve frozen scored fixtures × two arms × one attempt = 24 scored generations, with counterbalanced order. One dedicated non-scored warmup per arm uses a separate fixture. Any later one-repair experiment is a new saved batch with at most two attempts per task run; it does not silently expand this pilot or the existing 70-row cap plan. The proposed manifest leaves runtime activation disabled and contains no generated schedule.

Use the same declared task deadline, initially proposed as 180 s, and output allowance across each pair except C2's explicitly changed allowance. Preflight and validate this budget on development fixtures. Count a task-level timeout as a non-pass; abort the batch for containment failure, active user traffic or stop instruction. Display infrastructure failures separately and include them in the conservative operational denominator; never remove them silently.

A twelve-task screening rule, proposed for moderator review:
- Quality candidate: at least two additional semantic passes, no losses among baseline passes, and no worse all-task deadline score.
- Speed candidate: identical passing-task set, no increased completeness/integrity failure, at least 10% lower paired median accepted time **and** lower all-task deadline score.
- Neither rule is statistical significance or production proof. Freeze the selected policy, then use a fresh holdout batch and repeated counterbalanced timing blocks before adoption. Do not tune on that holdout. Preserve negative results.

For confidence estimates, resample/compare at independent task level, keeping repeated observations clustered with their task. Do not treat 60 schedule rows or translations as 60 independent quality problems; publish raw paired counts and uncertainty. No production p95 claim from this pilot.

## 8. Result contract and implementation handoff

Extend the existing planner/validator rather than building a competing laptop runner. Add components with narrow responsibilities:

1. **Manifest/record validation:** version, ready status, hashes, expected history, run/schedule identity and all task-required fields; fail on null prerequisites.
2. **Artifact extraction/patch staging:** non-executing, bounded, deterministic, real-project writes impossible.
3. **Isolated grader:** selected saved candidate in; external behavioral observations/result out; no model client.
4. **Aggregator:** full planned/attempted/unrun/failed/truncated/unverified/semantic-pass coverage, batch-complete status and paired statistics.
5. **Optional future coordinator:** owns model requests, deadline/repair policy and checkpoints. It is outside the present review-only helper and remains disabled until the separate execution design is reviewed.

Minimum per-attempt fields:

```text
batch_id, plan_hash, task_id, task_revision, run_id, arm, attempt, parent_attempt
fixture_hashes, prompt_hash, raw_response_hash, extracted_hash, patch_hash
engine/model immutable IDs, runtime image digest, extractor/judge versions
request route, sampling/thinking, context, requested/effective output cap
resolved relevant env presence + sanitized non-secret settings, history hashes
monotonic start/first_answer/end/apply/grade times, queue and transfer durations
prompt/completion/reasoning tokens, finish_reason, stream_done_seen, response kind
transport, structure, behavior, integrity outcomes and reason codes
public/hidden test counts, resource limit outcome, cancellation, actual elapsed
ttp_pass_s or null, deadline_s, capped_deadline_score_s, evidence artifact hashes
```

No secrets or personal prompts in those records. Raw synthetic drafts/test artifacts may be retained in the private experiment store under a declared policy; publish sanitized summaries/hashes. Do not claim that hashes alone replace missing evidence.

**Remaining blockers:** no independent access to runtime helper/planner source in this session; new round-4 record/summary gaps await worker integration; fixture starters, tests and reference hashes are not yet implemented; no validated isolated runtime or containment probes exist in this track; exact immutable model/engine identities remain incomplete in the inspected project evidence; no new model evaluation or live TTPP measurement has run.

Next authorized work under the current boundary is offline source/fixture/record review. Semantic execution and any later model traffic remain outside this research task. The existing PC worker retains sole laptop runtime ownership.
