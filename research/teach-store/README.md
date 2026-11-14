# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval to publish these files.
The laptop copy is the working one; this folder is for reading and review.

| Revision | Laptop local commit | In this repository | Status |
|---|---|---|---|
| 1 | `28a1974` | commit `a72c796` | Examined by the independent static review (first report). Preserved in history. |
| 2 | `e4fff00` | commit `1f8577d` | Examined (second report). Preserved in history. |
| 3 | `fc3dc8a` | commit `8c0ee3b` | Examined (third report). Preserved in history. |
| 4 | `dd40a6b` | this commit | Repairs proposed in response to the third report. **Not yet reviewed.** |

Revision 4 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `27827f7fafd093082577bfc704d1dca32a7ea8bd342a3c6b75b47e27672f2b90` |
| `teach_hook.py` | `7623d430dfd37a809bc1fe1f1af5949d9c17e6939d470c0ce84dbb25dfbd3335` (unchanged since revision 2) |
| `tests/test_teach_store.py` | `4e42d19cd473dfcdcfb4d9b9288cfffb3741ff61261c90d98f74eb46fed9087e` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged since revision 1) |
| `TEACH.md` | `cc68528a2b063d95e82273bc71d7a74b913655f7f9b7126d9a767264f9679583` |

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has never been created there. Nothing here
contains keys, chats or personal data.

## Running the tests from this folder

```
python -B -m unittest tests.test_teach_store
```

61 tests, 1 skipped when run from this folder (the check that the laptop's gateway configuration
does not list the hook needs that file, which is not published). On the laptop they run against
the real gateway rules: 61 pass, and the project suite is 161. Only the Windows lock path has been
run.

## Revision 4 changes, by finding of the third report

| Finding | Change |
|---|---|
| `t002` can be issued twice: committed add, failed audit line, live file lost before another save, recovery from a backup and log that never saw it | A new file, `store.idmark`, holds the highest id number ever reserved. It is written, by atomic replace, **before** the entry is saved, and does not depend on the backup or the audit log. `add` takes the next id from the larger of the store's counter and the mark. Recovery includes the mark in its high-water calculation. Consequence: a failed save burns an id; ids can be skipped but not repeated. |
| Recovery must not silently claim id safety when the evidence is missing | If `store.idmark` is missing or unreadable, `recover` refuses and changes nothing. `recover --accept-unconfirmed-ids` restores anyway and prints a warning that a new id might repeat an old one. |
| Purge: a short note can match and erase an unrelated damaged line | Purge no longer rewrites or removes any audit line that is not valid JSON on the basis of matching. All such lines are left untouched. |
| Purge: keyword-only remnants and compact id forms can be missed | Because they cannot be attributed, they are counted, not removed: the report gives the number of unreadable lines kept and how many of them contain the entry's id, text or a keyword (case-insensitive substring, so `"id":"t001"` without a space is counted). |
| Retained evidence was not byte for byte (line endings) | The audit log is processed as raw bytes with line endings kept. Only this entry's own valid records are rewritten. Every other line, valid or not, is copied unchanged, CRLF or LF, and a final line without an ending is not joined to the next record. |
| Incomplete purge must be reported, not promised | The report has `complete`. It is false whenever unreadable audit lines were kept or other files remain in the folder, and the command prints "Purge is NOT complete". `--delete-unreadable-audit-lines` (every unreadable line, related or not) and `--delete-damaged-copies` are explicit owner decisions. |

## Limits that remain

- The policy sentence is an instruction to the model, not enforcement. How the model treats the
  data block is untested and needs a separately authorized trial.
- `store.idmark` is one more file that can itself be lost; then recovery refuses by default.
- A user message that itself begins with the exact block marker is treated as already injected.
- `recover` restores a backup that is one change behind; `list` against `audit.jsonl` is a manual
  check.
- Purge is retryable, not atomic across the three files. It does not reach copies outside the
  folder and is not secure erasure. Valid audit records of *other* entries that happen to quote
  this entry's text are not touched.
- The POSIX lock path is untested.
- The budget is in gateway admission units (bytes), not model tokens.
- The running gateway has never been started with the hook.
