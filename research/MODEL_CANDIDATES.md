# Model comparison plan

Goal: better coding assistance at useful laptop latency, without choosing only by parameter count or replacing the existing working model before comparison.

## Baseline

Existing local Qwen 35B, exact checkpoint and container not yet captured. Treat its model ID as unknown until inspecting model metadata. Preserve it.

## First specialist candidate

Qwen3-Coder-30B-A3B-Instruct. Upstream Colibri documents support on its qwen36 engine and an approximately 19 GB int4 group-scaled container. This is a source claim, not a local install or speed measurement. The model has all-attention layers, unlike the hybrid Qwen3.6 baseline candidate; therefore context memory and prompt cost must be measured separately.

Sources:
- [Qwen's model card](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct).
- [Pinned Colibri model guide](https://github.com/JustVugg/colibri/blob/0a5504a1dc64f86fcd0fe7db298b0448c730e7e6/docs/qwen36.md#qwen3-coder-30b-a3b).

## Before any download

- Confirm current free SSD capacity and Windows RAM headroom.
- Match installed engine, model architecture, tokenizer/template, supported container and conversion path.
- Prefer a verified compatible prepared container over downloading a full checkpoint plus conversion only if provenance and hashes can be checked.
- Check license, final download size and temporary conversion storage.
- Give the candidate a separate directory and server profile; do not overwrite the current model or change the default UI route.
- Avoid keeping both large models running unless measured memory supports it.

## Compare what matters

Use the same workload and comparable quantization. Report time to a correct patch, test success, instruction following, structured tools, useful Arabic, peak RAM/VRAM and first-answer latency. A lower active-parameter count is not its full memory requirement. A larger model that technically starts but takes minutes per turn may not meet the workbench goal.

Other candidates should enter only with an official model card, installed-runtime compatibility evidence and a reason to expect a quality/latency gain. Earlier chats mentioned additional model families; those recommendations are not carried over as validated facts.
