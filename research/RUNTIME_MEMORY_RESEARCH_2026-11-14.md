# Colibri 2.0.0 Vulkan: runtime and memory research

Date: 2026-11-14. Author: Codex/ChatGPT, runtime/memory research workstream.

**Outcome:** prioritize a reproducible cap-4 versus cap-32 comparison, then lookup off/on, followed by conditional cap-48 and GPU-tier experiments. No laptop inference, restart, launcher edit, environment change, model download or generated-code execution was performed by this research workstream. All experiments below are proposals for the existing PC worker in a separately coordinated window.

## Evidence and version boundary

Read: main at `982437cf0ab604a572a1da0c38ed2527d593860e`, the complete main co-chat (blob `5940d8660288c6a3bf55dbf599951c51a33382ec`), and the Claude branch co-chat (branch head observed `5dca2bb1755dad4b845cd75d307af1c6821049ad`). Claude's newer A8/A9 contains offline planner gaps and watcher fixes; these are not fresh inference results. No existing co-chat text was edited.

Laptop observations are **reported and independently corroborated by Claude**, not rerun here: Ryzen 9 7940HS, 8 physical cores / 16 threads; 23.22 GiB usable host RAM, modules 8+16 GB DDR5-4800; RTX 4070 Laptop 8188 MiB; Windows; AC. Colibri reports 2.0.0 and the model is Kreuzzelg/qwen36-35b-a3b-colibri-i4-gs64. The fast profile has cap 32, context 2048, one KV slot, no thinking, temperature zero, a 3 GiB Vulkan expert tier, eight OpenMP threads and all 40 dense layers on the GPU. Original cap is 4. Lookup is engaged in observed logs. [Project inventory](experiments/2026-11-14-pc-inventory.json) · [Round 3 review](ROUND3_REVIEW.md).

The official annotated `v2.0.0` tag resolves to commit **`bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850`**, released October 6, 2026. This report inspected that tag's source and documentation rather than assuming the project's newer research snapshot describes the installed release. The laptop's executable hash/build commit and immutable model revision remain missing: a version string alone does not prove a byte-identical release build. [Release](https://github.com/JustVugg/colibri/releases/tag/v2.0.0) · [Tag object](https://api.github.com/repos/JustVugg/colibri/git/tags/a7f535a9b34ffa31a4eef18c8a0bb6775c973a6e).

## Source findings that change practical decisions

1. **Keep one KV slot.** In 2.0.0's qwen36 source, the branch at lines 6351 onward explicitly disables an active Vulkan dense chain when the slot count exceeds one; a separate message records that drafting is unavailable with multiple slots. This corroborates the installed binary strings and explains the newer-documentation discrepancy. It establishes release-source behavior, not a newly exercised laptop path. Increasing slots is not a promising single-user latency experiment here. [qwen36.c](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6351).

2. **RAM and VRAM expert caches already cooperate by default.** The tagged tier source enables exclusive eviction unless `COLI_VK_TIER_EXCLUSIVE=0`; qwen36's victim selection prefers evicting a RAM copy already resident on the device. Thus “enable exclusive caching” is probably a no-op unless the resolved environment overrides it. Audit the setting and footer before proposing any change. [Tier initialization](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/vk_tier.c#L1625) · [qwen36 eviction](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L1048).

