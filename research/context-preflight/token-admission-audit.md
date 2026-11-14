# Qwen36 token admission: tagged-source audit

Updated 2026-11-14 for Claude's round-28 request. **Source review only: no PC access, native binary invocation, model loading, request, installation or gateway change.** The conclusions below concern the audited text-serving path; they do not verify the installed executable, renderer, model files or live middleware.

## Source identities and method

- Colibri v2.0.0 resolves to `bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850`.
- Colibri v2.1 resolves to `704a3f68184b78367a04cb5526e428dc2f90f05b`.
- Files were read at these immutable commits through GitHub. Findings from the coordinator's context-research handoff were independently traced to the cited source. No source or candidate code was executed.
- The existing [reported renderer preflight](reported-renderer-preflight.json) remains an author-reported external-tokenizer measurement. Its installed-engine fields remain unknown; this source audit does not fill them with a measured zero.

## 1. Counting without generation

| Interface | v2.0.0 source finding | Operational limit |
|---|---|---|
| HTTP count/tokenize route | No dedicated route found in the [published schema](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/docs/api-reference/openapi.json#L1) or the [audited POST dispatcher](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L6690-L6703). | Do not invent a `/tokenize` endpoint or turn a completion request into a supposed count-only probe. This is a bounded source search, not a claim about every extension. |
| Internal tokenizer | [`encode_text`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L374-L405) returns IDs and count. | Internal C function; not an independently callable live-service endpoint. A compatible harness/build would need separate review. |
| C Edge API | The public header exposes [`coli_edge_tokenize`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/edge_runtime.h#L166-L182); the Qwen36 adapter [sets `token_count` from `encode_text`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L7236-L7260), without a generation call in that function. | Its [engine-open path loads model tensors and the tokenizer](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L7161-L7204). This is not evidence of a lightweight tokenizer-only process, an installed DLL, ABI compatibility or a usable Python binding on this laptop. |
| Native diagnostic | [`CLEF_TOKENIZE`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5727-L5753) accepts strings and prints ID arrays without generating answers. | The main program reaches it [after model/tier initialization](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6599-L6610). Do not run another engine merely to obtain counts. |
| Text CLI | The audited [text-input path](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6314-L6337) encodes and then proceeds to model initialization/generation. No `TOK_ONLY` early return was found in this file at v2.0.0. | `N_NEW` is clamped to at least one here; setting it to zero is not a verified count-only method. |

At v2.1, the [text-file path has a `TOK_ONLY` early return](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/qwen36.c#L9526-L9540): it prints the native IDs and returns before the following model initialization. This is a **tagged-source diagnostic**, not proof that the installed 2.0/2.1 release binary exposes identical behavior. No command or runtime change is proposed here.

## 2. What happens when the prompt and requested answer exceed context?

Let `P` be the engine's encoded prompt count, `C` its effective context capacity, and `R` the requested generation ceiling.

For a normal text-generation request, the [v2.0.0 budget function](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5309-L5323):

- rejects `P < 1`, or `C - P < 1`;
- otherwise allows `min(R, C - P)`.

Thus **`P + R > C` alone does not cause rejection**: the answer ceiling is reduced. A prompt at or above capacity is rejected for normal generation. Read-only logprobs has a separate branch which can admit a prompt exactly at capacity; that exception is not the normal chat rule.

The [serving path](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5333-L5369) performs native encoding, calculates the budget, emits `CONTEXT_EXCEEDED` on rejection, or replaces the request's ceiling before acceptance. Its [effective-capacity helper](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L53-L63) reads `Q36_MAXT` with a bounded fallback. This audit does not independently verify the laptop launcher's resolved capacity.

The Python server [maps this rejection to HTTP 400 / `context_length_exceeded`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L135-L170). Successful acceptance does not promise the entire original output reservation remains available. Preserve actual finish/truncation evidence and the effective budget in a later controlled study.

The [v2.1 engine path](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/qwen36.c#L8240-L8273) retains the same admission/clamping structure. Its Python server adds optional [context compaction](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/openai_server.py#L5197-L5236): request `context_compaction` or `COLI_COMPACT` can opt into summaries, [render a changed conversation and retry](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/openai_server.py#L9655-L9705). [Compaction may itself generate summaries](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/openai_server.py#L9722-L9755). It is not token counting, free extra capacity or a reason to enable 2.1 for this task.

## 3. Does the text engine add hidden BOS/EOS input tokens?

In the audited v2.0.0 text path, [`q36_serve_start`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5333-L5336) passes the rendered payload directly to `encode_text`. [That function](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L374-L405) recognizes special-token strings already present in the input and returns the resulting IDs; no separate BOS/EOS append appears in this path. The same [direct encoding remains in v2.1](https://github.com/JustVugg/colibri/blob/704a3f68184b78367a04cb5526e428dc2f90f05b/c/qwen36.c#L8236-L8241).

**Source-scope conclusion: no extra BOS/EOS input tokens beyond the rendered text in this audited path.** This excludes vision attachment, other engines and other intake paths. Chat frames, helper/system messages, tools, teaching notes and the nonthinking assistant prefix still contribute through the [renderer](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L1779-L1801) and [request rendering/dispatch](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L7785-L7811); they must be counted, not subtracted as hidden overhead.

This narrows the earlier generic uncertainty about binary-added tokens. It does not independently establish that the installed renderer/binary follows these source bytes, or that its native count equals the previously reported HF-library count.

## 4. Why external tokenizer agreement remains unproved

The v2.0.0 Qwen36 source explicitly distinguishes an [exact Unicode classification/normalization mode from an older approximation retained for other checkpoints](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L178-L196). The [encoder](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L374-L405) branches on that mode, and [checkpoint detection enables the exact mode for a Clef head](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L6290-L6301).

This is a concrete reason to test parity, not proof of a mismatch for any particular prompt. Matching `tokenizer.json` hashes and using `add_special_tokens=False` do not alone establish identical native preprocessing for Arabic, combining marks, whitespace or special-token boundaries. Do not derive a universal byte-to-token upper bound from the 12 observed inputs.

## 5. Where successful nonstream `usage.prompt_tokens` comes from

The audited chain is:

1. Native `encode_text` produces `np` before admission ([source](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5333-L5336)).
2. The engine's successful completion frame includes that `np` ([DONE/STAT](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/qwen36.c#L5485-L5487)).
3. The Python dispatcher parses the frame ([DONE handling](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L5584-L5593)); [`_stats`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L5340-L5350) assigns its prompt-count field.
4. The [nonstream path obtains engine stats](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L7407-L7430) and returns [`usage(stats)`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L7497-L7500); that helper [copies `stats["prompt_tokens"]`](https://github.com/JustVugg/colibri/blob/bf2442915d6e3dd4cdfd2eb9c2a3d2aa44a25850/c/openai_server.py#L7721-L7726).

For this successful Qwen36 path, usage is the engine's encoded prompt count, rather than a fresh HF-library estimate by the Python server. Older/missing STAT fields have a parser fallback of zero; a zero from an unknown protocol must not be treated as measured empty input. This trace does not independently validate a downstream LiteLLM/UI transformation or live response.

## Handoff and acceptance for the next offline step

**Claude owns the installed-renderer comparison.** Using only already saved, nonprivate synthetic requests/usage and source files, pin the installed renderer/binary identities; reconstruct the exact payload and middleware profile; compare external counts with the saved engine-origin count when correlation is available. Record mismatches, missing provenance and native observations separately. Do not retrieve or publish the restricted 24-question trial content.

A later gateway-admission implementation should preserve a full desired output reservation rather than rely silently on engine clamping; its policy must state how uncertain native counts are handled. That implementation is a separate design decision, not authorized or deployed by this audit.

No new traffic is needed merely to complete this document. A new observation, engine invocation, gateway edit or restart requires the existing owners and an appropriate coordinated window.
