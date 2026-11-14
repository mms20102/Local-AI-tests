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

## Round 2 update — coordinator-relayed PC evidence

The earlier no-PC-access limitation applies to this repository session, not to the whole project. A separate PC worker is available and owns laptop interaction. See [I001](../research/experiments/2026-11-14-pc-inventory.json) for exact hardware, installed Colibri 2.0.0/Vulkan configuration and the cap-4/cap-32 comparison identity.

Claude has now posted genuine Q1–Q3 replies and Q4/Q5 questions; Codex/ChatGPT answers are appended in co-chat. The new [R001](../research/experiments/2026-11-14-output-budget.json) result is a preliminary worker report without raw artifacts, not a fresh measurement performed by this session.

PC transport disconnected and then recovered; the latest shell/WebUI health checks succeeded. Offline benchmark-harness correction is in progress. Its known Arabic fixture defect and incomplete stop tests prevent calling it ready. No complete cache experiment has run.

Latest worker update for this round: shell/WebUI health 200 verified; the offline planner/validator preparation archive is complete with 27 reported tests and ZIP/credential checks. It remains a preparation artifact, not an operational runner or an executed benchmark. See I001 for the checksum and missing pieces.

## Round 3 evidence status

Claude independently confirmed the laptop inventory in a read-only session and independently ran the 27 planner tests. It sent no inference. File-level UI flags are off, while effective call counting remains pending. Binary message strings suggest a restricted multi-slot path but do not prove its execution condition.

The planner covers only preparation and has incomplete correctness assessment (30/60 rows). [Round 3 review](../research/ROUND3_REVIEW.md) records the resulting limits and next checks. Claude's own pause acknowledgement has now been read at b6d67e2. The worker must still coordinate the whole quiet window, including user activity, before testing.

Latest worker checkpoint: UI call-count verification blocked before input; no message submitted. New offline helper/planner changes reportedly pass 91/30 tests, but worker validation is still in progress and this session has not reviewed the revised source. No new performance measurement is claimed.
