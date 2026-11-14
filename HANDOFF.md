# Handoff — Claude cloud session → next session

Written by Claude on 2026-11-14, at the end of a cloud session that could not reach the laptop.
Read this after [CLAUDE_BRIEFING.md](CLAUDE_BRIEFING.md). It records what this session did and what is still open.

## Where things stand

| Item | State |
|---|---|
| Repository | `mms20102/Local-AI-tests`, private |
| `main` | `19ef0fe` — ChatGPT/Codex handover (briefing, docs, research files, round 1 questions) |
| `claude/cloud-environment-setup-ha4b84` | `main` plus Claude's round 1 replies and this file. **Not merged into `main`; no pull request opened** |
| Shared log | [research/co-chat.md](research/co-chat.md) |
| ChatGPT's reply to Claude | Not received yet. Q4 and Q5 are waiting on ChatGPT |
| Laptop access | None from the cloud session. No laptop measurement exists from Claude |
| Cloud environment | Still the account's Default. No setup script, hosts, keys or variables were saved. None are needed for this work |

## What this session did

1. Created `research/co-chat.md` (first version, before the briefing existed).
2. Read the briefing and every linked file at `19ef0fe`.
3. Re-read the Colibri documentation at the pinned snapshot `0a5504a1dc64f86fcd0fe7db298b0448c730e7e6`: README, SETTINGS, tuning, speculative, api, qwen36, plus ENVIRONMENT, qwen36-cuda-tier and routing-telemetry.
4. Posted Claude's turns in the log: A1.2, A2.2, A3.2, six challenges to the briefing, Q4, Q5 and an ownership proposal.

## Claude's main findings (all from upstream docs, none measured locally)

- **Cache gain (H001/H002):** the baseline cache size was never recorded. Without `--cap`, the engine sizes the cache from free RAM at start, so the old comparison may not have had a fixed baseline. `--ram` has no effect on the qwen36 engine. A cap of 32 is about 2.2 GB of roughly 17.4 GB of experts (derived), so 32 is one point on a curve, not an optimum.
- **Missing controls:** the OS file cache and KV prefix reuse both make a second run faster. Use a fresh engine process per arm, `KVSAVE=0` or new conversations, `USAGE_SAVE=0` when a GPU tier is on, explicit `--cap` in both arms, temperature 0, and at least six AB/BA pairs.
- **Prompt lookup (H004) is in doubt:** it is on by default from engine 1.13.0, and it is disabled under a CUDA tier that holds only part of the experts, which an 8 GB card forces. Upstream gain where it works: 6–7% on a code edit, none on chat.
- **Qwen3-Coder-30B-A3B:** second route only. Needs about 80 GB free disk to download and convert; 6.5 GB resident at cap 32, 15.2 GB at cap 128. Proposed gate: 12 held-out coding tasks, at least 2 more passes than baseline, or equal passes at least 25% faster, with 3 GB RAM free and no hard paging.

Full reasoning and sources are in the log.

## Blockers

- **Laptop:** the cloud session listed four Remote Control folders on two PCs (`DESKTOP-K1GB41Q`, `DESKTOP-AIN4NRQ`); none was offered to cloud sessions, and `local-chat` was never in the list.
- **Shared local log:** not possible from the cloud. GitHub is the only copy both assistants can reach.

## Next steps, in order

1. **Start a session on the AI laptop** in `C:\Users\User\Documents\TryOut-Project\private-ai\local-chat` (Claude desktop app), with this repository cloned beside it, not inside it.
2. **Pull first.** Check `main` and the Claude branch for new ChatGPT turns before writing anything.
3. **Read-only inventory (experiment P001).** Engine version and commit, build backend, both launchers' command lines and environment with secrets removed, `coli plan --json`, `coli doctor --json`, any saved profile in `%LOCALAPPDATA%\colibri\tuning`, the container's `qwen36_meta.json` and sizes, CPU model, `nvidia-smi`, free RAM and disk. Post a sanitized summary in the log.
4. **Answer Q4 from the inventory** if ChatGPT has not: which backend and version the fast launcher uses.
5. **Smoke test (P002)**, then the cap reproduction (P003) as designed in A1.2. One owner at a time; agree the owner in the log before any benchmark traffic.
6. Lookup check (A2.2) and the coder-model gate (A3.2) only after that.

Not yet written: the inventory script and the streaming timing client that Claude offered. Mohamed has not confirmed the ownership proposal.

## Decisions waiting on Mohamed

- Merge the Claude branch into `main` (pull request), or have ChatGPT read the branch.
- Confirm or change the ownership proposal at the end of Claude's round 1 replies.
- Push after every reply, or hold commits until told.

## Rules that carry over

- Write only your own turns. Never write or edit ChatGPT's. Add, do not rewrite.
- Label every claim: documented, derived, reported, unverified or measured.
- Nothing private goes to GitHub: no `local.env`, keys, logins, chats, raw logs or model files.
- Keep the original launcher runnable. One change at a time, with a rollback.
- No model-generated code is executed automatically.
- Do not touch the Al-Mu'jiza project.

## Getting the files on the laptop

```bash
git clone https://github.com/mms20102/Local-AI-tests.git
```
```bash
git -C Local-AI-tests checkout claude/cloud-environment-setup-ha4b84
```
