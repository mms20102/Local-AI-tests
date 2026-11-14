# Local-AI-tests

Private research workspace for Mohamed, Claude and Codex/ChatGPT.

**Start with [CLAUDE_BRIEFING.md](CLAUDE_BRIEFING.md), then [research/co-chat.md](research/co-chat.md).**

The project improves an existing Windows local workbench: Open WebUI → LiteLLM → Colibri → Qwen. The focus is measured response speed, coding correctness and tool reliability.

## Documents
- [Current state and evidence](docs/CURRENT_STATE.md)
- [Architecture and cache distinctions](docs/ARCHITECTURE.md)
- [Historical reports and experiment queue](research/EXPERIMENTS.md)
- [Benchmark protocol](research/BENCHMARK_PROTOCOL.md)
- [Model comparison plan](research/MODEL_CANDIDATES.md)
- [Roadmap](research/ROADMAP.md)
- [Primary sources](research/SOURCES.md)

This initial handover reconstructs the visible project history. Prior laptop test reports are explicitly labelled reported until raw artifacts or new measurements support them. No new laptop benchmarks were run by this documentation session.

The shared log contains each assistant's own turns only. Repository updates do not automatically wake another assistant; pull the latest branch before replying.

Do not commit local.env, credentials, private logs/chats, personal data or model weights. Codespaces/cloud checks do not measure the laptop's GPU. Preserve the working launcher and model while testing alternatives.

## Latest review round

Claude's genuine replies and ChatGPT's responses are in [co-chat](research/co-chat.md). Read the appended round 2 for current status; [Claude's HANDOFF.md](HANDOFF.md) remains an earlier author-preserved snapshot.

- [Optimization review](research/OPTIMIZATION_REVIEW.md)
- [Installed inventory and preparation artifact](research/experiments/2026-11-14-pc-inventory.json)
- [Output-budget test report](research/experiments/2026-11-14-output-budget.json)
- [Next worker evidence/test requests](research/PC_TEST_REQUEST.md)

An offline planner/validator package is prepared. It is not a full runner, and no new cache A/B batch is complete.
