# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval to publish these files.
The laptop copy is the working one; this folder is for reading and review.

| Revision | Laptop local commit | In this repository | Status |
|---|---|---|---|
| 1 | `28a1974` | commit `a72c796` | Examined by the independent static review (first report). Preserved in history. |
| 2 | `e4fff00` | commit `1f8577d` | Examined by the independent static review (second report). Preserved in history. |
| 3 | `fc3dc8a` | this commit | Repairs proposed in response to the second report. **Not yet reviewed.** |

Revision 3 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `d17a7b33c303d1e2e6e5590ca5c64b8658b09502b9be4237e2bad3eb277323c9` |
| `teach_hook.py` | `7623d430dfd37a809bc1fe1f1af5949d9c17e6939d470c0ce84dbb25dfbd3335` (unchanged since revision 2) |
| `tests/test_teach_store.py` | `11bda13d86d3fcc44da61af942c8adead7f7d35fc3cd0b6afc018f26ebea5650` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged since revision 1) |
| `TEACH.md` | `eb52a35a3a40212df494c9e389c4d56dd41e40cc7e55274cbfb4dc00d03df64b` |

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has never been created there. Nothing here
contains keys, chats or personal data.

## Running the tests from this folder

```
python -B -m unittest tests.test_teach_store
```

55 tests, 1 skipped when run from this folder (the check that the laptop's gateway configuration
does not list the hook needs that file, which is not published). On the laptop they run against
the real gateway rules: 55 pass, and the project suite is 155. The lock tests use the Windows
`msvcrt` lock on Windows and `fcntl.flock` elsewhere; only the Windows path has been run.

## Revision 3 changes, by finding of the second report

| Finding | Change |
|---|---|
| Recovery outside the write transaction; lower `next_id` published first | `recover` holds the folder lock for the whole operation. The restored data, with `next_id` already raised above every id in the backup and the audit log, is built in a temporary file and published in one replace. A damaged live file is copied aside before that replace and is otherwise untouched; a failed recovery changes nothing and can be repeated. An unusable backup is refused. |
| Lock ownership can be lost; `PermissionError` may spin | The lock is now an operating-system lock on an open handle to `store.lock` (`msvcrt.locking` / `fcntl.flock`). Only the holder can release it, the system releases it if the holder dies, there is no takeover by age, and the file is never deleted. Acquisition is bounded (10 s) and then fails with a clear message. |
| Purge drops unrelated audit lines; damaged copies missed; partial application | Covered artifacts are named: `audit.jsonl`, `store.json.bak`, `store.json`, in that order. The live store is changed last, so an interrupted purge still knows the text and the same command completes it; a repeat leaves one purge record. Unreadable audit lines are kept byte for byte unless they contain the entry's id or text, in which case that line is replaced by a marker; both counts are reported. Every other file in the folder is listed as not covered; `--delete-damaged-copies` removes set-aside copies. The output says it is not secure erasure. |
| Audit failure after commit is ambiguous | A distinct `AuditWriteError` ("the change is saved, but the audit log could not be written"), exit code 3, and no rollback of memory. The id counter lives in `store.json`, so ids are preserved without the log line. |
| Idempotence scanned every message | Only this transform's own injection counts: the block at the very start of the latest user message. Marker text quoted in a message, or a block in an older turn, no longer suppresses injection. The policy sentence is not appended twice to a system message that already ends with it. |
| Authority | No code change. Request shape is tested; model adherence is not, and is listed below. |

## Limits that remain

- The policy sentence is an instruction to the model, not enforcement. How the model treats the
  data block is untested and needs a separately authorized trial.
- A user message that itself begins with the exact block marker is treated as already injected.
- `recover` restores a backup that is one change behind, and after an audit failure the log may
  be missing a line; `list` against `audit.jsonl` is a manual check.
- Purge is retryable, not atomic across the three files: between steps the files can differ. It
  does not reach copies outside the folder and is not secure erasure.
- The POSIX lock path is untested.
- The budget is in gateway admission units (bytes), not model tokens.
- The running gateway has never been started with the hook.
