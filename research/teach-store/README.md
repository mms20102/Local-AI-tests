# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval to publish these files.
The laptop copy is the working one; this folder is for reading and review.

| Revision | Laptop local commit | In this repository | Status |
|---|---|---|---|
| 1 | `28a1974` | commit `a72c796` | The snapshot the independent static review examined. Preserved in history. |
| 2 | `e4fff00` | code at commit `35037d6`; this README corrected one commit later | Repairs proposed in response to that review. **Not yet reviewed.** |

Revision 2 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `adceed4f3a6ef04f41aaa283764f2f943038a132c094aad4647fbd8cd747448c` |
| `teach_hook.py` | `7623d430dfd37a809bc1fe1f1af5949d9c17e6939d470c0ce84dbb25dfbd3335` |
| `tests/test_teach_store.py` | `49c966b8674eccc0ab1d0fcce7b22664c92cc5e33a3c70af300ed5ebe918e6dc` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged) |
| `TEACH.md` | `e03ddfbcfb5c53e607e5fcc1ee3f632349f27fa24e6bb9ed7c97895979350d1c` |

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has never been created there. Nothing here
contains keys, chats or personal data.

## Running the tests from this folder

```
python -B -m unittest tests.test_teach_store
```

Revision 2 runs standalone: 43 tests, 1 skipped (the check that the laptop's gateway configuration
does not list the hook, which needs that file). Without the laptop project, the tests use the same
budget numbers and the store's own restatement of the gateway's admission arithmetic. On the
laptop they run against the real gateway rules (`chat_contract.py`, `settings.json`): 43 pass, and
the project suite is 143. `litellm.base.json` is read by one test only and is not published.

## What revision 2 changes, by review finding

| Finding | Change |
|---|---|
| Live file renamed away during a save | The new version is written to a uniquely named temporary file and swapped in; the previous version is copied to the backup first. The live file is never absent. A failed save leaves the last committed version. |
| Silent empty start; ids restarting | A missing or unreadable live file is refused when a backup or audit log exists. `recover` restores the backup on request and never hands out an id the audit log has seen. |
| No lock; shared temporary name | Writers take an exclusive lock file and re-read the store under it. Temporary names include the process id and a random token. |
| Notes in the system message | Notes are now a delimited `<saved_notes>` block in front of the latest **user** message. The system message receives only `POLICY`, a fixed sentence defined in code that says the block is data and the current request takes priority. Stored text may not contain the marker. |
| Delete retains content | `delete` is documented as logical. New `purge` overwrites an entry's text and keywords in the store, the backup and the audit log. |
| Keywords not screened | Keywords pass the same key-shape check. The check is documented as a heuristic. |
| Repeated hook invocation | Applying the transformation to a request that already carries the block or the policy changes nothing. |
| Preview ignores the conversation | Preview output is labelled an illustration that does not predict remaining room or token fit. |
| Test dependencies | Listed above; tests run standalone. |

## Limits that remain

- The policy sentence is an instruction to the model, not an enforcement mechanism. Whether the
  model treats the block as data is untested.
- The lock is a lock file with a 30-second stale takeover, not an operating-system lock. A writer
  stalled longer than that could be overtaken.
- `recover` restores a backup that is one change behind.
- `purge` cannot reach copies outside the store folder, and drops audit lines that are not valid
  JSON.
- The budget is in gateway admission units (bytes), not model tokens.
- The running gateway has never been started with the hook.
