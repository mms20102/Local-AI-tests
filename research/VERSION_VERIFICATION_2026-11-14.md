# Version and advisory verification — 2026-11-14

This is a primary-source check of Claude's rounds 23–24, not an installation instruction or a laptop inspection. This session installed/updated nothing and sent no model request.

## Verified upstream release metadata

| Project | Official latest stable release reported by GitHub API at this check | Published UTC | Primary source |
|---|---|---|---|
| Colibri | v2.1.0 | 2026-10-31 12:50:50 | [release](https://github.com/JustVugg/colibri/releases/tag/v2.1.0) |
| Open WebUI | v0.13.3 | 2026-11-08 23:48:24 | [release](https://github.com/open-webui/open-webui/releases/tag/v0.13.3) |
| LiteLLM | v1.109.1 | 2026-11-12 02:07:01 | [release](https://github.com/BerriAI/litellm/releases/tag/v1.109.1) |

These are dated upstream observations; they do not verify the installed packages or recommend replacing them.

The official Colibri release API lists the Windows Vulkan asset as **17,540,387 bytes**, SHA-256 **195ee0be129d563789f1ade2383e023bde5519230d6fb508516e63767ee85465**. Both match Claude's round-24 report. This verifies published metadata agreement, not the actual local archive, extraction, running binary or behavior. No performance expectation follows from a release number.

## Security scope checked against the maintainer advisory

[GHSA-2rwg-2wh4-7c4f](https://github.com/BerriAI/litellm/security/advisories/GHSA-2rwg-2wh4-7c4f) is High, published November 12. It lists 1.108.6 and 1.109.1 among patched releases. Its stated prerequisite is an Azure OpenAI/Azure AI deployment without the named Azure API-key environment variables. Claude reports no Azure deployment; that configuration was not independently inspected here. This is not a finding of exposure or a general clean-environment guarantee.

No dependency update, credential action or live reconfiguration follows from this document.

## Local change requiring runtime-owner reconciliation

Claude round 24 reports:
- 2.1.0 extracted beside 2.0.0, with the old runtime preserved; 2.1 not started.
- An optional version selector added to worker-owned `workbench.py` and a new 2.1 launcher at local commit `cf4d369`.
- The old checksum for `workbench.py` is now stale; 173 authored tests reportedly passed.

These are **author reports**, not independent verification. The PC worker has been asked to inspect the actual tree/diff before editing, verify current production/baseline identities and launcher behavior, reconcile the checksum and rerun relevant offline tests. Do not overwrite or revert concurrent work to make an older manifest match. Preserve both runtimes and existing commits; do not start 2.1 under this handoff.

A 2.0-versus-2.1 study changes engine defaults and needs separate pinned identities/plan and fresh admission/maintenance clearance. It is distinct from the frozen cap4/cap32 study.

## Claims left unverified

Python build “latest”, NVIDIA's current version and the model repository's current immutable revision were not independently established by this check. The model API could not be retrieved. An upstream modification date predating a local download does not by itself prove the installed checkpoint matches current main; compare immutable revisions/files instead.

Installed renderer/tokenizer hashes in the [preflight observation](context-preflight/reported-renderer-preflight.json) are Claude's measured report; binary-added tokens remain null.

Hook stays **off**. No runtime start/update, model request, real-store action or retry of rejected component publication was performed.

## Subsequent runtime report

After round 24, Claude opened and explicitly closed a first-start window. He reports 2.1 started and answered two small synthetic drafts, then was stopped because of high memory pressure; 2.0 was restored and one draft completed. The earlier “unstarted” statement is historical. The [reported observation](experiments/2026-11-14-colibri-2.1-first-start-reported.json) keeps single samples and incomparable timings separate from verification. Only read-only launcher/identity/checksum inspection has resumed; no new runtime test or update is requested.

A subsequent second-window notice supersedes the first closure for coordination: a host-pool-off test and another launcher change are reported intent, with outcome pending. No current runtime identity is inferred from the first restoration. Hold competing runtime/gateway activity until the matching window-2 closure.
