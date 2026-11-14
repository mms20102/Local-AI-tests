# Current bounded worker packet

Updated 2026-11-14. This replaces the early 27-test packet; [the historical version](https://github.com/mms20102/Local-AI-tests/blob/3701d34729efb8fe7a174d2b48957709692fdfdb/research/PC_TEST_REQUEST.md) remains available. No new model request or runtime change is authorized by this packet.

## Ownership and current boundaries

**Window 2 OPEN — hold supersedes the earlier handoff:** Claude's first window closed, then he announced a separate host-pool-off 2.1 test and another workbench change. Hold runtime/gateway traffic and commands on ports 8000, 4001 and 8080 until the matching second-window closure. The first closure does not release this window. Only nonintrusive offline work that cannot interfere may continue. After closure, inspect the actual latest working tree/launcher diff, current native-engine identity and stale checksum without edits or another runtime test.

The existing PC worker owns the operational adapter and laptop runtime. Claude owns teach/CODE-Q1 source and has supplied renderer/tokenizer measurements. Codex maintains evidence/source review. Do not start a competing engine or runner.

Teach revision 6 completed independent offline persistence checks; hook stays **OFF**. No real taught store is reported present. Preserve its files, local Git history and gateway configuration.

The worker's latest explicit component checkpoint reports 109 isolated tests for collector/admission, bounded SSE/journal and stalled-socket/cancellation behavior. Later local work is in a preserved 18-file commit; exact current readiness needs a worker checkpoint. Component publication remains denied by automatic approval review; no branch was created and no retry/alternate upload is requested.

## A. Unblocked local preparation

1. Continue the **existing** adapter/lifecycle work offline with synthetic inputs and local test servers only, within current resource limits. Identify remaining pieces instead of deriving readiness from a test count.
2. Produce a concise sanitized checkpoint: exact local commit, authored tests run, lifecycle/identity/restore coverage, and whether any path can send a live request. Keep full benchmark execution disabled.
3. Preserve exact expected-identity/history and record/stop-policy contracts. A new branch, schema or cache plan is not needed.
4. Preserve rejected-publication artifacts locally. Handoffs must use an explicit source allowlist and exclude all `.git` directories, secrets, private chats/logs, environments, weights and runtime data. Do not publish the blocked components under another filename/route.

## B. Tokenizer-only preflight — coordinate with Claude

See [context-preflight](context-preflight/README.md) and its pinned 12-task input inventory. Claude completed that tokenizer-only work in rounds 22–23. Reported inputs span 118–300 tokens and fenced references including one end token span 31–137; maximum input plus 256 is 556. The normalized reported observation is included. Do not repeat those counts merely to fill a packet.

- No model weights, inference, engine restart, package installation, GPU use or live API probe.
- Identify installed renderer/flavor, tokenizer/special-token settings and their hashes. The tagged upstream schema has no documented count/tokenize endpoint; do not invent one.
- Count the actual serialized synthetic request, including fixed system/helper text, chat frames and the nonthinking generation prefix. Count fenced authored references separately.
- Report actual counts and 2048-context/256-output fit with special-token overhead explicitly included; missing/unverified values stay null.
- Do not expose hidden cases, private prompts or credentials. Stop for conflicting worker activity or insufficient lightweight-task headroom.

The static input audit does not validate token fit, and a fitting reference does not guarantee a generated response fits.

## C. Read-only evidence still needed

Capture only missing, sanitized evidence; avoid repeating the broad inventory:

- Immutable installed engine/model identity. Full weight hashing can be I/O-heavy; schedule it appropriately and preserve the working process.
- Fresh host commit/physical and GPU headroom, production-port ownership and relevant paging counters. Earlier ~0.94 GiB commit-headroom samples are not current clearance.
- Names-only environment evidence for lookup absence and pinned placement history. `USAGE_SAVE=0` prevents writes but still permits reads; fresh processes do not flush OS cache.
- Exact current implementation/stop/rollback status, with unknowns named.

Do not raise cap/context/tier or stop production ports merely to pass admission.

## D. Runtime work remains gated

Full arm execution requires pinned identity, completed owned lifecycle/restoration, fresh admission success and a coordinator-confirmed idle window. One model instance only. No interference with user traffic.

Keep the frozen schema-4 cap4/cap32 plan, lookup unset, 60 measured entries plus 10 warmups. Other comparisons need their own plan. Preserve all failures/truncations and planned/unobserved denominators; unknown token counts do not support comparable-length speed claims.

Round 24 reports an unstarted side-by-side 2.1 install and changes to worker-owned workbench.py at local commit cf4d369; its old checksum is stale. Review/reconcile that additive selector and current checksum privately before relying on the earlier manifest; do not start 2.1 here. Claude has since reported a first start and restoration; the local diff/identity/test claims still need independent read-only inspection. A version comparison needs a separate frozen identity/plan.

No generated code execution, teach activation, UI-control bypass, live purge/recovery or rejected-publication retry is part of this packet. Return sanitized status/evidence through the coordinator, preserving local work.
