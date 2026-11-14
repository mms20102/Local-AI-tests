# Local-AI-tests

A private, local AI assistant on one Windows laptop, and the evidence for what it can and cannot do.

The assistant runs entirely on the laptop: no cloud inference, no subscription. This repository holds
the parts of that work that are safe to publish: the code that was written for it, the tests, the
measurements, and a running log of two AI assistants (Claude and ChatGPT) reviewing each other's work
for the owner, Mohamed.

```
Browser  →  Open WebUI  →  LiteLLM gateway  →  Colibri engine  →  Qwen3.6-35B model
            (chat page)    (auth, limits,      (inference on      (23 GB, int4)
                            teaching notes)     GPU + RAM + SSD)
```

The laptop: Ryzen 9 7940HS, 23 GiB usable RAM, RTX 4070 Laptop (8 GB), Windows 11.

## The goal

> Give Mohamed a private local assistant he can use every day for routine coding in Arabic or English:
> complete, reviewable answers; demonstrated correctness on a declared task set; useful response times;
> editable teaching notes; and simple, recoverable operation, without a required inference subscription.

Six checks define "done". The full wording and thresholds are in
[research/FINAL_GOAL.md](research/FINAL_GOAL.md).

| # | Check | Where it stands (2026-11-15) |
|---|---|---|
| 1 | Long conversations, with the full answer allowance reserved | Working on the laptop for the request shapes tested: a 1,717-token prompt with the full 256-token answer, Arabic, and multi-turn. Over-long requests are refused with a clear reason. Not a proof for every conversation; the 32-token margin is a judgment |
| 2 | Coding quality: at least 9 of 12 tasks pass on the first attempt | 12 of 12 answers are complete and well-formed. They have not yet been run against their 116 test cases; that grading has been handed to the independent reviewer |
| 3 | Speed: median 15 s to first useful text, 60 s per task, counted only for correct answers | Not measured yet. An exploratory run gave 34.9 s per task and 16.1 s to first text, while a large download was running and without checking correctness |
| 4 | Start, stop and recover without help | Three clean stop-start cycles and a 20-request session. An owner guide exists on the laptop |
| 5 | Teaching notes with visible limits | Store and hook reviewed through revision 18. An in-chat "notes left out" notice is a tested prototype, not loaded |
| 6 | Private operation | In one 82-second sample the stack's processes connected to nothing outside the laptop. Sampling, not a packet capture |

For the detailed, dated status with every qualification, see [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md).

## Quick start

You need Python 3.12 or newer. No packages are required.

```
git clone https://github.com/mms20102/Local-AI-tests.git
cd Local-AI-tests
python tools/run_all_tests.py
```

Expected: 229 tests run in 5 suites, 16 of them skipped, every suite passing. This is the count on
2026-11-15; it grows. The skipped tests need files
that exist only on the laptop (the model's tokenizer, the gateway's settings) or the LiteLLM library.
Nothing in the test suites starts a service, calls a model or uses the network. The same command runs
on GitHub for every pull request, on Linux and Windows.

## What is in here

| Path | What it is | Runs offline |
|---|---|---|
| [research/teach-store/](research/teach-store/) | The teaching notes: a small store of rules and facts the owner writes, and the gateway hook that adds them to chat requests | 109 tests |
| [research/gateway-admission/](research/gateway-admission/) | The gateway's request check: text-only rules, and admission by real token count | 30 tests |
| [research/teach-status-adapter-prototype/](research/teach-status-adapter-prototype/) | Prototype: one status line in a streamed answer when notes were left out | 46 tests |
| [research/coding-quality-v1/](research/coding-quality-v1/) | CODE-Q1: 12 small coding tasks (9 English, 3 Arabic), 116 test cases, a grader, and the model's first-pass answers | 31 tests |
| [research/context-preflight/](research/context-preflight/) | Comparisons of the gateway's token count with the engine's for the request shapes tested, with their limits | data and audits |
| [research/experiments-claude/](research/experiments-claude/) | Measurements taken on the laptop, with the scripts that produced them | data |
| [research/experiments/](research/experiments/), [research/audits/](research/audits/) | Independent review records | data |
| [research/co-chat.md](research/co-chat.md) | The shared log between the two assistants. Append-only | — |
| [tools/](tools/) | `run_all_tests.py`, and a watcher that reports new turns in the log | 13 tests |
| [docs/](docs/) | Architecture, current state, glossary, history | — |

A fuller map with a suggested reading order is in [research/README.md](research/README.md).

## What is not in here, on purpose

The laptop project itself is private and is not published: its launchers, configuration, keys, chats,
logs, and the model files. What appears here from that project was copied file by file with the
owner's approval. See [SECURITY.md](SECURITY.md) for the rules.

## How the work is done

Two assistants work for the owner and check each other. Neither result counts until the other side
has had the chance to break it.

- **Claude** works on the laptop: writes most of the code here, runs the model, takes measurements.
- **ChatGPT** works from the published files: reads source, audits numbers, writes designs and some
  code, and relays an independent reviewer who runs the published tests in a separate environment.
- **The owner decides.** Scope, targets, anything that restarts the laptop's services, and anything
  published from the laptop need his word.

Every claim in the log is labelled *measured*, *recorded*, *derived*, *documented*, *reported* or
*inferred*, so a reader can tell an observation from a conclusion. The full conventions are in
[CONTRIBUTING.md](CONTRIBUTING.md), and the terms used throughout are in
[docs/GLOSSARY.md](docs/GLOSSARY.md).

## Branches

Work currently lives on two lines that this branch combines:

- `main`: documentation, audits and review records.
- `claude/cloud-environment-setup-ha4b84`: the code, the laptop measurements and the shared log.

A draft pull request from the second into the first stays open as the coordination channel. Merging
it is the owner's decision.

## Documents worth reading first

1. [research/FINAL_GOAL.md](research/FINAL_GOAL.md): what "done" means.
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): how the pieces fit.
3. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md): the dated status.
4. [research/README.md](research/README.md): where everything else is.

The previous landing page is kept as
[docs/history/README-checkpoint-2026-11-14.md](docs/history/README-checkpoint-2026-11-14.md).

## License

No license has been chosen. Until the owner adds one, all rights are reserved: you may read the
repository, but there is no permission to reuse the code.
