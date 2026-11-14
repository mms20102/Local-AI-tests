# Primary source register

Checked 2026-11-14. Upstream Colibri snapshot: 0a5504a1dc64f86fcd0fe7db298b0448c730e7e6.
Upstream capabilities are not proof that the installed laptop binary supports them.

| Source | What it supports | Limitation |
|---|---|---|
| [Colibri README](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/README.md) | Weight placement across disk/RAM/GPU and compatible API; catalog and measured examples | Other machines' measurements are not laptop predictions |
| [Settings](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/SETTINGS.md) | --cap is expert-cache capacity; --ctx, --ram and policy are distinct | Confirm installed-version meaning and effective values |
| [Tuning](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/tuning.md) | History-based expert placement, interleaved/reverse-order tests and resource policy | Placement history can overfit; some optional knobs change semantics |
| [Speculative decoding](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/speculative.md) | Prompt-lookup/target verification and engine/backend restrictions | qwen36 lookup is disabled for partially resident CUDA expert tiers, cache-aware routing and some formats; floating-point placement can affect output |
| [API](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/api.md) | Prefix reuse, queue/cancellation, tools and gateway metrics | Internal first-output metrics can include reasoning/tool output and exclude queue/render time |
| [Qwen family guide](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/qwen36.md) | Qwen3-Coder support, formats, template and context-architecture differences | Does not establish installed model identity or local speed |

## Papers and other primary research leads

- [Fast Inference from Transformers via Speculative Decoding — Leviathan et al., ICML 2023](https://proceedings.mlr.press/v202/leviathan23a.html): verified speculative generation as an inference technique. A paper is not proof of support in the installed runtime or speedup under this machine's memory constraints.
- [CraftGPT — creator repository](https://github.com/sammyuri/craftgpt): prior project research discussed a computer/neural computation implemented within Minecraft. Simulation on the same host is not extra physical compute and no Minecraft acceleration was implemented here.
- [Qwen3-Coder official model card](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct): primary model identity/capabilities/license reference; review the card before installing.

Quantum-computing ideas were requested previously. No verified quantum technique, quantum hardware path or local quantum-simulation speedup for this workbench has been demonstrated. Do not advertise one or silently substitute theory for a benchmark. New research must name a paper, hardware assumptions and an applicable measured implementation.

## Historical result provenance

The latency numbers in EXPERIMENTS.md come from the prior user-visible conversation, not these upstream sources. The previous PC raw logs were not accessible in this session. Repository inspection proves file/branch state only.

## Round 2 additions and source conflict

- [Open WebUI task models](https://docs.openwebui.com/features/administration/task-models/): official controls for optional UI inference chores. Check installed settings before testing them.
- [Open WebUI prompt caching](https://docs.openwebui.com/getting-started/essentials/#prompt-caching-kv-cache): stable-prefix considerations.
- [Colibri ENVIRONMENT](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/ENVIRONMENT.md): USAGE_SAVE disables writes, not history reads; COLI_PARK and version-specific controls.
- [Colibri Vulkan](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/vulkan.md) and [qwen36 chain source](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/c/qwen36_chain.h) describe multiplexed qwen36 dense-chain support. api.md's broad multi-slot limitation is not a safe universal rule. This discrepancy is recorded for Claude review; actual installed 2.0.0 behavior must be checked.

Worker reports I001/R001 are coordinator-relayed observations. Their raw artifacts are not present here; do not cite upstream source as the provenance of laptop measurements.
