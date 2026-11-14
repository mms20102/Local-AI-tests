# Paired protocol 01: OFFLINE PREPARATION ONLY

Protocol: mms20102/Local-AI-tests research/BENCHMARK_PROTOCOL.md
Verified blob SHA: 03f0b8b04c7a8f772d2890322b486917476f33af.

## Use
From this folder with existing Python:
    python -B harness.py
prints a deterministic dry-run plan only.
    python -B -m unittest -v test_harness
runs synthetic unit tests only, without model calls.
    python -B harness.py --validate records.json
validates an offline schema-3 header/records checkpoint, bounded to 2 MiB (see below).

No launcher, model adapter, HTTP client, process control, code execution or credential access exists.
--run always refuses, even with --maintenance. The production-port guard is unit-tested
but no actual port probe is implemented: unconditional refusal is stronger than the guard.
This is NOT an operational benchmark. Do not claim readiness to run from these files.

## Frozen schedule
A=cap4, B=cap32, same Qwen3.6 model, ctx2048, output ceiling256, kvslots1,
Vulkan1/CUDA0, tier3 GiB, OMP8, USAGE_SAVE=0. All other launch settings must stay fixed.
Five pairs ordered AB, BA, AB, BA, AB. Each arm start has one unscored warmup
(prompt: Reply exactly READY.), then the same six tasks. Ten starts, ten warmups,
sixty measured requests. Keep tasks and prompt/template hashes frozen; hidden fixtures
are separate from task objects. Same template and request parameters remain an adapter gap.
Five pairs are exploratory, not evidence for production p95.

## Required future coordinated execution
1. Owner coordinates maintenance; preserve original launchers/model, no automated stopping
   or restoration by this prototype. Verify production 8000/4001/8080 closed immediately
   before each temporary launch. Reject uncertain port probe outcomes.
2. Snapshot expert history independently from an untouched baseline before every arm;
   record snapshot SHA and before/after history SHA. Do not let arm B inherit arm A telemetry.
   USAGE_SAVE=0 alone does not prove isolation; actual engine reads/writes must be reviewed.
   No history file was read or copied for this preparation.
3. Pin executable/model/template identities. identity_sha is a digest of immutable identity,
   NOT arm settings (cap intentionally differs). Arm settings are separately bound by plan_hash.
4. AC/stable power and no competing generation; record startup separately from requests.
   Set a real end-to-end deadline and memory-pressure threshold before execution.
   Stop after two consecutive infrastructure faults (transport_error/deadline), or an immediate-stop condition below;
   retain failures. No automatic retry of uncertain requests.
5. Persist append-only records atomically before/after each request and snapshot/checkpoint
   at arm boundaries. This prototype only validates terminal prefix records, not writes.
   Crash/inflight records require manual reconciliation, never blind replay.
   Hash contamination is rejected; preserve raw invalid records separately for audit.
6. Confirm reverse order, correctness and original-launcher rollback before any adoption.

## Metrics NOT implemented
Client first nonempty visible-text time and complete latency; tool-only latency separately.
Never use reasoning/keepalive/header time as TTFT. Unknown counts are null, not guesses.
Actual prompt/output token counting and full request-deadline enforcement need an adapter.
No telemetry collector implemented: CPU thermals/utilization, RAM peaks/free memory,
GPU dedicated/shared memory, paging, disk reads, expert hits, queue wait, startup.
Potential Windows sources verified by coordinator: Memory PageReads/sec, AvailableMBytes,
ProcessorTotal, PhysicalDiskReadBytes and GPUProcessMemory Dedicated/Shared counters.
No sample is produced here. No paired statistical summary/adoption decision implemented.

## Correctness boundaries
Exact factual JSON and repetitive edit have offline checks. Tool fixture validates exact
name/arguments/schema and returns literal simulated 5, never dispatches anything.
The synthetic error/recovery fixture is present but follow-up recovery NOT implemented.
Pure-function/bug-fix edge cases are frozen, but generated code is NEVER executed here:
their correctness remains unverified. Arabic explanation/code needs semantic review.
No full semantic/execution test claims, no equivalence claim from latency alone.
Do not pass hidden test fixtures to the model. Reserve new holdout tasks before adoption.

## Artifact contract
Records must form the exact schedule prefix, unique ordered IDs and matching plan hash.
Each has terminal state, original output, honest correctness label, nullable token/TTFT
metrics, total latency for completed requests, identity and history SHA evidence.
Unknown/missing hashes, malformed metrics and falsely claimed correctness fail closed.
This validator cannot prove hashes were honestly measured or enforce OS-level isolation.
No files outside this folder were changed.


## Round 3 integrity and coverage
COLI_LOOKUP is explicitly null/unset in the fixed plan, not 0 or an inherited value.
The coordinator reports the production launcher uses a sanitized environment allowlist
that excludes inheritance of this variable. A future execution adapter must likewise
omit COLI_LOOKUP and verify its effective environment; this offline planner does not
launch or enforce a process environment.

History checks remain STRICT: every recorded history_before_sha and history_after_sha
must equal the original baseline hash, across every request and both arms.
Do not weaken this to per-arm equality or permit an after-hash change. A change is
contamination, not an acceptable performance tradeoff. Preserve rejected raw evidence.

