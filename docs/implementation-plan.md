# Safe implementation plan

This plan follows the supplied reliability/security prompt and keeps the release
blocked until evidence closes each dependency.

## Dependency order

1. **Evidence and schemas** — define versioned manifest, task, case, execution,
   grader, summary, and hash-manifest records. Add raw-record validation and
   summary recomputation without running candidates.
2. **Judge fixtures** — add trusted correct/wrong/incomplete/timeout/crash/
   refusal/spoof/mutation fixtures and reproduce the F02 defect. Candidate
   self-reporting must have no authority.
3. **Isolation design review** — document the threat model and select a
   disposable VM or demonstrably equivalent boundary. Keep live execution
   disabled until preflight proves identity, network policy, mappings, limits,
   and cleanup.
4. **Runtime doctor** — implement machine-readable identity and resource
   capture. Unknown executable, model, tokenizer, callback, profile, or process
   identity must fail closed.
5. **Exact context admission** — count the final serialized request after
   teaching injection and reserve output plus margin. Add Arabic and Unicode
   boundary fixtures.
6. **Teaching/privacy contract** — test a disposable multilingual store, exact
   final payload, omission statuses, counter failures, deterministic ordering,
   and bounded nonblocking evidence handling.
7. **Lifecycle/recovery** — implement and test explicit state transitions,
   process-identity checks, cancellation, atomic journals, restore, rollback,
   and missing-telemetry refusal.
8. **Controlled quality run** — only after steps 1–7 and independent isolation
   approval. Preserve raw records and keep the locked 12-task denominator.
9. **Controlled performance run** — only after correctness is accepted. Use
   quiet AB/BA runs, useful-text parsing, resource telemetry, cold/warm
   separation, and rollback.
10. **Independent release review** — a separate reviewer checks the packet,
    hashes, commands, raw evidence, and every gate before any release claim.

## Safe commands in this checkout

- `git status --short --branch`
- `git log --oneline --decorate`
- Static searches and document inspection
- Trusted repository/documentation checks
- JSON parsing of checked-in evidence files

## Prohibited until isolation and approval

- Starting the local model or live gateway
- Downloading models or changing runtime/security settings
- Executing generated or untrusted candidate code
- Running hostile probes
- Accessing credentials, private prompts, notes, or raw logs
- Treating a host subprocess, WSL, Docker, or unverified Sandbox as a security
  boundary

## Definition of done

The release gate remains `BLOCKED` until every mandatory gate is `PASS` and a
separate reviewer signs off. Improvements that only add documentation or
offline trusted fixtures do not authorize a live benchmark.
