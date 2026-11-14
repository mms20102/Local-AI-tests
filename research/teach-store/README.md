# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval to publish these files.
The laptop copy is the working one; this folder is for reading and review.

| Revision | Laptop local commit | In this repository | Status |
|---|---|---|---|
| 1 | `28a1974` | commit `a72c796` | Examined by the independent static review. Preserved in history. |
| 2 | `e4fff00` | commit `1f8577d` | Examined. Preserved in history. |
| 3 | `fc3dc8a` | commit `8c0ee3b` | Examined. Preserved in history. |
| 4 | `dd40a6b` | commit `54cec06` | Examined. Preserved in history. |
| 5 | `f663f66` | this commit | Repairs proposed in response to the review of revision 4. **Not yet reviewed.** |

Every revision so far has had real defects found by the independent reviewer. Treat revision 5 as
unproven until that review reports otherwise.

Revision 5 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `b7e60330298112d81bfc7c0efd846096157eb9d260ce62dbb897aff642b2dbef` |
| `teach_hook.py` | `7623d430dfd37a809bc1fe1f1af5949d9c17e6939d470c0ce84dbb25dfbd3335` (unchanged since revision 2) |
| `tests/test_teach_store.py` | `f253915ebd707153326a41487f89f8cf72e95586af9d0ba8f40f8e314dd1ae6d` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged since revision 1) |
| `TEACH.md` | `092a99dd0567dc00a075de597c3bfdd6e6797de9a0efd88336fd717c2fc70dd8` |

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has never been created there. Nothing here
contains keys, chats or personal data.

## Running the tests from this folder

```
python -B -m unittest tests.test_teach_store
```

70 tests, 1 skipped when run from this folder (the check that the laptop's gateway configuration
does not list the hook needs that file, which is not published). On the laptop they run against
the real gateway rules: 70 pass, and the project suite is 170. Only the Windows lock path has been
run.

## Revision 5 changes, by finding of the review of revision 4

| Finding | Change |
|---|---|
| Recovery wrote the id mark after releasing the lock, so a concurrent add's higher mark could be overwritten with a lower one | The mark is written inside the same lock as the rest of recovery, and `write_id_mark` is monotonic everywhere: a value that is not higher than the current readable mark is ignored. |
| Recovery failure ordering: live file could be published and the mark write then fail | Order is now mark first, then set a damaged file aside, then publish the live file, all under the lock. A failure at the mark leaves everything as it was. A failure at publication leaves the live file as it was and the mark possibly higher, which can only skip a number. No path publishes the live file and then fails. |
| Durability scope | Every published file (store, backup, audit rewrite, mark) goes through one function that writes a temporary file, flushes it with `fsync`, and replaces the target. The claim is narrowed in code and documentation: tested against injected write failures and interrupted commands; **not** tested against power loss; the directory entry is not flushed. |
| Ordinary add treated a missing or unreadable mark as zero | Once a folder has held a store (live file, backup, audit log or mark file present), `add` refuses when the mark is missing or unreadable, as `recover` does. A new `reconcile-ids` command rebuilds the mark from the store, backup and audit log under the lock, never lowers a readable mark, and warns that an id used after the newest of those records could be issued again. |
| Incomplete purge returned exit code 0 | Exit code 4 when the purge is not complete. Codes are documented: 0 done, 1 refused, 3 saved but audit line failed, 4 purge not complete. |

## Guarantees, as narrowly as the evidence supports

- **Ids:** not repeated while `store.idmark` is readable. If it is lost, add and recover refuse;
  `reconcile-ids` is a manual path whose result is only as good as the remaining records. After
  a reserved-but-uncommitted id whose mark is then lost, reconcile will hand that number out; it
  was never attached to an entry.
- **Saves:** readers never see a partial file; a failed save leaves the previous version. Proven
  by fault injection at the process level only.
- **Purge:** rewrites the entry's own valid records in three files; reports, and signals by exit
  code, anything it left. Retryable, not atomic, not secure erasure.

## Limits that remain

- The policy sentence is an instruction to the model, not enforcement. How the model treats the
  data block is untested and needs a separately authorized trial.
- A user message that itself begins with the exact block marker is treated as already injected.
- `recover` restores a backup that is one change behind.
- Power-loss behaviour and the POSIX lock path are untested.
- The budget is in gateway admission units (bytes), not model tokens.
- The running gateway has never been started with the hook.
