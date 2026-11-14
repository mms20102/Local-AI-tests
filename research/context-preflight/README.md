# CODE-Q1 context preflight

Checkpoint: 2026-11-14. Static input audit complete; **installed-renderer/tokenizer measurements reported by Claude**. Installed native counts remain unmeasured here. The [tagged-source admission audit](token-admission-audit.md) finds no separately appended BOS/EOS in the audited Qwen36 text path, while native/external-tokenizer agreement remains unproved. No model request or candidate-code execution was performed for this preflight.

## Independent source/input checks

At [de9398a](https://github.com/mms20102/Local-AI-tests/tree/de9398a167b64c79510b470b7d60b3a0931aad04/research/coding-quality-v1), fixture revision 2 has 12 prompts and 13 reference files. Codex matched all **25 Git blob identities** to that immutable tree and confirmed those files are unchanged at the later observation commit. Manifest SHA-256 values were not independently recomputed here.

[input-audit.json](input-audit.json) preserves this static snapshot: Unicode code points, UTF-8 sizes and null token fields. The references were read as text, never imported or executed; hidden cases were excluded. Canonical reference text uses manifest file order, LF endings, final whitespace trimmed and one Python fence per file, with filename comments only for multi-file answers.

| Task | Prompt code points | Prompt UTF-8 bytes | Fenced reference UTF-8 bytes | Static token count |
|---|---:|---:|---:|---|
| A01 | 389 | 628 | 147 | pending |
| A02 | 380 | 600 | 351 | pending |
| A03 | 665 | 957 | 191 | pending |
| B01 | 774 | 774 | 199 | pending |
| B02 | 524 | 524 | 112 | pending |
| B03 | 657 | 657 | 264 | pending |
| E01 | 742 | 742 | 342 | pending |
| E02 | 1047 | 1047 | 452 | pending |
| E03 | 1129 | 1129 | 469 | pending |
| F01 | 411 | 411 | 207 | pending |
| F02 | 596 | 596 | 272 | pending |
| F03 | 608 | 608 | 450 | pending |

Bytes and code points differ for the Arabic prompts. Neither is converted into tokens.

## Reported installed-renderer preflight

Claude's [script and raw result](https://github.com/mms20102/Local-AI-tests/tree/3851799d5553da7240778763e245d834a9843638/research/coding-quality-v1) are preserved on his branch. [reported-renderer-preflight.json](reported-renderer-preflight.json) normalizes the observations with explicit provenance.

Reported identities:
- Tokenizer SHA-256: `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`; existing `tokenizers 0.23.3`.
- Installed Colibri 2.0.0 renderer SHA-256: `67817219f7e7bb649eaae4f3570e7e43e9d4f388a7de1ea4b9031ad15bd7e43d`, `render_chat_qwen`.
- Synthetic system text: “Provide concise code for review only. Never execute it.” One task/user message, thinking off, no tools, history or teach notes.
- The script reconstructs frames from the installed source description; the library uses `add_special_tokens=False`. Fenced references include one end-of-turn token.

| Task | Reported rendered input tokens | Reported reference tokens incl. EOT | Input + 256 |
|---|---:|---:|---:|
| A01 | 156 | 44 | 412 |
| A02 | 160 | 127 | 416 |
| A03 | 222 | 53 | 478 |
| B01 | 218 | 54 | 474 |
| B02 | 161 | 31 | 417 |
| B03 | 208 | 80 | 464 |
| E01 | 218 | 89 | 474 |
| E02 | 270 | 137 | 526 |
| E03 | 300 | 125 | 556 |
| F01 | 118 | 53 | 374 |
| F02 | 180 | 77 | 436 |
| F03 | 175 | 108 | 431 |

The reported ranges are **118–300 input** and **31–137 reference** tokens. Maximum rendered input plus the full output reservation is **556**, below 2048 **before any binary-added tokens**. All authored references fit 256 under this tokenizer method. That does not establish generated response length, semantic correctness or complete engine context fit.

Codex checked task ids, prompt sizes, unchanged Git identities, arithmetic and maxima against the raw report. Codex did **not** rerun tokenization, inspect the laptop renderer bytes or establish Python-library/native-tokenizer parity. The result is author-reported measurement with independently checked consistency, not an independent engine run.

## Tagged source verification

The [v2.0.0 API schema](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/api-reference/openapi.json) has no documented tokenize/count route. The [Qwen renderer](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L1779) includes message frames and a preclosed thinking block for nonthinking requests. [Flavor dispatch](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L3460) can select another renderer. This supports the serialization concern; it is not installed-binary proof.

Round 23 corrects the earlier plain-ChatML count by four tokens per request. Prefer that result over round 22.

## Remaining evidence and bounded next steps

Keep **installed measured binary-added input tokens, actual engine prompt tokens and full-engine fit null** until correlated evidence exists. Source inspection narrows the generic overhead question but does not establish installed-binary/tokenizer parity. Claude's round-28 handoff is an offline comparison using installed renderer source and already-saved synthetic usage where provenance permits. Do not send traffic solely to fill these fields or silently invent a BOS correction; do not reuse 2.0 counts for 2.1.

The observed bytes/token ratio is text-dependent. It does not prove every serialized request is conservatively admitted by a byte rule, and it does not justify dividing the live admission count by four. A later reviewed admission design should count actual serialization plus output/special-token reservation, keep units explicit, and preserve fail-closed behavior. No live budget or context setting is changed here.

A fitting authored reference is a feasibility check only. The teach hook stays **off**, generated-code execution stays disabled, and the blocked benchmark-component publication is not retried. The PC worker retains runtime ownership.
