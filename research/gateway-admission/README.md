# Gateway admission by real token count

Published by Claude (laptop session) on 2026-11-14 with Mohamed's approval, for review. These are
copies of files from the private laptop project. They contain setting *names* only: no keys,
logins, chats or logs.

| File | SHA-256 |
|---|---|
| `chat_contract.py` | `3f16bbe67b75fdee318cbda7e7803b0fb5c5407e495f108b8573712b56e740a8` |
| `gateway_auth.py` | `a4046a9949ff0758e58aab35a9103ec4a1f237b5a98ffd1ba43adef4917d5db7` |
| `token_count.py` | `a68b24734564a3f4664638406a5b50a7b81e55abc523a37573dc005c791b42a6` |
| `tests/test_token_admission.py` | `31827f40883e1c906745160aef08776d28b06874fc390a8894994aade87e4760` |

Laptop local commits: `28753be` (the change) and `aa545f9` (tests runnable from this copy).
`changes-since-baseline.diff` is the exact diff of `chat_contract.py` and `gateway_auth.py`
against the laptop baseline commit; `token_count.py` and the test file are new.

## Revision after the independent review (laptop commit `d8d25e2`, NOT loaded)

The review of commit `6c12983` (15 passed, 3 skipped) raised four findings. This folder now holds
the revised files; the version loaded on the laptop is still the one at `6c12983`.

1. **Served profile bound.** `token_count.PROFILE` names the one profile the render and counts
   were checked against: engine 2.0.0, the SHA-256 of the installed `openai_server.py` that holds
   the renderer, thinking off, context 2048, and the tokenizer hash. The launcher reports what it
   actually starts, read from its real command line and files (`served_profile`), and the gateway
   uses real counting only if that report equals the profile field by field and its own context
   setting agrees (`load_bound_counter`). Otherwise the byte rule applies, and the start-up log
   line gives a fixed reason word. The 2.1.0 launcher therefore gets the byte rule.
   Two small edits outside these files carry the report: the launcher sets one environment
   variable from `served_profile(...)` and the service starter passes it to the gateway process.
2. **Unsupported shapes refused before either route:** a system message that is not first, and
   assistant history containing `</think>`.
3. **Final enriched request validated:** see `../teach-store/` revision 16.
4. **Boundaries exercised with the real tokenizer** (laptop only): prompts found by search to be
   exactly one below, at, and one above the largest admissible count, for 256 and 64 output
   tokens, and an Arabic conversation with history on each side of the limit.

Follow-up (laptop commit `83a6f58`, not loaded), from the preliminary review at `79dd21f`: the
content-type check now runs before the reasoning-tag check, so null, numeric or boolean content
is a controlled refusal on both routes and the counter is not called.

Not addressed: the 32-token allowance is still a judgment, not a bound.

## Status

- **Loaded on the laptop** since runtime window 7 (see co-chat). The gateway log line
  `[admission] real token counting` was recorded at start.
- **Not independently reviewed.**
- Live evidence, counts only: [24 saved rows](../context-preflight/usage-parity-2026-11-14.json) and
  [six window 7 requests](../context-preflight/window7-usage-parity-2026-11-14.json), all with
  difference 0 between this counter and the engine's reported prompt tokens.

## What it does

`validate_chat(body, settings, count_tokens=None)`:

1. All earlier checks are unchanged.
2. The byte rule runs first. A request it admits is admitted exactly as before and the counter is
   not called.
3. Only a request the byte rule would refuse is counted: the messages are rendered the way the
   installed Colibri 2.0.0 renderer does with thinking off (`token_count.render`) and counted with
   the model's `tokenizer.json`, pinned by SHA-256. It is admitted when
   prompt tokens + requested output + 32 fit the context; otherwise HTTP 413.
4. If the tokenizer file or library is missing, the hash differs, the counter raises, or it
   returns anything but a positive integer, the byte rule decides. A fault can only make
   admission stricter.

## Known limits

- The 32-token allowance is not derived from a bound. It covers request shapes whose render is
  read from source and confirmed only on a few requests (two Arabic, two with history).
- The counter is loaded once when the gateway starts. A tokenizer file replaced afterwards is
  not noticed until restart; the hash pin is checked at load only.
- Added after publication (laptop commit `7dd479f`, **not loaded**): a system message that is not
  first is refused here with a clear message. The version loaded on the laptop still accepts and
  counts it, and the engine then refuses it.
- Assistant history containing `</think>` is rendered here without the engine's special handling.
- The teach hook runs after this check. See `../teach-store/` for how notes are budgeted.

## Running the tests from this folder

```
python -m unittest discover -s tests
```

Needs nothing beyond the standard library for 22 tests. The 6 tests that need the real tokenizer are
skipped unless the `tokenizers` package and the pinned tokenizer file are present, which is only
the case on the laptop.
