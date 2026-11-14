# Laptop benchmark protocol

Historical design with a current evidence correction, 2026-11-14. The frozen schema-4 plan is unchanged; no full cache A/B has run. Use [CURRENT_STATE](../docs/CURRENT_STATE.md) and [the current worker packet](PC_TEST_REQUEST.md) for implementation/admission status. Earlier 27-test references below describe historical checkpoints, not current readiness.

Purpose: improve time to a complete, correct useful answer.

## Ownership and resource boundary

A separate PC worker can reach the laptop. Its offline planner/validator package is prepared with 27 reported tests, but an operational benchmark runner is not yet implemented. Codex/ChatGPT handles repository evidence/review; Claude provides independent review through co-chat. Do not ask Mohamed to duplicate work already owned by that worker.

Only one model instance at a time. A second instance exceeds reported GPU headroom. Baseline/candidate restarts require an agreed idle maintenance window; do not interrupt active user chat.

## Prerequisites

1. Capture exact engine/model/backend/quantization, CPU/GPU/RAM and sanitized effective configuration. See inventory I001.
2. Historical baseline/candidate is now reported confirmed as expert cap 4 versus 32, same model, Vulkan. Make both caps explicit if supported; inspect actual runtime values rather than trusting a file.
3. Record saved tuning profiles, auto-tier plans and automatic cap raising. Disable auto changes only if the installed engine actually reads the control. At the pinned v2.0.0 source, RAM_GB is read in automatic cap sizing; explicit positive caps 4/32 bypass that branch. Do not treat it as a universal hard memory guard. See [the scoped source correction](RUNTIME_MEMORY_RESEARCH_2026-11-14.md).
4. Keep AC power, comparable thermal state and unchanged driver, backend, context, thinking/sampling and output ceiling for placement tests.
5. Keep the original launcher/model and a private config backup. Publish no secrets, private prompts or unredacted process command lines.

## Workload and correctness

Use fixed synthetic tasks: short instruction, pure function, bug fix, repetitive edit, schema-checked mock tool request, and Arabic plus coding. Keep functional tests hidden from the model; reserve additional holdout tasks.

Record expected deliverables and actual input/output tokens. Truncated answers fail completeness; do not count their shorter latency as a speed win. Capture finish_reason and context clamping. An AST parse or signature/structure match is a static check, not proof that code behaves correctly. Do not execute generated code under the current draft-only workflow; functional testing requires a separately defined isolated runner.

## State control: distinct sources

- Expert resident state and adaptive placement: start each profile block from the same unmodified history when the active backend uses it. USAGE_SAVE=0 prevents history writes; it still reads prior history and does not prove in-memory adaptation is frozen.
- GPU-tier histories: apply snapshot controls only where the installed engine actually records/loads them. CPU-only paths may differ.
- Prefix/KV state: persistence control and in-memory reuse are separate. KVSAVE=0 is useful only if this engine honors it; it does not clear live context. A new UI chat may still send the same cacheable prefix.
- Saved tuning profiles and auto plans: record and control them rather than silently inheriting settings.
- OS file cache: restarting an engine does NOT clear it. Counterbalance order and record file I/O/memory; describe unmeasured file-cache bias honestly. Do not use privileged cache flushes.
- Thermal and power state: record and avoid comparing cold hardware with a throttled later arm.

For a profile comparison, use fresh processes sequentially per arm/block, equal starting histories and the same unscored warm-up/workload order. Measure startup separately. Where a supported reset exists, verify that it resets the intended state. A warm conversational-reuse test is separate and intentionally preserves prefixes.

## Ordering and sample size

- Use AB/BA counterbalancing; no simultaneous A/B servers.
- The worker's prepared plan is five paired blocks across six tasks (60 measured entries plus 10 warmups), explicitly exploratory and not yet run. Six or more pairs can be planned for confirmation if practical; do not change a saved run budget silently.
- Six pairs are not a blanket significance guarantee. Dependence, multiple tasks/metrics and run-order effects matter. A two-sided sign-test minimum p-value is not a substitute for a sound design or confidence interval.
- Publish every paired result, medians, spread and exclusions. Do not claim a production p95 from a tiny sample.
- Stop for active user traffic, repeated faults, unsafe resource pressure or an expired run deadline; save the checkpoint.
- Use the same synthetic request sequence per arm. A repeated exact prompt with cached prefix is not equivalent to cold prefill.

## Metrics and adoption

At the client: first nonempty visible answer text, completion time, actual token counts and finish reason. Record reasoning/tool output separately; SSE keepalives and header arrival are not answer text.

Also capture peak/sampled host and GPU memory, paging pressure, queue wait, expert hit/I/O and active lookup telemetry. Minimum sampled free RAM does not establish peak headroom.

For CPU-only pure residency changes, demand byte-identical deterministic text where the installed engine promises arithmetic invariance. GPU placement/backend changes may alter rounding; investigate and retain meaningful task checks rather than treating every byte change as either harmless or automatically wrong.

A proposed screening gate is at least 10% median paired completion improvement with equivalent completeness/correctness, no sustained memory-pressure regression, and a confirmatory reverse-order block. This threshold is a project decision, not a statistical theorem. Publish no causal lookup claim until lookup-off versus lookup-on is actually run and the feature's active state is verified.

If no clear gain survives confirmation, retain baseline and publish the negative result. Verify original-launcher rollback after the maintenance test.

## Version caveats

Tagged v2.0.0 qwen36 source disables the active Vulkan dense-chain path with more than one mux slot; installed build identity and effective runtime behavior still require verification. Do not generalize a version-specific condition to every runtime.

A cloud/Codespace test cannot reproduce this laptop's GPU, RAM or thermal behavior.

## Round 3 review addendum

The planner's 27 tests validate preparation logic, not an end-to-end runner. Claude reports function/bugfix/Arabic rows always carry correctness unverified (30/60 measured entries). Publish full coverage and failures; no experiment-wide "no correctness regression" claim is supported until the missing assessments are supplied.

Validate run IDs, schedule coverage, arm pairing and warmup segregation at batch level. History before=after per row does not imply the intended history was equal between arms. Record the actual resolved lookup setting, including an explicit absent state where appropriate, rather than treating omission from a launcher as process state.

Compare latency with completeness, finish reason and output length visible. Report every failed/truncated run; any complete-pair latency subset must show the full denominator and failure rates.

UI call counting requires an actually confirmed quiet window and correlated observation across the relevant path, including bounded asynchronous tail time. One engine log line alone is not universal proof that all optional UI calls are disabled.
