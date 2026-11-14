# Workbench architecture

Reported working path:

Browser → Open WebUI (loopback :8080) → LiteLLM gateway → Colibri API → Qwen model

Do not infer local gateway ports, model IDs or authentication settings from upstream examples. Inspect the actual local configuration privately.

## Responsibilities

- Open WebUI: interactive chat UI and chat storage.
- LiteLLM: common routing/authentication/configuration boundary.
- Colibri: local inference, expert placement and compatible HTTP interface.
- Draft helper: sends a request and saves code/text for human review; it does not execute generated code.
- This repository: sanitized evidence, decisions, coordination and reproducible test design.

## Three different caches

1. Expert placement/cache: which weights are resident in GPU/RAM versus backing storage. The reported 32 setting belongs here only if the actual launcher confirms it.
2. Conversation/prefix/KV state: avoids recomputing repeated prompt prefixes; a separate context/memory budget.
3. Prompt-lookup speculative drafting: proposes repeated token sequences and verifies them with the target; performance depends on workload and supported backend.

None is training on the user's conversations. More slots or larger caps do not automatically improve total latency under a tight memory budget.

## Local and cloud boundaries

The laptop runs inference. A GitHub Codespace can edit repository files and run suitable CPU tests, but its 127.0.0.1 is not the laptop's 127.0.0.1 and it cannot benchmark the RTX laptop without an explicitly designed connection. No such connection is assumed here.

## Reversible experiments

Inventory versions → save sanitized baseline → single override → bounded paired test → correctness/memory review → adopt or rollback.

Keep secrets in the existing private local environment, preserve authentication and loopback binding, and avoid uploading local chat databases or raw prompts.
