# Independent research: faster, better at code, and teachable

Date: 2026-11-14. Author: Claude (laptop session), at Mohamed's request. This is independent of the ChatGPT/Codex research streams; I did not read their conclusions into it, and where we overlap I say so at the end.

**What I did:** three web-research passes (speed and hardware, memory and teaching, coding tools), a fourth pass that re-read the primary pages to check the claims that matter, and read-only inspection of the laptop. No model request was sent, nothing was restarted, no setting was changed, nothing was installed.

**Labels:** *measured* = I observed it on this laptop today; *documented* = stated on a primary page that was re-read for this report; *reported* = third-party measurement or secondary source, not checked further; *inference* = my reasoning.

## Summary

1. **The slow part is the experts that do not fit in memory, not the GPU.** In today's live session the engine spent about 119 s on CPU-side expert work against about 18 s waiting on the GPU (*measured*). The 23.0 GB model does not fit in 23.2 GiB of RAM, so about half of the CPU-side expert requests go to disk (*measured*).
2. **The same model is reported at 24–39 tokens/s on older 8 GB and 12 GB cards with 32 GB RAM** under llama.cpp (*reported*). This laptop produces roughly 3 tokens/s (*inference* from the log). RAM is the most likely difference. A RAM upgrade is the single change with the strongest evidence behind it.
3. **Before spending money, three free steps are worth testing:** Colibri 2.1.0 beside 2.0.0, a larger context window, and a second small model that fits entirely on the GPU for quick answers.
4. **"Teachable" is realistic today as memory, not as retraining.** A reviewed rule-and-fact store plus retrieval works on this hardware once the context is larger. Retraining the 35B model on this laptop is not feasible; retraining a small companion model is.
5. **No coding agent works at a 2,048-token context.** The lowest documented floor is about 22,000 tokens. Context has to grow before any agent is worth trying.

## 1. Where the time goes (*measured*)

From the redacted engine log of the session started 11:08 with the fast launcher, cumulative over 13 requests:

| Quantity | Value |
|---|---|
| Model forward steps | 339 |
| Waiting for the GPU (dense chain, GPU-tier experts) | 17.6 s |
| Routed experts computed on the CPU, including disk loads | 119.1 s |
| CPU-side expert time per step | about 350 ms |
| CPU-side expert requests served from RAM / from disk | 51,678 / 55,306 (first 11 requests) |

The two times can overlap, so they are not an exact wall-clock split. The proportion is still clear: the GPU is not the limit. Anything that keeps more experts in memory, or uses a model with fewer experts off the card, attacks the right problem.

**Memory state (*measured*):** commit charge 31.08 of 32.22 GiB; 5.98 GiB "available", of which 5.89 GiB is standby cache; pagefile 9 GiB allocated, system-managed, 0.1 GiB used. *Documented* by Microsoft: the commit limit is physical memory plus page files, and a system-managed pagefile grows when commit reaches 90% of the limit, "assuming enough free disk space". This machine is at 96.5% with 457 GiB free, so why it has not grown is unexplained.

## 2. Speed: options in order of evidence

| # | Option | Evidence | Cost and risk | Reversible test |
|---|---|---|---|---|
| 1 | **RAM to 2×16 GB or 2×32 GB** | *Reported:* Qwen3.6-35B-A3B at 32.8 tok/s (RTX 2080 8 GB), about 24 (GTX 1080 8 GB), 38.9 (RTX 3060 12 GB), all with 32 GB RAM under llama.cpp. *Documented:* Colibri asks for "~30 GB RAM for comfortable expert caching". *Reported:* single to dual channel raised CPU decode by a mean 56% on another machine; the present 8+16 GB pair is asymmetric. | Money. The laptop's supported maximum must be checked with the maker first; I did not find it. | Hardware; keep the old modules. |
| 2 | **Colibri 2.1.0 beside 2.0.0** (released 2026-10-31) | *Documented:* KV caches are float16 by default; experts the card cannot hold stay in a host RAM pool computed by the CPU; side requests "park" the conversation (Qwen3.6 on CPU 51.6 s to 3.3 s a turn); "Windows heap and memory fixes". | New defaults; six commits already follow the release. No 8 GB laptop figure for Qwen3.6 exists upstream. | Unpack to a second folder, same prompts, compare; delete to revert. |
| 3 | **Second, small model fully on the GPU** for quick answers and code drafts | *Reported:* Qwen3.5-9B at about 55 tok/s with 32K context on an RTX 3070 8 GB (7.0 GiB VRAM). | Lower quality than the 35B. It cannot share the card with the 35B, so it is a switch, not a pair. Disk and a second runtime if Colibri cannot load it. | Second launcher; original untouched. |
| 4 | **Larger context** | *Measured (planner estimate, engine running):* 2,048 to 8,192 tokens adds about 240 MiB of state; 16,384 adds about 560 MiB. *Documented:* float16 KV in 2.1.0 halves this. | Commit headroom is only about 1 GiB now. Long prompts take longer to read. | One launcher flag in a test profile. |
| 5 | **MTP head** (`Q36_MTP=1`, 2.1.0) | *Documented:* Vulkan decode 83–84 to 100–109 tok/s, GPU not named. *Reported:* on low-VRAM setups under llama.cpp it was slower. | May lose here, where half the experts are off the card. | One environment variable. |
| 6 | **Prompt lookup** (already on) | *Documented:* +6–7% on code edits, nothing on free chat. *Measured:* it engages here (1.15–1.72 tokens per step on edits). | None; the gain has not been measured on this laptop. | Already planned by the PC worker. |

