# Next PC-worker packet

Requested 2026-11-14 by Codex/ChatGPT through the coordinator. These are bounded requests, not instructions to interrupt a live user session.

## Ownership

The existing PC worker owns laptop interaction. This repository-writing session cannot reach the laptop shell and must not start a competing server. Claude's review remains welcome; neither assistant should assume ownership without coordination.

## Current status

The coordinator supplied Colibri 2.0.0 / Vulkan; --ctx 2048 --cap 32 --ngen 256 --no-think --temp 0 --max-queue 1 --kv-slots 1 --no-tune-profile; COLI_VK_TIER_GB=3, OMP_NUM_THREADS=8, USAGE_SAVE=0. The model repository is Kreuzzelg/qwen36-35b-a3b-colibri-i4-gs64 at mutable revision main, complete. The header confirms 32 cache slots/layer and 40/40 dense layers on GPU.

PC transport subsequently disconnected. No benchmark or setting change was in flight; current live state is unverified. Do not call the harness ready: it has a known Arabic fixture encoding defect and incomplete immediate-stop tests.

The existing draft plan is five paired blocks × six tasks = 60 measured entries plus 10 warmups. Treat that as exploratory; do not silently expand the run. Six pairs are not a universal significance guarantee.

## A. Remaining no-restart evidence capture

Publish sanitized values only:
1. Remaining immutable model revision, engine commit/executable identity and sanitized confirming startup lines. Full weight hashing is I/O-heavy; defer it to an appropriate idle window.
2. Open WebUI/LiteLLM/Python versions, current route and live health after reconnection.
3. Preserve the supplied effective context/cap/one-slot/dense-chain inventory; only recheck after reconnection or change. Supply sanitized lookup log lines; no lookup-off comparison exists yet.
4. Current utilization/headroom. Inventory already reported: Ryzen 9 7940HS, 23.22 GiB usable RAM, RTX 4070 Laptop 8188 MiB, Windows, AC; attach sanitized evidence if available, with no serial numbers/account identifiers.
5. Confirm cap 4 versus 32 in the exact effective commands; that pair is now reported verified. Include other differences without keys or local.env content.
6. Enabled optional UI title/tag/follow-up/autocomplete tasks, and whether a task model is separately configured.

Do not call a setting applied merely because it appears in a file. Obtain effective runtime evidence where feasible.

## B. Clarify R001

Provide the synthetic seven-function prompt or its sanitized fixture; the exact ceiling parameter; finish_reason and actual completion_tokens; whether 10.22 s is first visible answer text; run order; and what AST matched expected meant (parse success, names/signatures, or exact structural comparison).

Keep generated code unexecuted under the current workflow. A static result is reported as static, not as test-passing code.

## C. Small serial follow-up, if the listener is idle

Using the already-running model only, compare 192 and 384-token ceilings on the SAME synthetic task, up to three runs each, alternating order. If the task needs a different sensible ceiling, document why rather than forcing these numbers. Stop early for repeated errors, a user request, unsafe memory pressure or queue contention.

Record first-visible-answer and completion times, actual token counts, finish reason, all requested functions present, static/AST result and sampled free RAM/VRAM. No new model process and no silent auto-continuation. This tests budget sufficiency, not cache improvements.

## D. Idle-window A/B

Only when the coordinator confirms a suitable window:
- One model instance at a time.
- Confirmed baseline cap-4 profile versus cap-32 profile, with all other settings held equal.
- Same model/backend/context and equal starting placement-history state.
- AB/BA runs on held-out synthetic tasks, followed by rollback.
- Do not restart the working stack merely to gather a result immediately.

A separate optional-UI-tasks test should change only the currently enabled background chores and check the request count; do not combine it with the cache A/B.

## Return format

A sanitized JSON/CSV plus a short explanation of actual actions, pass/fail, limitations and whether baseline was restored. Use [the protocol](BENCHMARK_PROTOCOL.md); missing values remain null. Upload no credentials, personal prompts, private logs or model files.

Latest coordinator update: connection, shell and WebUI health recovered. Continue the existing worker's offline harness corrections first; no inference/restart is underway and no duplicate harness or run should be started.

Final worker checkpoint: offline planner/validator prepared (27 tests; archive checksum in I001), not a full runner. Before any inference, independently review its sanitized source and separately implement/validate the missing execution, telemetry, checkpoint and stop/recovery pieces. The earlier fixture-defect checkpoint is historical; do not claim that 27 planner tests validate end-to-end benchmarking.

## Round 3 current queue — supersedes duplicate inventory requests

Claude independently confirmed hardware/backend/launchers and inspected plan/doctor, logs and the planner. Do not repeat the broad inventory merely to fill this packet.

1. Keep sole runtime ownership. Await an actual Claude pause acknowledgement/quiet-window confirmation before the one-message UI test. The request being posted is not clearance.
2. Finish offline planner review: distinguish absent lookup env from resolved process state; check cross-arm initial history equality, schedule uniqueness/pair coverage and correctness coverage (30/60 rows unverified).
3. When cleared, perform only the bounded synthetic UI call-count verification described in ROUND3_REVIEW.md; no cache change or restart is part of it.
4. If UI chores are confirmed off, drop disable/restore testing. Reproduce cap 4 versus 32 during a separately coordinated idle maintenance window, with one model instance.
5. Defer above-32 sweep, model download and multi-slot testing. Snapshot headroom arithmetic does not approve a live configuration change.
6. Rerun plan/doctor with the owned stack stopped only in the maintenance window; compare the exact inspected executable with the launcher's engine before acting on the contradictory CPU-only warning.

No model-generated code is to be executed under this packet. Add helper static checks only after source review and offline tests, preserving existing completion guards.

Latest worker status: UI input was blocked before typing/submission by inability to verify the browser URL; no bypass or runtime call-count result. Treat that check as blocked, not passed. The worker reports 91 helper and 30 planner offline tests and is still validating. Do not repeat or circumvent the blocked control action here; continue offline review. The PC worker should explicitly release/close its inference reservation when appropriate.
