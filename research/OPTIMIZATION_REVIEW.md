# Practical optimization review — 2026-11-14

This is a research/test plan, not a report of configuration changes. Claude has posted genuine replies on the shared branch. This review incorporates that exchange and new coordinator-relayed PC-worker evidence; see the appended round in co-chat.md.

## 1. Optimize time to a complete answer

A [new PC-worker report](experiments/2026-11-14-output-budget.json) compared output ceilings on a seven-function task:

| Ceiling | Elapsed | First text | Outcome |
|---|---:|---:|---|
| 32 tokens | 18.28 s | Not supplied | Truncated |
| 192 tokens | 30.41 s | 10.22 s | Reported complete; AST matched expected |

No generated code was executed. Minimum sampled free RAM was 5.62 GiB. Exact model/version, prompt, actual token counts, finish reasons and raw artifacts are missing.

The 32-token result is not an accepted speed improvement. An AST match does not establish functional correctness unless the matching criterion and semantic checks are supplied. 192 is adequate for this one reported task only.

**Proposed helper behaviour:** keep a task-appropriate configurable ceiling; retain the provider's finish reason; label length-limited output as incomplete; never present it as ready code. Allow a bounded, explicit continuation instead of a silent retry loop. Verify exact request parameters and gateway mapping before implementing. Upstream Colibri documents max_tokens/max_completion_tokens as ceilings and length as a possible stopping reason, including context clamping. [Colibri API](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/api.md)

## 2. Remove optional competing UI calls before adding a model

Open WebUI's official guide says UI tasks can call the chat model for titles, tags, follow-ups and autocomplete; unavailable task-model selections fall back to it. It exposes individual task switches. [Official task-model guide](https://docs.openwebui.com/features/administration/task-models/)

For this memory-limited laptop, my inference is to test disabling any enabled optional chores first. Do not start a second model just to generate titles. Confirm the installed version and effective admin settings; environment values alone are not proof of applied state. Record exact switches and restore them after the experiment.

**Proposed comparison:** same UI coding prompt, current settings versus optional chores disabled. Measure end-to-end latency and the number/type of inference requests. Trace only synthetic prompts; keep tokens, credentials and personal conversations out of artifacts. Do not disable retrieval or other functionality required by the task to claim a faster equivalent result.

Candidate switches, only if supported and currently enabled:
- ENABLE_TITLE_GENERATION
- ENABLE_TAGS_GENERATION
- ENABLE_FOLLOW_UP_GENERATION
- ENABLE_AUTOCOMPLETE_GENERATION

No such switch was changed here. No gain is measured yet.

## 3. Verify the effective concurrency settings

There is an upstream documentation conflict: api.md broadly describes qwen36 multi-slot dense-chain restrictions, while ENVIRONMENT.md and vulkan.md describe a newer qwen36 multiplexed dense-chain path, backed by c/qwen36_chain.h. A blanket statement that multiple slots always disable qwen36's Vulkan chain would therefore be unsafe. Installed version, partial-chain/device/KV-split constraints and actual startup/profile output must decide the test. [API](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/api.md#isolated-kv-contexts) · [Vulkan guide](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/vulkan.md) · [Chain implementation](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/c/qwen36_chain.h)

Do not confuse the reported expert cap 32 with 32 KV conversations. Record both independently. Avoid increasing concurrency as a speculative speed fix for single-user interactive work.

## 4. Protect prefix reuse

Stable system prompts and tool definitions can preserve reusable context; changing prefixes can add prefill work. Open WebUI's official [essentials guide](https://docs.openwebui.com/getting-started/essentials/#prompt-caching-kv-cache) discusses these sources of cache invalidation.

Test two successive synthetic turns through the full UI/gateway path. Determine whether an auxiliary task, changing prompt text or a template mismatch causes avoidable re-prefill. Use effective Colibri reuse/profiler evidence where available and compare direct API behaviour. Do not remove required context or tool definitions merely to reduce latency.

## 5. Current worker-verified inventory

[Inventory I001](experiments/2026-11-14-pc-inventory.json) records the coordinator's new report: Ryzen 9 7940HS, 23.22 GiB usable RAM, RTX 4070 Laptop 8188 MiB, Windows, AC, Vulkan. The historical cache comparison was cap 4 versus 32 on the same model. Logs show lookup engaged, but no lookup-off A/B proves its benefit. Further worker evidence identifies Colibri 2.0.0, context 2048, cap 32 (original 4), no thinking, temperature 0, one KV slot, no saved tuning profile, 3 GiB Vulkan expert-tier budget, eight OpenMP threads, and all 40 dense layers on the GPU. USAGE_SAVE=0 is already set, but history is still read. Lookup shows 1.00 tokens/forward for addition and 1.54–1.72 for edits; this is engagement evidence, not a lookup-off timing comparison.

These were worker observations, not direct shell reads by this repository session. Transport then disconnected with no benchmark or setting change in flight; current service state is unverified. The harness is partial, with an unresolved Arabic fixture encoding defect; 23 synthetic harness tests do not make it ready. Upstream research documentation may describe features newer than installed 2.0.0.

## 6. Sequence work without disrupting the user

The worker says a duplicate model instance exceeds GPU capacity. That blocks simultaneous A/B servers; it does not rule out sequential one-instance testing.

- Through the existing listener: collect sanitized inventory, completion/finish metadata and a short serial synthetic budget check when it will not queue behind user work.
- In an agreed idle window: stop only the owned stack, switch one profile, test, restore; never load both arms simultaneously.
- Keep model upgrades and the coding-specialist comparison separate from cache tuning.
- Publish a gain only with equivalent completeness/correctness, not token reduction alone.

The requested worker packet is [PC_TEST_REQUEST.md](PC_TEST_REQUEST.md). Coordination and Claude review continue in [co-chat.md](co-chat.md).

Latest coordinator update: the connection recovered and shell/WebUI health checks succeeded. Offline harness fixes are in progress, with no new inference or restart. This does not make the partial harness ready or produce a cache comparison.

Final worker checkpoint for this round: the offline planner/validator package is prepared and has 27 passing tests plus reported ZIP/credential checks. That supersedes the earlier fixture-defect checkpoint, but it is not an operational benchmark runner: it has no model launcher, telemetry collector, checkpoint writer or semantic runner. No cache A/B batch ran. See I001 for the reported archive checksum.

## Round 3 update: avoid redundant tuning

Claude's read-only laptop review confirms the optional UI generation flags are False in the environment file and ENABLE_PERSISTENT_CONFIG=False. Do not assume this is an available performance win; only runtime verification remains. The installed binary's multi-slot strings are conditional evidence, not tested multi-slot behavior.

The independent 27-test planner review also identifies 30/60 measured rows with correctness unverified. [ROUND3_REVIEW.md](ROUND3_REVIEW.md) narrows the claims, records derived memory headroom candidates and defines the next verification/review steps. The PC worker remains sole runtime owner; Claude's pause acknowledgement has now been observed, while overall stack/user activity still needs worker coordination.
