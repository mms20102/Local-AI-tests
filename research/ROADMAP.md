# Research roadmap

## Phase 0 — Shared handover
- [x] Locate the private repository and inspect existing work.
- [x] Preserve Claude's original co-chat.
- [x] Reconstruct a sanitized briefing from visible project history.
- [x] Open real questions for Claude with source-linked constraints.
- [ ] Receive Claude's actual response; no response is fabricated or assumed.

## Phase 1 — Recover reproducibility
- [ ] Access the AI laptop and inventory actual runtime/model/hardware.
- [ ] Recover earlier timing artifacts, scripts and lockfiles where available.
- [ ] Publish sanitized configurations and record exact versions.
- [ ] Run a fresh smoke test and freeze a baseline.
Done when another session can reproduce the baseline without needing private chats or secrets.

## Phase 2 — Low-risk speed
- [ ] Expert-cache sizing under real free RAM/VRAM limits.
- [ ] Concise coding instructions.
- [ ] Prompt-prefix reuse through the UI and gateway.
- [ ] Prompt lookup only on a supported installed backend; include non-repetitive controls.
Done when paired tests show a useful speed gain with no task-quality regression and a tested rollback.

## Phase 3 — Better coding model
- [ ] Resource/format/license check for Qwen3-Coder-30B-A3B.
- [ ] Separate side-by-side install if appropriate.
- [ ] Frozen correctness, tool and Arabic evaluation.
- [ ] Select a route/default only from measured tradeoffs.

## Phase 4 — Coding execution
The working draft helper does not execute code. Autonomous execution is a separate design task: isolated workspace, explicit tool permissions, bounded commands, tests, logs and recovery. Do not infer that structured tool-call output has already enabled this phase.

## Ownership and bounded work

Codex/ChatGPT maintains handover/evidence and proposes reproducible experiments. Claude reviews and challenges through co-chat, and may own an experiment when coordination records it. Mohamed moderates scope and decisions. Only one owner operates the laptop at a time.

Do not leave open-ended agent loops or assume repository messages trigger the other agent automatically. If blocked on PC access or a reply, finish independent documentation/review and report the exact blocker.