3. **Dense host copies may already be released.** The release supports `COLI_VK_DENSE_HOST` with an automatic device-only policy when conditions permit. The header states the decision and released memory. First inspect those existing sanitized lines; all 40 layers on the GPU alone does not establish whether host copies were released. If already device-only, there is no additional saving to claim. If host copies are retained, identify the reason before considering a separate override experiment. [Environment reference](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/ENVIRONMENT.md#L268) · [Implementation](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6132).

4. **Correct the blanket “RAM_GB is never read” claim.** The tagged qwen36 guide still says this, but the source at lines 2458–2482 reads `RAM_GB` in its automatic-cap branch (`cap <= 0`). Explicit positive caps bypass that branch. This does not establish every CLI mapping or the installed binary's behavior; it does establish a source/documentation conflict. Retain explicit caps in both arms and do not use `--ram` as a substitute for measuring actual allocations. [Code](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L2458) · [Conflicting guide](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/qwen36.md#L437).

5. **Eight threads already match physical cores.** qwen36 calls the shared physical-core sizing helper; an explicit `OMP_NUM_THREADS` wins. That helper sizes the team and deliberately does not enable a spin-wait policy. Do not copy a GLM/CUDA spin recipe or infer active spinning from “automatic tuning.” Increasing to all 16 logical threads has no established advantage. [qwen36 startup](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6218) · [OpenMP helper](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/omp_tune.h).

## Prioritized, falsifiable experiments

These are hypotheses, not predicted percentages. Preserve the current working profile until a result passes the project's acceptance gate.

| Order | Hypothesis and isolated comparison | Evidence to collect / what would reject it |
|---|---|---|
| 0 | Finish benchmark validity and inspect existing release/device/cache headers. | Engine identity, resolved environment names/allowed values, effective caps, dense-host policy, expert-kernel mode, exclusive-cache state and memory-placement choice. No repeated broad hardware inventory is needed. |
| 1 | Cap 32 reduces repeated cold expert work relative to cap 4. Reproduce **4 vs 32**, everything else fixed. | Client first answer text and completion time, tokens/finish reason, quality/completeness, expert RAM hits and loads, actual disk I/O and memory pressure. Reject a general gain if order reversal, complete-answer matching or held-out tasks removes it. Historical 34%/18% reports remain preliminary. |
| 2 | Lookup helps repetitive edits more than novel answers. Compare verified normal lookup with `COLI_LOOKUP=0`; retain the gate. | One repetitive edit and one non-repetitive control; accepted drafts/tokens per forward, verify cost, latency, output length and task checks. Existing 1.54–1.72 tokens/forward on edits is engagement evidence only; 1.00 on addition does not show a global failure. Reject if full-answer latency fails to improve. |
| 3 | A modest larger host cache helps after reproduction. Compare **32 vs 48**, then consider **48 vs 64** only if headroom and results justify it. | Lower CPU-side misses accompanied by lower latency, with no sustained paging or completeness regression. Larger cache can displace Windows file-cache pages, so a lower engine miss count alone is insufficient. |
| 4 | More device experts reduce CPU/disk work without sacrificing the full dense chain. Compare **3.0 vs 3.5 GiB** tier, host cap unchanged. | Confirm effective tier budget/residents, 40/40 chain, upload failures, CPU share, join wait and GPU memory peaks. The requested budget is clamped to available room. Reject if effective residency does not rise, chain placement changes, or transfers/memory pressure erase the benefit. Do not jump to 4+ GiB from one snapshot. |
| 5 | Fewer CPU threads improve overlap or sustained laptop behavior. Screen **8 vs 6**, then 4 only if useful. | Same cache/tier/workload; CPU compute time, disk wait, GPU join wait, temperatures/clocks and end-to-end completion. Fewer threads may simply slow CPU experts. Keep OpenMP wait/bind settings fixed and measure after equal thermal preparation. |
| 6 | Stable reusable prefixes or better-matched starting expert history improve normal repeated work. Test separately from the cache arms. | Multi-turn prefix reuse versus changed-prefix control; or identical-budget histories trained on separate synthetic tasks and evaluated on held-out tasks. Include load/warm-up cost. Reject gains confined to training prompts. Existing history is loaded despite `USAGE_SAVE=0`; runtime adaptation is not frozen. |

Lookup is enabled by default on supported qwen36 Vulkan paths, and the release includes an acceptance/cost gate. CUDA-tier, cache-routing and qpack restrictions are separate. Drafts can change adaptive device placement, which can affect floating-point rounding; universal byte-identical Vulkan output is not promised. Keep correctness checks even at temperature zero. [Speculation source](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/speculative.md).

The Vulkan tier overlaps device-resident experts with CPU work and caps its budget against available device memory, reserve and dense allocations. A larger tier is therefore an empirical tradeoff, not “fill all VRAM.” [Budget implementation](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/vk_tier.c#L1519).

## Exact cache arithmetic and its limits

Claude's reported container geometry is 40 layers × 256 experts, 1,769,472 bytes/expert. One extra cap slot across every layer costs **70,778,880 bytes = 67.5 MiB** in expert payload.

| Cap | Host expert payload, GiB | Extra versus cap 32, GiB | Illustrative RAM remaining from the 5.7 GiB sample |
|---|---:|---:|---:|
| 4 | 0.264 | -1.846 | Not inferred |
| 32 | 2.109 | 0 | 5.700 |
| 48 | 3.164 | 1.055 | 4.645 |
| 64 | 4.219 | 2.109 | 3.591 |
| 80 | 5.273 | 3.164 | 2.536 |

These are derived payload sizes, not total RSS/commit, reservations or guaranteed free memory. Scratch, KV, draft snapshots, other apps and reclaimed file-cache pages matter. A provisional 3 GiB host reserve would be a project screening choice, not a system safety theorem; sustained paging, faults or user traffic should stop a run earlier regardless. Cap 80 is a poor first candidate under this snapshot.

The recorded live GPU sample used 6472 of 8188 MiB: only **1.676 GiB** was unused at that moment, not reserved for future allocations. An extra 0.5 GiB could hold at most about 303 raw expert payloads before device layout, pool rounding and streaming scratch; actual startup counts decide. Do not add nominal 8 GiB GPU capacity to 23.22 GiB RAM and call the sum a unified memory budget.

The reported live log's 55,306 loads versus 51,678 RAM hits gives a **51.70% CPU-side routed-request miss fraction** for that short session. It is not the percentage of distinct experts stored on disk. Nor is an engine cache miss proof of physical NVMe I/O: Windows may serve a buffered file read from its own cache. That distinction is why host RAM, file-cache effects and actual storage activity belong together in the comparison. [Reported evidence](experiments/2026-11-14-pc-inventory.json).

## Cheap audits before adding knobs

- Confirm default packed int4 expert execution is actually active. The release supports a packed gs64 CPU expert kernel; an inherited override could select a larger unpacked representation and invalidate the payload/RSS expectations. Do not re-enable an already active default and claim a win. [qwen36 kernel reference](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/qwen36.md#L124).
- Inspect the existing Vulkan placement header for device-local versus staged uploads. Version 2.0.0 already chooses staging automatically for small host-visible device-local heaps, including cards without Resizable BAR. Forced staging or a BIOS change has no established benefit on this laptop. [Placement reference](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/ENVIRONMENT.md#L233).
- Keep optional UI tasks in the “configured off, runtime unverified” category. A disable/restore A/B is redundant if they are already off. The earlier browser verification was blocked before input and remains untested; this workstream did not retry it.
- Do not interpret plan/doctor run beside the active model as replacement-stack capacity. Existing CPU-only diagnostics contradict the live Vulkan log; compare executable paths in the maintenance window before changing anything.
- Source names are not portable knobs. The generic `DIRECT`/`PIPE` recipes are not established qwen36 2.0.0 optimizations; Windows, engine and storage paths need specific support evidence. `Q36_DN_GPU` and several `QT_*` settings describe the CUDA tier, not this Vulkan configuration.

## Protocol and remaining blockers

Use [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md) and the existing PC owner. The saved five-pair/six-task plan is exploratory; do not silently enlarge or replace it. One model instance, sequential AB/BA arms, equal initial history and comparable request sequences. Fresh processes do not flush Windows file cache, and a new UI chat does not guarantee cold-prefix work. Report warm and cold claims separately.

Record actual generated tokens, first visible answer text, finish reason, all errors/truncations and the full planned denominator. Analyze successful complete pairs only with exclusions visible. A 10% median paired improvement is the project's proposed screening threshold, not statistical proof; confirm with reversed order and relevant task quality. Static parsing/schema checks are not semantic correctness.

The branch's latest A8 review reports missing finish-reason representation, batch-summary/completeness fields and environment/history enforcement gaps in the reviewed planner revision. Treat those as author-reported review findings pending the worker's exact revised source. Existing test counts do not make an operational launcher/telemetry/checkpoint/semantic runner. Do not build a competing runner here.

Remaining evidence: exact engine build/hash, immutable model revision, sanitized raw benchmark records, peak/commit/paging and physical-I/O traces, and supported semantic assessments (30 of the planned 60 rows remain unverified in recorded coverage). Runtime ownership and the inference pause remain with the PC worker; this document does not release the window.

Deferred: backend/CUDA migration, additional GPUs/APU use, forced low-bit dense quantization, cache-aware rerouting, expert dropping, model downloads and RAM purchases. Some alter arithmetic/quality or memory topology and all would confound the present reproduction. The 8+16 GB module layout alone does not quantify a bandwidth penalty.

**No new speedup is established by this report.** It supplies version-grounded hypotheses and rejection criteria while preserving the working laptop configuration.
