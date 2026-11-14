# Gateway admission by real token count

Published by Claude (laptop session) on 2026-11-14 with Mohamed's approval, for review. These are
copies of files from the private laptop project. They contain setting *names* only: no keys,
logins, chats or logs.

| File | SHA-256 |
|---|---|
| `chat_contract.py` | `67607b8dc0409041367c2038d5201b079ef1219693fa1c810e3df6e2471a10b7` |
| `gateway_auth.py` | `17af7b5f25f3b956ea8ce21250b3b2dc24f87f1b0b35f2d751662bb9b8f093f1` |
| `token_count.py` | `6833251bd4d70538716cc528be26db41a7ed327b7dad1b8757ab5d83aca85a6d` |
| `tests/test_token_admission.py` | `f0af5cf76bf98774b8432395101d37b3f6f962a464fb3f0a0b616a57305f548c` |

Laptop local commits: `28753be` (the change) and `aa545f9` (tests runnable from this copy).
`changes-since-baseline.diff` is the exact diff of `chat_contract.py` and `gateway_auth.py`
against the laptop baseline commit; `token_count.py` and the test file are new.

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
- A system message that is not first is accepted and counted here, and then refused by the
  engine with its own message.
- Assistant history containing `</think>` is rendered here without the engine's special handling.
- The teach hook runs after this check. See `../teach-store/` for how notes are budgeted.

## Running the tests from this folder

```
python -m unittest discover -s tests
```

Needs nothing beyond the standard library for 15 tests. The 3 tests in `RealTokenizerTests` are
skipped unless the `tokenizers` package and the pinned tokenizer file are present, which is only
the case on the laptop.
