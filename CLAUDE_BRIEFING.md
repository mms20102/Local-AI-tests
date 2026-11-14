# Claude briefing — Local AI tests

Updated: 2026-11-14. Owner/moderator: Mohamed.

## Start here

Build on Mohamed's working private local AI workbench. Improve usable speed, coding correctness and tool reliability without replacing a working configuration on speculation. Coordinate with Codex/ChatGPT in [research/co-chat.md](research/co-chat.md). Mohamed explicitly authorized that exchange; write only your own turns.

This workbench is its own project. It is not the Al-Mu'jiza analysis/training project and must not change Al-Mu'jiza files or methods.

## Evidence status of this handover

This briefing is reconstructed from the visible project conversation and the continuation handoff. An earlier chat prepared 11 sanitized files, but its workspace is not accessible from this session, and that upload never appeared on the inspected branches. This is not represented as a byte-for-byte upload of those files.

Directly verified here on 2026-11-14:
- The repository is private and the connected account has push permission.
- Before this publication, main contained only README.md at 5146412b5a3bd260327b52716b22756e4b25c258.
- Claude's branch claude/cloud-environment-setup-ha4b84 contained research/co-chat.md at 3e3f7f2c8a99372c9ee0e9bb4685703beaad453b. Its original text is retained in the shared log.
- Current upstream Colibri documentation was inspected; see [sources](research/SOURCES.md).

Reported by the prior project conversation, not independently rerun here:
- Local chat works through Open WebUI → LiteLLM → Colibri → Qwen.
- Real generation, streaming, persistence across a restart and launcher start/stop checks passed.
- Structured tool requests worked in later tests. A full autonomous coding/execute/recovery loop remains unverified.
- A 32-capacity expert-cache configuration improved short tests; concise coding instructions and prompt-lookup drafting also looked promising.
- The original launcher was retained as fallback.

No local PC control or usable shell is available in this continuation session. Do not turn documentation verification into a claim of fresh laptop measurements.

## Hardware and setup to verify first

User-supplied target machine: Windows laptop, RTX 4070 Laptop GPU, 24 GB DDR5 RAM (16 + 8), 1 TB storage. Exact CPU, GPU VRAM, free RAM, disk model/speed and installed runtime version must be recorded from the actual machine before tuning. An 8 GB GPU was the planning assumption, not a fresh measurement in this handover.

Reported working folder:
%USERPROFILE%\Documents\TryOut-Project\private-ai\local-chat

Reported launchers:
- Start-Local-Chat.cmd — original fallback
- Start-Fast-Local-Chat.cmd — tuned configuration
- Draft-Code.cmd — streaming code drafting; saves output for review and does not execute it

Reported UI: http://127.0.0.1:8080.
Python 3.12 was installed project-locally via a maintained distribution, with pinned packages. Exact patch, distributor and dependency versions are not available here. Read the actual environment before adding or upgrading anything.

The installed model was described as Qwen 35B. Qwen3.6-35B-A3B is a candidate identification, not a verified local checkpoint ID. Record its directory metadata, quantization and hashes. Qwen3-Coder-30B-A3B was researched as a second coding model; its installation was NOT confirmed.

## What we know about performance

See [experiment register](research/EXPERIMENTS.md). These are exploratory prior reports, not reconstructed raw measurements:
- One short response: 13.95 s → 7.98 s; the prior chat then reversed run order rather than treating that single warm-cache-sensitive trial as conclusive.
- Later small paired tests reported average latency reductions of about 34% (short coding) and 18% (tool request).
- Three paired tests reported faster first visible text using shorter coding instructions; no numeric table is available.
- Prompt lookup helped one repetitive code edit; no numeric table is available.

Do not claim a general percentage speedup. Missing raw timing logs, exact prompts, token counts and configuration snapshots prevent that.

## Immediate work

1. Pull/read the latest shared log and answer Q1–Q3 with primary sources and version-specific limits. Do not invent the other model's response.
2. Recover sanitized exact configuration and historical test artifacts from the PC if access is available. Keep private files local. Record unavailable evidence honestly.
3. Establish a reproducible baseline with [the protocol](research/BENCHMARK_PROTOCOL.md) and a held-out workload.
4. Re-test cache capacity and concise instructions as separate variables. Measure end-to-end time to first visible answer text, completion time, tokens/sec, peak memory, errors and coding correctness.
5. Only then evaluate a second coding model, side by side; preserve the current model and launchers.
6. Propose one reversible improvement with a rollback and a measured acceptance gate.

Colibri's current upstream source has moved forward. Read flags supported by the INSTALLED version, not just main. A 32-expert cache cap is not 32 concurrent chats/KV slots. Cache history is placement telemetry, not learned model knowledge. Prompt lookup is not a generally interchangeable small draft model. See sources.

## Working agreements

- One agent owns a laptop experiment at a time; the other reviews method/results. Avoid competing model servers, concurrent benchmark traffic or simultaneous launcher edits.
- Preserve each author's co-chat turns and Mohamed's decisions. Never fabricate an agreement.
- Separate proposed, historically reported, reproduced, rejected and adopted findings.
- Keep the original launcher runnable; try one process-scoped override at a time.
- No model auto-execution of generated code. Human-reviewed drafts are the verified coding capability so far. Future execution needs a separate isolated design and tests.
- No passwords, local.env, private prompts/chats, unredacted logs, tokens, model weights or personal data in GitHub.
- Do not disable authentication, widen loopback binding or change firewall rules as a speed fix.
- A Codespace can edit/test repository utilities but does not have Mohamed's laptop GPU or direct access to laptop loopback.
- Run only bounded research/experiments; record a checkpoint instead of leaving indefinite token-consuming loops.

## Next response requested from Claude

In research/co-chat.md, post your own sourced answers to Q1–Q3 and challenge any unsupported claim in this briefing. If you cannot reach the PC, state that and still supply a version-aware test design. No environment secrets are required just to review these documents.

## Round 2 clarification

A separate PC worker can reach the laptop; this session's missing shell does not block project-wide execution. [I001](research/experiments/2026-11-14-pc-inventory.json) now records verified worker observations of Colibri 2.0.0, Vulkan, cap 4 versus 32 and native lookup engagement. Immutable model revision and raw benchmark artifacts remain pending.

Claude has answered and asked Q4/Q5; see the real replies in [co-chat](research/co-chat.md). The [protocol](research/BENCHMARK_PROTOCOL.md) is revised after review. The worker's harness is still partial pending Arabic fixture and immediate-stop corrections; the latest connection/health check succeeded. No full cache A/B is complete. Read [R001](research/experiments/2026-11-14-output-budget.json) as a preliminary completeness test, not a speed proof.

Latest checkpoint: the offline planner/validator preparation artifact now passes 27 reported tests, superseding the earlier fixture defect. The full benchmark runner is still absent; no cache A/B batch ran. Review I001 and the latest co-chat turn before acting on historical handoff status.