Not recommended: more KV slots (*documented* in the 2.0.0 source by ChatGPT, and *measured* in the installed binary's messages: it turns the GPU dense chain off), large pages, and a bigger GPU tier or RAM cache while commit headroom is about 1 GiB.

One upstream figure I checked and am **not** relying on: the Vulkan guide mentions 63 tok/s on an RTX 3070 for Qwen3.6, but the passage does not say how many experts were on the card, and a nearby passage with 2,756 of 10,240 experts on the card describes much slower steps.

## 3. Teachable and live

Interpretation I used: the assistant should remember what Mohamed teaches it across sessions, improve from corrections, and stay current, locally and privately.

**Stage 1 — memory, no weight changes (do first).**

- **A reviewed rule-and-fact store.** A plain local file of short rules ("always answer code questions with a test"), facts and corrections. Mohamed adds entries with a "teach" command; the gateway injects the relevant ones into each request within a fixed token budget. Every entry is dated, listed and deletable. This fits the project's existing strict gateway, needs no new service, and is the safest form of teaching: nothing is learned without review (*inference*).
- **Retrieval over Mohamed's own files and past chats.** *Documented:* Open WebUI has built-in Knowledge (retrieval) and Memory features; memory injection is capped at 2,000 characters by default, which alone would fill half of a 2,048-token window. *Documented:* Open WebUI's own guidance for retrieval assumes 8,192 tokens or more. So context must grow first.
- **Embedding model.** *Documented (model cards):* BAAI/bge-m3 (MIT, dense and sparse, 8,192-token input) with bge-reranker-v2-m3 (Apache-2.0). *Reported:* bge-m3 led a 2025 Arabic retrieval study. Run it on the CPU. It competes with the model for RAM (*inference:* 1–3 GB), which is one more reason for the RAM upgrade.
- **Keep automatic memory writing off.** *Reported:* published attacks plant false memories through ordinary content. Memory should change only when Mohamed approves an entry.

**Stage 2 — teaching by retraining a small model.**

- *Documented (Unsloth requirements):* QLoRA needs about 3.5 GB of VRAM for a 3B model and 6 GB for an 8B model; a 32B model needs 26 GB. Retraining the 35B model on an 8 GB card is not feasible; a 3–8B model is.
- *Reported:* fine-tuning is good for style and format; retrieval beat it for new facts (0.875 against 0.504 in one 2024 study). So: retrieval for knowledge, fine-tuning for habits.
- Pipeline (*inference*): log corrections as prompt, wrong answer, corrected answer; curate by hand; at 300–1,000 examples train an adapter on a small model with the main model stopped; promote it only if it passes a fixed regression suite; keep the base model so rollback is a routing change.
- *Documented:* Colibri's Qwen3.6 guide does not mention adapters. Whether a retrained small model loads in Colibri is unverified; llama.cpp is the fallback.

**Stage 3 — research-grade, later.** A nightly job in which the model proposes merged or rewritten memories for Mohamed to approve ("sleep-time" consolidation, *reported*). Direct weight editing is not suitable: *reported* studies show it degrades a model after hundreds of edits.

**Staying current.** Scheduled indexing of chosen local folders is private. Web search (for example through SearXNG) sends queries out of the machine and brings untrusted text in; *reported* guidance (OWASP) is that retrieved text can carry instructions and no complete defence exists. If it is ever enabled, keep it per-chat and keep tools and code execution off in the same chat.

## 4. Coding

- **No constrained decoding for this model.** *Documented:* Colibri's `tool_choice: "required"` is "a prompt-level instruction, not a sampling constraint", and its strict tool mode is for GLM models only.
- **Validate and retry instead.** *Reported:* one Qwen coder model went from 6.75% first-try success on a complex schema to over 99.8% with a validate-and-retry loop. Add schema validation of tool arguments and one bounded retry to the existing draft helper. Tools still execute nothing.
- **A private regression suite before any other change.** 30–60 self-written tasks with hidden tests, half with Arabic instructions, reporting validity, required names, pass rate and time separately. This is close to ChatGPT's proposed 12-task study; the two should be one suite.
- **Agents need context.** *Documented:* OpenHands asks for at least 22,000 tokens; Colibri's own settings guide says coding agents need 64K. Aider is the only mainstream agent that needs no tool calling; try it on a scratch copy after the context reaches 16K.
- **Running generated code.** *Documented:* Windows Sandbox is hypervisor-isolated, can have networking disabled, and needs at least 2 GB. That exceeds today's headroom, so tests would run in a batch with the model unloaded. Python-level sandboxes are not isolation (*documented* in the Python manual).

## 5. Housekeeping and security

- **LiteLLM.** *Documented:* PyPI version 1.107.0 was malicious for about two hours on 21 October 2026. *Measured:* this project installed 1.108.5; the install reports and lock files never mention 1.107.0, and the files the incident report names (`cook.pth`, `sitecustomize.py`) are absent from both environments. *Documented:* advisory GHSA-2rwg-2wh4-7c4f (High, 12 November) is fixed in 1.108.6, and affects only deployments with Azure models, which this one does not have. Moving to 1.108.6 is still the tidy step.
- **Lock files with hashes** through `uv` and a few days' delay before accepting new releases (*reported* practice after the incident).
- **The local project folder is not a git repository.** Putting the code (not `local.env`, `.runtime` or `.validation`) under local version control would make every experiment reversible.
- **Open WebUI:** stay on Python 3.12 (*documented* upper bound below 3.13). Keep the "Auto" tool-permission mode off.

## 6. Proposed order

1. Private regression suite and local git (no risk, makes everything else measurable).
2. Colibri 2.1.0 in a second folder; rerun the planned cap 4 against 32 comparison on both versions.
3. Test profile with an 8K context once commit headroom is healthy.
4. Rule-and-fact store in the gateway, with a "teach" command and a review list.
5. Decide on RAM after steps 2–3: if the engine is still disk-bound, buy RAM; this is the step most likely to change the speed class.
6. Small GPU-resident second model as a fast route; later the base for retraining.
7. Retrieval over local files; validate-and-retry tool calls; Aider trial; sandboxed tests.

Steps 2, 3, 5 and 6 touch the running stack and belong to the PC worker and an agreed window. Steps 1, 4 and the offline parts of 7 can be built and tested without the model.

## 7. Limits of this report

- No speed figure for this exact laptop exists for any alternative; every outside number is from other hardware.
- The 24–39 tok/s llama.cpp reports are third-party posts that I did not verify, and all used 32 GB RAM.
- The per-token context cost is the planner's estimate, taken while the engine was running.
- The secondary sources in the three research passes were not all re-read; the claims marked *documented* were.
- Overlap with the ChatGPT streams: both sides name Qwen3-Coder and a small Qwen as candidates and both put the cap reproduction first. New here: the time split, the RAM evidence, Colibri 2.1.0, the context cost, the memory design, and the LiteLLM check.

## Sources

Colibri: [release 2.1.0](https://github.com/JustVugg/colibri/releases/tag/v2.1.0) · [changelog](https://raw.githubusercontent.com/JustVugg/colibri/main/CHANGELOG.md) · [Vulkan guide](https://raw.githubusercontent.com/JustVugg/colibri/main/docs/vulkan.md) · [Qwen3.6 guide](https://github.com/JustVugg/colibri/blob/main/docs/qwen36.md) · [API at 2.0.0](https://github.com/JustVugg/colibri/blob/v2.0.0/docs/api.md) · [settings](https://github.com/JustVugg/colibri/blob/main/docs/SETTINGS.md) · [speculation](https://github.com/JustVugg/colibri/blob/main/docs/speculative.md)

Windows: [page file](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file) · [Windows Sandbox configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file) · [Python audit hooks note](https://docs.python.org/3/library/sys.html)

LiteLLM and Open WebUI: [incident of 21 October 2026](https://docs.litellm.ai/blog/security-incident-oct-21-2026) · [GHSA-2rwg-2wh4-7c4f](https://github.com/BerriAI/litellm/security/advisories/GHSA-2rwg-2wh4-7c4f) · [Open WebUI memory](https://docs.openwebui.com/features/chat-conversations/memory) · [Open WebUI retrieval](https://docs.openwebui.com/features/chat-conversations/rag/)

Teaching: [Unsloth requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements) · [bge-m3](https://huggingface.co/BAAI/bge-m3) · [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) · [Arabic retrieval study](https://arxiv.org/pdf/2506.06339) · [fine-tuning versus retrieval](https://aclanthology.org/2024.emnlp-main.15.pdf) · [sleep-time compute](https://arxiv.org/abs/2504.13171) · [sequential editing failures](https://arxiv.org/abs/2401.07453) · [memory injection attack](https://arxiv.org/abs/2503.03704) · [OWASP prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)

Third-party speed reports (*reported*, unverified): [RTX 2080](https://lemmy.world/post/50066075) · [GTX 1080](https://prismix.dev/news/9d1e7a1cab26) · [RTX 3060 and GTX 1650](https://insiderllm.com/guides/best-way-run-qwen-3-6-35b-moe-locally/) · [8 GB model survey](https://localllm.in/blog/best-local-llms-8gb-vram-2025) · [dual-channel test](https://insiderllm.com/guides/dual-channel-ram-local-llm-cpu-inference/)

Coding: [OpenHands local models](https://docs.openhands.dev/openhands/usage/llms/local-llms) · [Aider edit formats](https://aider.chat/docs/more/edit-formats.html) · [validate-and-retry report](https://typia.io/blog/function-calling-harness-qwen-meetup-korea/) · [constraint cost study](https://www.alphaxiv.org/abs/2605.26128.md)
