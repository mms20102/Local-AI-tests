# Local-AI-tests

Mohamed's private research workspace for improving local AI response speed, coding quality and reviewed persistent context.

The working laptop stack is **Open WebUI → LiteLLM → Colibri → Qwen**. This repository records evidence and separate proposals; cloud tests do not measure the laptop GPU.

## Current checkpoint — 2026-11-14

**Runtime coordination:** consult the [active co-chat](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md) before PC work. Window 4 results are exploratory; a later window-5 closure reports the teach hook **enabled with an empty store**, not independently verified here. Independent rev7 review found a request-path logging failure. Rev10 passed targeted offline checks (78 passed, 5 skipped), with no blocking regression in scope; output shape is not issued-ID provenance, and synchronous logging can still block. After a reported restart, the exact loaded hook revision is independently unverified. No runtime change is made here.

**Independent runtime checkpoint:** after window 3 closed, the PC worker confirmed 2.0 running with its prior verified binary hash, no 2.1 process, unchanged original launchers and a clean tree at local 7111656. Workbench checksum drift and a missing 2.1-launcher manifest entry need [source review before trust renewal](research/MANIFEST_REVIEW_2026-11-14.md). No tests were rerun or files changed. Recheck [active reservations](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md) before local work.

| Workstream | Verified or reported progress | Next boundary |
|---|---|---|
| Teach store | Rev6 persistence and rev10 diagnostic hardening have scoped independent offline passes | Callback enabled is reported; exact loaded revision/live invariance are unverified; synchronous output can still block |
| Coding quality | Claude published 12 frozen tasks, 116 authored cases and a gated grader; 31 grader tests reported passing | No model pass rate. Generated-code execution is disabled; reviewed semantic isolation is absent |
| Cache experiment | [Exploratory result audit](research/audits/cap4-cap32-exploratory-audit-2026-11-14.md): arithmetic reproduces 26.73% lower recorded completion time | Split invocations with lifecycle failure; no semantic assessment. Full schema-4 study still not run |
| Operational components | PC worker reported bounded SSE/journal/collector checks, including 109 isolated tests at that checkpoint | Local-only components; publication blocked. No full-run readiness claim |
| Context preflight | 25 prompt/reference blobs matched; Claude reports 118–300 rendered input and 31–137 reference tokens | Binary-added tokens remain null; no full-engine fit claim |

Start with [current state](docs/CURRENT_STATE.md), [next worker packet](research/PC_TEST_REQUEST.md) and [context audit](research/context-preflight/README.md).

## Where active work lives

- [Live shared co-chat on Claude's branch](https://github.com/mms20102/Local-AI-tests/blob/claude/cloud-environment-setup-ha4b84/research/co-chat.md) — read the latest turn before replying.
- [Reviewed teach revision 6](https://github.com/mms20102/Local-AI-tests/tree/015a2ecd63468445b9ebed1f01b95291fa577177/research/teach-store).
- [Frozen CODE-Q1 fixtures](https://github.com/mms20102/Local-AI-tests/tree/de9398a167b64c79510b470b7d60b3a0931aad04/research/coding-quality-v1).
- [Published schema-4 planner](https://github.com/mms20102/Local-AI-tests/tree/974e667cfdcc389a56797f042dcb61cc13d435be/research/planners/cap4-cap32-schema4).

Main and Claude's branch have diverged; these links are intentional. No merge or branch reset is implied. Draft PR #1 is also the coordination webhook bridge and remains open and unmerged. The coordinator observed a real wake; delivery/continuity is not guaranteed.

## Working rules

The PC worker owns runtime operations; Claude owns the teach implementation and CODE-Q1 fixtures; Codex maintains shared evidence and coordinates review. Claude completed a reported renderer/tokenizer preflight. Binary-added tokens and independent installed-renderer parity remain unresolved.

Preserve the working launcher/model and all authors' turns. Keep credentials, private chats, raw personal logs, model weights and `.git` folders out of handoffs. Do not execute generated code or enable the teach hook under the current offline work.

[Roadmap](research/ROADMAP.md) · [Benchmark protocol](research/BENCHMARK_PROTOCOL.md) · [Runtime source research](research/RUNTIME_MEMORY_RESEARCH_2026-11-14.md) · [Version/advisory verification](research/VERSION_VERIFICATION_2026-11-14.md) · [Initial briefing](CLAUDE_BRIEFING.md)

Earlier documents remain in Git history. This update replaces stale landing-page checkpoints; it does not publish the blocked benchmark components or establish a performance gain.

The exploratory audit independently recomputes published metadata; it does not rerun static grading or execute model outputs. Source results, including the first invocation's aborted/failed-restoration status, remain unchanged.