The plan now publishes explicit planned correctness coverage:
- 20/60 measured entries: exact fixtures (format and repetitive edit).
- 10/60: tool schema/name/arguments only, not end-to-end semantic or recovery validation.
- 30/60: function, bugfix and Arabic ALWAYS unverified. These have no correctness signal
  in this prototype, even when outputs look plausible or latency improves.
These are planned coverage counts, NOT completed results or pass counts.
Overall no-regression and full semantic execution claims are explicitly unsupported.
Five pairs remain exploratory. No execution adapter, model call, restart or
model-generated code execution was added.
## Artifact format (updated for schema 3)
Validation now expects an object with header and records, not a bare list:
{"header":{"plan_hash":"<current plan hash>","expected_history_sha":"<independently captured baseline SHA256>","expected_identity_sha":"<independently captured identity SHA256>"},"records":[]}
Supply the batch header independently BEFORE requests. Do not derive expected_history_sha
from the first result. Every before/after hash must match that header, including first row.
Old schema-1 artifacts are intentionally rejected; never invent evidence to migrate them.

Every raw record adds finish_reason and child_env_names. A complete text row requires stop;
a complete tool row may use stop or tool_calls. length requires state failed and
invalid_reason truncated. n_failed includes cancellations/truncations; n_truncated is its
subset, NOT an additional disjoint category. Unknown finish reasons fail closed.

child_env_names is a names-only inventory of ALL resolved child environment variables
whose names begin COLI_ or OMP_, plus USAGE_SAVE. Collect after the future launcher's
sanitization, not from a declared plan or a generic parent environment. Do not record
values or unrelated environment entries. The inventory must include COLI_VULKAN,
COLI_CUDA, COLI_VK_TIER_GB, OMP_NUM_THREADS and USAGE_SAVE; COLI_LOOKUP is forbidden.
This validates a supplied declaration, not actual OS observation or inventory honesty.
The planner still has no launcher, environment collector, or network adapter.

Summary preserves the full raw records list unchanged. Per-task/per-arm counts expose
planned, observed, complete, failed, truncated and unobserved rows; warmups stay separate.
Denominators remain 60 measured rows, 10 warmups and 30 task-level AB pairs.
batch_complete means every scheduled terminal row was observed, NOT all succeeded.
fully_observed_pairs includes failed arms. both_transport_complete_pairs requires both
complete. eligible_complete_pairs additionally requires both exact-fixture passes.
Thus at most 10/30 pairs are eligible with current checks: 5 format and 5 edit pairs.
Tool schema-only and function/bugfix/Arabic unverified pairs are explicitly excluded,
alongside missing arms, failures, truncations and known incorrect fixtures. Eligibility
does NOT establish broad semantic correctness, paired statistical significance or adoption.
Five pairs stay exploratory. Metadata cannot certify truthful measurements or hidden
environment state. Invalid artifacts fail closed without rewriting the original input;
preserve raw evidence externally for audit. No checkpoint writer or recovery executor exists.

Environment-name order is not constrained or claimed sorted. Names must be unique.
Neither environment VALUES nor provenance/completeness of the supplied inventory are
verified by this metadata validator; an omitted unknown name cannot be detected here.

## Round 7: schema 3 is the current contract
Schema 1/2 records and headers are not silently upgraded. Recollect missing evidence;
never infer it from the first output row. Before arm 1, a future runner must capture and
persist the header containing current plan_hash, expected_history_sha AND
expected_identity_sha from independently captured baseline identity/history.
Every row, including the first, must match those expected hashes. The validator cannot
prove header independence, when it was captured/persisted, or observation honesty.

The plan hash freezes this stop policy:
- Cancellation, memory pressure, identity/history mismatch, or unrelated traffic:
  immediate stop. Actual hash mismatch fails validation closed; preserve raw input for audit.
- Only transport_error and deadline increment the consecutive infrastructure-fault counter.
  Two consecutive infrastructure faults stop the batch.
- Truncation stays state=failed, finish_reason=length, invalid_reason=truncated.
  It is a received response: resets the infrastructure counter and never increments it.
- A complete response resets the counter even if an exact fixture is wrong. That is a
  quality failure/exclusion, not an infrastructure fault. No generated code is executed.
All accepted raw rows remain in the summary unchanged, including failures. Rejected
artifacts are never rewritten or pruned; retain the original file for forensic review.

The planned eligible_pair_ceiling is 10, NOT ten observed passes. The denominator remains
30 task-level pairs. eligible_complete_pairs is retained as an exact-fixture-qualified
count; exact_fixture_qualified_pairs is its explicit equivalent. Neither is a speed claim.
speed_comparison_eligible_pairs additionally requires both input AND output token counts
known and identical across the two arms. Unknown or unequal counts produce explicit
speed_comparison_exclusions, without converting a quality pass into a failure.
n_complete_with_token_counts counts complete rows with both input/output counts known;
null counts remain null, not zero or an estimate. Known counts alone do not establish
quality for schema-only or unverified categories. No speed, statistical or adoption
claim is computed. Future measurement still must verify actual token-count provenance.
count_relationships is machine-readable: n_truncated is a subset of n_failed;
cancelled rows are also included in n_failed, not an extra disjoint denominator.
The planner remains offline-only with unconditional --run refusal.
