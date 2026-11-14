# Round 3 review and next actions — 2026-11-14

This reviews Claude's actual laptop report in [co-chat](co-chat.md). No inference, restart or setting change was performed by this repository session.

## Established and still unverified

Claude independently confirmed I001's hardware, Colibri 2.0.0/Vulkan backend, cap-4 versus cap-32 launchers, one KV slot and lookup engagement. Exact metadata and provenance are recorded in [I001](experiments/2026-11-14-pc-inventory.json).

The UI environment file disables optional generation tasks and persistent config. That is strong configuration evidence, not a runtime request trace. The appropriate next step is verification, not an assumed disable/restore improvement.

Binary strings show a multi-slot chain-off/no-drafting message exists. They do not establish that an arbitrary multi-slot run would execute it. Retain the working one-slot profile; no risky multi-slot experiment is needed for the present question.

The helper's existing truncation/finish guards are recorded from local project files. They should be inspected and tested before describing any new guard as implemented.

## Planner review

Claude independently ran the 27 preparation-package tests and confirms it only plans/validates. No operational runner, measured cap comparison or semantic execution is thereby established.

Three task categories (function, bugfix, Arabic) remain correctness-unverified: 30 of 60 measured entries. Publish all timing/failure data, but do not call the entire result a quality-preserving speedup. Even latency-only comparisons need comparable completeness, stop reason and output length.

Reviewer checks requested, not newly confirmed defects:
1. Track actual resolved child-process lookup state, not just omission from launchers. An absent variable is not the literal string "unset".
2. Require history unchanged within each run AND identical intended starting history across paired arms. Two individually unchanged but different files would pass the former test alone.
3. Validate schedule coverage, unique run IDs, correct A/B pairing and separate warmups. A row validator alone is not a whole-experiment validator.
4. Keep transport/record validity, syntactic/schema checks and semantic correctness separate. Never silently convert unknown to pass.
5. Preserve failed/truncated results and report failure rates. Do not cherry-pick successful fast pairs.

## Conditional memory candidates, after reproduction

Claude supplied per_cap_bytes = 70,778,880. Derived host expert-cache capacity, not total process memory:

| Cap | Host expert cache | Additional versus 32 | Illustrative free RAM from a 5.7 GiB snapshot |
|---|---:|---:|---:|
| 32 | 2.109 GiB | 0 | 5.700 GiB |
| 48 | 3.164 GiB | 1.055 GiB | 4.645 GiB |
| 64 | 4.219 GiB | 2.109 GiB | 3.591 GiB |
| 80 | 5.273 GiB | 3.164 GiB | 2.536 GiB |

These subtract only the incremental cache from one free-memory observation. Scratch, KV growth, other apps and paging can invalidate them. Cap 64 is a test candidate, not a guaranteed safe configuration or proven optimum. Do not change cap before the 4-versus-32 reproduction.

The log's 55,306 disk loads / (51,678 RAM hits + 55,306 disk loads) = 51.70% of CPU-side routed requests in that sample. It is not a percentage of distinct experts resident on disk, nor a stable whole-workload miss rate.

## Bounded runtime verification proposal

The PC worker remains sole runtime owner and is waiting for a confirmed quiet window. Claude's own acknowledgement has now been read at b6d67e2. This clears Claude's inference traffic only; the PC worker still needs to coordinate any user activity and the overall quiet window.

After actual clearance, use one fresh synthetic UI chat message through the normal UI, not an API client alone. Observe a quiet pre-test baseline, correlate the request across UI/gateway/engine where feasible, then allow a bounded post-completion observation window for asynchronous jobs. Preserve only sanitized counts/timestamps/route labels. A single engine POST proves one observed call only within that route/window; missing logs, delayed calls or failures before the engine must not be interpreted as proof of absence.

If the expected single foreground call is the only observed inference and runtime flags align, close the UI-chores investigation for this configuration. Do not run a pointless disable/restore A/B when already off.

## Offline helper improvements to review

- Validate completion signals without silently retrying; [DONE] is an SSE-stream check, not a universal requirement for non-stream JSON.
- Parse fences robustly, report Python as parses/unparseable, and check declared expected functions/signatures where task metadata requires them.
- Permit appropriate callable kinds (for example async functions or methods) when the task asks for those; do not impose top-level def on every coding task.
- Static success is not semantic correctness. Keep execution outside the current draft-only workflow.

No changes to the helper are claimed here.

## Reply watcher: static review and delivery limit

Claude added tools/watch_cochat.py and tools/Watch-CoChat.cmd. Static review here confirms no model call or git push/pull/merge is invoked; the watcher fetches and writes local notifications. This session cannot read the PC inbox directly or subscribe to its stdout. The existing PC worker can relay an event through the coordinator; no automatic wake-up of this cloud chat is established.

Suggested offline review cases for Claude (not reproduced here):
- A commit that changes no co-chat text currently still produces an unknown-speaker event. Filter metadata-only changes if the promise is reply notification.
- Branch catch-up can repeat an already-notified reply because events are keyed by old/new ranges; test content/turn-level deduplication across main and the Claude branch.
- State heads mutate before all notification writes succeed. Test transient write/Git failure recovery so retry in the same process cannot silently lose an event.
- The first run records current heads without replay unless --since is supplied; document this clearly.

No watcher defect is claimed reproduced by execution in this session, and no watcher code was changed here.

## Latest worker checkpoint

The one-message UI attempt was blocked before input because PC control could not confidently establish the Windows browser's current URL for policy enforcement. Nothing was typed or submitted, and no bypass was attempted. Runtime UI call counts remain untested.

The worker reports new offline helper fence/syntax/required-name checks with 91 passing tests and planner lookup/coverage updates with 30. Validation is still in progress; this repository session has not reviewed those revised sources or rerun their tests. These counts do not establish model correctness or a speedup. Claude's pause is acknowledged; the PC worker must explicitly close/release the test window.
