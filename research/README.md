# Research: map and reading order

Everything under `research/` is one of four kinds: **code** that runs, **evidence** that was measured
or audited, **plans** and designs, and the **log**. This page says which is which.

## If you have ten minutes

1. [FINAL_GOAL.md](FINAL_GOAL.md): the six checks that define "done".
2. [../docs/CURRENT_STATE.md](../docs/CURRENT_STATE.md): the dated status of each.
3. The README of whichever code folder you want to work on.

## Code

Each folder is self-contained, has its own README with a revision history and review status, and
runs offline with the standard library. `teach-store/` and `gateway-admission/` are copies of files
from the private laptop project; `coding-quality-v1/` and the adapter prototype were written in this
repository. Run all of them with `python tools/run_all_tests.py` from
the repository root.

| Folder | What it does | Tests | Review status |
|---|---|---|---|
| [teach-store/](teach-store/) | `teach_store.py`: the notes store (add, list, disable, purge, recover) with locking and crash recovery. `teach_hook.py`: the gateway hook that adds applicable notes to a chat request and reports what it left out | 109, 5 skipped | Reviewed offline through revision 18 |
| [gateway-admission/](gateway-admission/) | `chat_contract.py`: what a chat request may contain and whether it fits the context. `token_count.py`: the real token count, bound to one served profile. `gateway_auth.py`: the gateway's auth hook | 30, 6 skipped | Reviewed offline, including reason codes |
| [teach-status-adapter-prototype/](teach-status-adapter-prototype/) | Carries the hook's decision to the response stream and shows one fixed status line when notes were left out. Built on a status core written on the ChatGPT side | 46, 5 skipped | Revision 3 reviewed offline. Not loaded anywhere |
| [coding-quality-v1/](coding-quality-v1/) | CODE-Q1: 12 frozen tasks with 116 authored cases, `grade.py` (static and gated behavioural grading), a token preflight, and the model's first-pass drafts | 31 | Fixture revision 2. First-pass drafts graded in Windows Sandbox: 11 of 12 pass ([details](coding-quality-v1/sandbox/README.md)); harness not independently reviewed |

Skipped tests need the laptop's tokenizer file, its gateway settings, or the LiteLLM library.

## Evidence

| Path | What it shows |
|---|---|
| [context-preflight/](context-preflight/) | Count comparisons between the gateway and the engine: 24 saved requests, then a few Arabic, multi-turn and long requests on the laptop, each with difference 0. These cover the shapes tested and are not a general proof. Source audits of how the engine counts and limits tokens |
| [experiments-claude/2026-11-14-cap4-cap32-exploratory/](experiments-claude/2026-11-14-cap4-cap32-exploratory/) | Cache setting 32 against 4: 705 s against 962 s over 48 requests. Exploratory |
| [experiments-claude/2026-11-14-window8/](experiments-claude/2026-11-14-window8/) | Three stop-start cycles, a 20-request session, boundary probes and a network-endpoint check on the laptop |
| [experiments-claude/2026-11-15-scratch-asgi/](experiments-claude/2026-11-15-scratch-asgi/) | A synthetic test through LiteLLM's real proxy application to a fake upstream: exact upstream body, status framing, and disconnects. Includes the fixture source |
| [experiments/](experiments/) | Independent review records, one JSON file per review, each pinned to a commit |
| [audits/](audits/) | Independent recomputation of published results |
| [gateway-admission-review.md](gateway-admission-review.md), [gateway-reason-codes-review.md](gateway-reason-codes-review.md), [teach-status-adapter-review.md](teach-status-adapter-review.md), [window8-observation-intake.md](window8-observation-intake.md) | Review write-ups for the code folders and the laptop observations |

## Plans, designs and background

| Document | What it is |
|---|---|
| [FINAL_GOAL.md](FINAL_GOAL.md) | The agreed goal and its six acceptance checks |
| [INTEGRATION_QUEUE.md](INTEGRATION_QUEUE.md) | Open work items and who is doing each |
| [ROADMAP.md](ROADMAP.md) | The longer-term order of work |
| [teach-status-display-contract.md](teach-status-display-contract.md) | Design for showing teaching status in the chat page |
| [WINDOWS_ISOLATION_PROPOSAL.md](WINDOWS_ISOLATION_PROPOSAL.md) | Proposal for grading generated code inside Windows Sandbox |
| [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md), [EXPERIMENTS.md](EXPERIMENTS.md) | How laptop benchmarks are to be run and registered |
| [PC_TEST_REQUEST.md](PC_TEST_REQUEST.md) | The current bounded request to whoever operates the laptop |
| [MODEL_CANDIDATES.md](MODEL_CANDIDATES.md) | Other models considered. None adopted |
| [CLAUDE_INDEPENDENT_RESEARCH_2026-11-14.md](CLAUDE_INDEPENDENT_RESEARCH_2026-11-14.md) | Claude's survey of ways to make the assistant faster, better at code and teachable |
| [OPTIMIZATION_REVIEW.md](OPTIMIZATION_REVIEW.md), [RUNTIME_MEMORY_RESEARCH_2026-11-14.md](RUNTIME_MEMORY_RESEARCH_2026-11-14.md), [2026-11-14-coding-reliability.md](2026-11-14-coding-reliability.md) | Research notes on speed, memory and coding reliability |
| [VERSION_VERIFICATION_2026-11-14.md](VERSION_VERIFICATION_2026-11-14.md), [MANIFEST_REVIEW_2026-11-14.md](MANIFEST_REVIEW_2026-11-14.md) | Checks of software versions and of launcher changes |
| [SOURCES.md](SOURCES.md) | Primary sources cited across the research |
| [briefing.md](briefing.md), [ROUND3_REVIEW.md](ROUND3_REVIEW.md) | Early briefing and review. Historical |

## The log

[co-chat.md](co-chat.md) is the append-only conversation between the two assistants, from the first
briefing to the present. It is long. Read it from the end backwards: the latest turns say what is
open, and each turn names the commit it answers. The conventions are in
[../CONTRIBUTING.md](../CONTRIBUTING.md).

## Reading a result here

Three habits of this project are worth knowing before you trust or doubt a number:

- **Scope travels with the result.** "Passed" always names a commit and what was checked. A pass on
  published source is not a statement about what the laptop is running.
- **Loaded is separate from reviewed.** Code can be reviewed and not loaded, or loaded by inference
  only. READMEs say which.
- **Timings taken during a large download are marked contended.** They are not benchmarks.
