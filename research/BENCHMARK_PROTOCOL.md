# Laptop benchmark protocol

Purpose: improve time to a correct useful answer, not merely make a short test print faster.

## Prerequisites

1. Verify actual executable/model identity and supported flags. Save a private full config and publish only sanitized values.
2. Use AC power and a stable power profile. Record thermals, CPU/GPU utilization and memory. Do not globally disable security or OS protections.
3. Keep one experiment owner and no unrelated generation traffic. Stop only the experiment's own temporary processes.
4. Retain the original launcher and model. Do not upgrade engine and model and change tuning simultaneously.

## Workload

Use at least six fixed, synthetic, non-private tasks:
- Short factual instruction with a strict expected format.
- Small pure-function coding task with meaningful edge-case tests.
- Bug fix in a supplied function with frozen regression tests.
- Repetitive edit with a known expected change.
- Structured tool request with JSON-schema validation and a simulated result; do not execute model requests on the PC.
- Short Arabic explanation plus a coding question.

Keep correctness tests hidden from the model. Reserve additional tasks for final holdout. Record prompt/template hashes and input/output token counts; do not compare answers of substantially different completeness as pure runtime gains.

## Ordering and repetitions

- Begin with one unscored warm-up per configuration.
- For each prompt, alternate paired runs in AB/BA order; aim for at least five measured pairs initially.
- Keep an independent untouched snapshot of expert-history state for each arm, or reset both to the same starting snapshot before a pair. Do not let the second arm inherit the first arm's trained placement telemetry.
- Report cold-load/start latency separately from warm request latency. Do not clear OS caches using privileged system tricks just for a prettier number.
- Discard a run only for a predeclared invalid condition; retain the failure in the log.
- Use a request deadline and stop the batch after repeated faults or unsafe memory pressure; save the checkpoint.

## Metrics

At the client: time to first nonempty visible answer text; time to complete; input/output token counts and tokens/sec where reported reliably. Tool-only outputs are timed separately. Streaming keepalives, reasoning text and HTTP-header arrival are not first visible answer text.

Also record peak process/host RAM, GPU dedicated/shared memory, available memory, hard paging, expert hit rate, disk reads, queue wait, errors and user cancellation. Do not equate upstream gateway histograms with client TTFT; see [sources](SOURCES.md).

## Acceptance

- Correctness and required content must not regress; faster wrong answers do not pass.
- For pure placement/scheduling experiments, compare deterministic outputs when the installed engine/backend promises invariance. Investigate differences rather than assuming they are harmless.
- A changed prompt is evaluated for equivalent task completion, not necessarily byte equality.
- Tool-call tests must validate schema and arguments, reject malformed/unknown requests and test a synthetic error/recovery case.
- Report median, spread and each paired difference. Five pairs are exploratory and do not justify a production p95 claim.
- Adopt only after a confirmatory reverse-order run and successful original-launcher rollback.
- If no clear benefit is reproduced, retain baseline and publish the negative result.

## Scope limits

Cloud/Codespace tests cannot substitute for laptop RAM/GPU/thermal measurements. Colibri's default speculative path and backend limitations may change between commits. Pin exact versions and document any upgrade as a separate experiment.
