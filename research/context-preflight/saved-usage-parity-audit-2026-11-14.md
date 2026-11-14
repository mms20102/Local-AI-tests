# Saved-usage parity audit — 2026-11-14

**Result: zero observed net count delta in all 24 sanitized recorded pairs.** This is an independent consistency check of Claude's published count artifact, not a rerun of tokenization or a trace of the live gateway.

The [original sanitized artifact](https://github.com/mms20102/Local-AI-tests/blob/f4215ea11ffdf23542bf7c0a2a1321ed6bfb0500/research/context-preflight/usage-parity-2026-11-14.json) is pinned at `f4215ea11ffdf23542bf7c0a2a1321ed6bfb0500`, Git blob `4258215bf0fdbff595633bb2c83856a921379eb0`. Claude's round-29 explanation is preserved in the [same pinned co-chat](https://github.com/mms20102/Local-AI-tests/blob/f4215ea11ffdf23542bf7c0a2a1321ed6bfb0500/research/co-chat.md). This audit leaves both unchanged. [Machine-readable record](saved-usage-parity-audit-2026-11-14.json).

## Recomputed from the artifact

| Check | Result |
|---|---|
| Rows | 24 unique contiguous row IDs |
| Saved prompt count minus external count | 0 in 24/24 rows; stored difference fields agree |
| Prompt-count range | 68–261 |
| Prompt-count sum | 3,333 |
| Length-ended responses | 9; each reports 256 completion tokens |
| Other finish reasons | 15 `stop`; each completion count is below 256 |
| User non-ASCII bytes | 16 across three rows, as recorded |

Claude reports one system plus one user message, no history or active teaching notes, thinking off, nonstream requests, temperature zero, a 256-token output request, Colibri 2.0.0, and external `tokenizers` counts with `add_special_tokens=False`. The artifact's tokenizer hash matches the earlier reported preflight hash. Those profile/identity statements were not independently observed on the laptop.

## Two metadata issues remain

1. **System-text size:** the JSON records **168 UTF-8 bytes**; round 29 says **182**. The count comparisons are arithmetically consistent, but exact request reconstruction is not independently established. Claude should reconcile the metadata without publishing any request text.
2. **Ratio label:** the summary calls 3.54 a whole-request bytes/token ratio. Using the JSON's system size, `(24 × 168 + 7,764 user-text bytes) / 3,333 prompt tokens = 3.5391539…`, which rounds to 3.54. The artifact contains no rendered-frame byte total. Therefore that value is consistent with **system-plus-user text payload bytes**, not independently established whole rendered request bytes. It is not a token-admission bound. Using the narrative's 182 instead gives approximately 3.64 even before frames.

Neither issue changes the recorded 24 zero differences, but both limit stronger reconstruction claims.

## Scope of the conclusion

The saved usage totals agree with the reported external totals for this **near-ASCII, two-message, Colibri 2.0 dataset**. This is consistent with the [tagged-source text-path findings](token-admission-audit.md).

The saved responses, tokenizer run, exact installed executable/renderer, request-to-row linkage and gateway propagation/estimation path were not independently inspected. We therefore do **not** convert this observation into a measured count of separately added BOS/EOS, prove absence of callback injection, token-ID identity, byte-for-byte wire equivalence or universal native/HF parity. Equal totals can establish net count agreement without identifying each component's contribution.

All nine length-ended rows reporting 256 is a recorded completion ceiling observation. It does not locate where that ceiling was imposed, diagnose those answers' quality, or establish context pressure as the cause. No Arabic, unusual-whitespace, combining-mark, history, tool, active-note or 2.1 profile is validated.

The historical CODE-Q1 preflight covers different prompts/profile. Its unknown native-count/extra-token/full-engine-fit fields remain unchanged. A separate record holds the observed **net** zero here.

## Ownership and actions

Claude retains any separately authorized gateway design/implementation. Its next accepted teach count/latency/documentation follow-ups are offline and Claude-owned; this audit requests no restart or runtime change. The controlled runner remains PC-worker-owned.

This session read only sanitized counts and documentation, performed JSON arithmetic checks, and published this record. No PC access, model traffic, package/model installation, real-store edit, gateway change or generated-code execution occurred. Restricted questions and answers remain local and were neither retrieved nor published.
