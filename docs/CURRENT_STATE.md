# Current state and evidence

Checkpoint: 2026-11-14.

## Directly checked in this continuation

- GitHub repository: mms20102/Local-AI-tests, private; authenticated account can push.
- Initial main had only README.md. No previous briefing upload was present.
- Claude authored research/co-chat.md on claude/cloud-environment-setup-ha4b84.
- Main was an ancestor of that Claude commit; no divergent changes were present at inspection.
- Colibri upstream documentation was reviewed. Snapshot: 0a5504a1dc64f86fcd0fe7db298b0448c730e7e6.
- Laptop shell/control is unavailable in this session. No fresh laptop benchmark has been performed.

## Prior-session reported capabilities

| Capability | Reported state | What remains to verify |
|---|---|---|
| Open WebUI + LiteLLM + Colibri | Real model response and streaming passed | Installed version inventory and live smoke test |
| Chat storage | Test chat survived restart | Backup/restore drill |
| Credentials | Local keys/admin login stored in a restricted local.env | Recheck bindings and ACLs without publishing credentials |
| Fast launcher | Used a 32-capacity expert cache | Exact flag, effective memory plan and command |
| Code drafting | Streaming helper saves output; no execution | Held-out coding evaluation |
| Tool calls | Structured requests passed later tests | Multi-step tool execution, validation and recovery |
| Model inventory | Existing Qwen 35B | Exact checkpoint, container/quantization and checksums |
| Second coding model | Researched | Download/install/test not confirmed |

## User-supplied target hardware

Windows; RTX 4070 Laptop; 24 GB DDR5 (16 + 8); 1 TB storage.
Do not confuse host RAM with VRAM. Exact VRAM and CPU are still a measurement task. Do not assume storage size implies NVMe speed or free capacity.

## Not shipped as part of this documentation

No runtime source, launchers, dependency lockfile, raw benchmark logs, credentials or model files were recovered from the inaccessible earlier workspace. The prior handoff named 11 prepared documents; these new documents consolidate the visible history rather than silently presenting themselves as those original bytes.

## Meaning of labels

- Directly checked: tool evidence available in this session.
- Reported: an earlier session said it happened; underlying artifacts not available here.
- Upstream documented: source capability; may differ from installed version.
- Proposed: a future test or change.
- Adopted: only after local reproduction, correctness review and rollback validation.
