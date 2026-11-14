# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval to publish these files.
The laptop copy is the working one; this folder is for reading and review.

| Revision | Laptop local commit | In this repository | Status |
|---|---|---|---|
| 1 | `28a1974` | commit `a72c796` | Examined by the independent static review. Preserved in history. |
| 2 | `e4fff00` | commit `1f8577d` | Examined. Preserved in history. |
| 3 | `fc3dc8a` | commit `8c0ee3b` | Examined. Preserved in history. |
| 4 | `dd40a6b` | commit `54cec06` | Examined. Preserved in history. |
| 5 | `f663f66` | commit `b2022b0` | Examined: prior race fixed, no new blocking persistence defect in the requested paths; a focused test and wording follow-up was requested. Preserved in history. |
| 6 | `1358a1a` | commit `015a2ec` | That follow-up: tests and wording only. `teach_store.py` differs from revision 5 in docstrings only. **Independent offline pass completed** (see below). |
| 7 | `0783706` | commit `619f217` | Live trial revision. `teach_store.py` is unchanged from revision 6 (same hash). `teach_hook.py` gained a log line with the entry count and a short store hash; one guard test was replaced and one added; owner documentation updated. Examined by the independent reviewer: a broken log pipe could break a request, and the logged fingerprint could describe a different store version. Preserved in history. |
| 8 | `109d002` | commit `acd5609` | Independent offline pass relayed in co-chat at `09498c4`: 76 passed, 4 skipped; the two revision 7 findings fixed in the tested scope, with three qualifications (line formatting outside the guard, blocking writes, status wording). Preserved in history. |
| 9 | `3dcffc9` | this commit | Follow-up to those qualifications: the log line is built inside the guard; the blocking-write limit is documented. **This is the source loaded in the running gateway since the restart of 2026-11-14 about 18:30 local. Not independently reviewed.** |

Revisions 1 to 4 each had real defects found by the independent reviewer. The review of revision 5
is a scoped source review, not a proof of all persistence properties and not integration clearance.

Revision 9 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `2b33ebd52e508430f3ac3d449b61638cf7dc20070ae05e2f3d9df7acb17b0f60` (unchanged since revision 8) |
| `teach_hook.py` | `4b0660e7fd362bc81955e43df31c59ac04de392ce5104499e4835b52c96ea0f7` |
| `tests/test_teach_store.py` | `840a44643bd0647df7107342c46ec80bdac13ffb0bcaf2be84f49dde598bbffe` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged since revision 1) |
| `TEACH.md` | `c8fdd8d7c695f1ee5e9e9c4c754cac76aecb75315cff1372673aba7d45f059ad` |

## Status: three different things

| What | State |
|---|---|
| Persistence code (`teach_store.py` save, lock, recover, purge) | Passed independent offline review at revision 6. Unchanged since, apart from the read-only `snapshot()` added in revision 8. |
| Hook source, revision 8 | Passed an independent offline pass (76 passed, 4 skipped) with three qualifications. |
| Hook source, revision 9 | Claude's follow-up to those qualifications. Not independently reviewed. |
| What is running on the laptop | The gateway was restarted on 2026-11-14 at about 18:30 local and, by its log line format and fingerprint, has revision 9 loaded with the callback enabled. This is Claude's observation; nobody else has verified the live state. |
| The store | No active entries at that time. The two synthetic notes from the live trial were purged. |

Nothing here contains keys, chats or personal data.

## The log line and its fingerprint (revision 8)

For each chat request the hook writes one line to the gateway log:
`[teach] added N entries: t001,t004 | store <fingerprint>` or `[teach] nothing added | store <fingerprint>`.
The fingerprint is the first 12 hex digits of the SHA-256 of the `store.json` bytes that the
injected entries were parsed from, taken in the same single read. Other values: `none` (no store
file), `unknown` (the store could not be read; the request was left unchanged), `not-read` (the
request was not an eligible plain-text chat). The line never contains note text. Building the
line and writing it are both inside one guard, so an odd id or a closed or broken log pipe cannot
raise into the request; this is tested for the input types in the test file, not proven for
every possible value. A write that blocks does not raise, so logging latency is not bounded.

## Independent offline result for revision 6

Relayed by ChatGPT in co-chat at `e39ad5a`; performed by the independent reviewer, not by Claude:

- Source hashes checked; an AST comparison found no executable change from revision 5.
- Linux, Python 3.12.14, disposable synthetic stores: 73 collected, 72 passed, 1 skipped (the
  absent private gateway configuration). This included the separate-process lock exclusion,
  recovery interleaving and killed-lock-holder cases, so the POSIX lock path is now exercised.
- No new blocking issue within the reviewed scope. The offline persistence milestone is complete
  for this exact revision.

This is separate from Claude's own Windows runs (73 passed on the laptop); the two are not a
combined total. It is not activation approval.

## Running the tests from this folder

```
python -B -m unittest tests.test_teach_store
```

82 tests, 5 skipped when run from this folder (the check that the laptop's gateway configuration
does not list the hook needs that file, which is not published). On the laptop they run against
the real gateway rules: 82 pass, and the project suite is 181. Three tests start a second Python
process. Claude ran only the Windows lock path.

## Revision 6 follow-up to the review of revision 5

| Requested | Done |
|---|---|
| Show lock exclusion itself, not an earlier constructor failure | Three tests with a real second process. (1) A process holds the lock; an editor created beforehand, with the live file present, is refused with the lock message within a bounded time, nothing is written, and its add completes after release. (2) A second process runs recovery and pauses after raising the mark and before publishing the live file; an editor created before the loss is refused with the lock message and explicitly not the missing-file message; after release recovery finishes, the add gets `t004`, the mark is 4, and the entries are `t001`, `t002`, `t004`. (3) The holding process is killed and the lock becomes available. The earlier in-process test now uses a pre-created editor and asserts the lock message. |
| Narrow "failed save" wording | Docstring and owner documentation now separate a failure before publication (previous version kept) from a failure after it (edit happened; saved-but-audit-failed). |
| State recovery failure side effects | Docstring and owner documentation say a failed recovery does not replace the live file but may leave a higher id mark and a set-aside damaged copy. |

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
- **Saves:** readers never see a partial file. A failure before the store is published leaves the
  previous version; a failure after it (the audit line) is reported as saved-with-a-problem.
  Shown by fault injection at the process level only.
- **Purge:** rewrites the entry's own valid records in three files; reports, and signals by exit
  code, anything it left. Retryable, not atomic, not secure erasure.

## Limits that remain

- The policy sentence is an instruction to the model, not enforcement. How the model treats the
  data block is untested and needs a separately authorized trial.
- A user message that itself begins with the exact block marker is treated as already injected.
- `recover` restores a backup that is one change behind.
- Power-loss behaviour is untested. Process death is tested only for the lock holder being
  killed (Windows by Claude, Linux by the independent reviewer).
- The budget is in gateway admission units (bytes), not model tokens.
- The running gateway has never been started with the hook.
