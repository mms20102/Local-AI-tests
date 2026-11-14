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
| 9 | `3dcffc9` | commit `3ac4a3e` | Independent offline pass relayed in co-chat at `dcf4c30`: 77 passed, 5 skipped; construction and output of the log line both guarded. Qualifications: malformed ids were echoed with `str()`, blocking output, stale status wording here. Preserved in history. |
| 10 | `b329e51` | commit `fd962cc` | Follow-up: the log line writes only ids and fingerprints in their canonical form and counts anything else without echoing it; this README's status wording corrected. **Independent offline pass relayed in co-chat at `30175f5`: 78 passed, 5 skipped; no blocking regression in the reviewed scope. Not loaded: the running gateway was last restarted before this revision existed.** |
| 11 | `d5b6c16` | commit `829d322` | Two findings from the integration queue at `31dd8db`: an active entry whose id the store could not have issued is now left out of selection, so the logged count and the injected entries cannot disagree; a locked store file is retried for at most about 0.1 s inside a chat request instead of 0.95 s; the wording about blocking and about unchanged requests is narrowed. Independent offline pass relayed in co-chat at `8e2c028`: 80 passed, 5 skipped. Loaded on the laptop by inference only (window 7). |
| 12 | `f939b54` | commit `eaf6016` | Notes for a long request are budgeted on the whole candidate request in real tokens (`apply_with_status`), following the contract in `context-preflight/note-budget-alignment.md` on main. The byte rule still decides every request it already served. Relevant notes left out for lack of room are counted and logged as `omitted-no-room:N`. Mohamed's policy: answer anyway and say the notes were left out. Preliminary independent result relayed in co-chat at `3998f8d`: 92 passed, 5 skipped, **not cleared**: a note over the size cap was reported as omitted 0, and one malformed entry hid the valid notes beside it. Not loaded. |
| 13 | `25b519f` | commit `cb98726` | Fixes for both findings: omissions are counted against every applicable note, by reason (`omitted-note-cap`, `omitted-no-room`); a malformed active entry is skipped on its own and counted (`skipped-invalid`), and the valid notes are still applied. Independent result relayed in co-chat at `f5d7aec`: 97 passed, 5 skipped; two defects remained (diagnostics from a second read could describe a different store version; lone-surrogate text suppressed valid neighbours). Not loaded. The omission is still reported in the gateway log only. |
| 14 | `8228816` | commit `fce4615` | Fixes for both: entries, fingerprint and the invalid count come from the same single read, with no second read; an entry whose text, keywords or date cannot be encoded as strict UTF-8 is skipped on its own and counted, its stored text untouched. Independent offline pass relayed in co-chat at `44c016f`: 100 passed, 5 skipped, no blocking regression in the two repairs. Not loaded. The omission is still reported in the gateway log only. |
| 15 | `7dd479f` | commit `87351de` | A left-out note is reported as `omitted-no-room` only when the room was measured; when a token count could not be made (no counter, or it failed) it is reported as `omitted-uncounted`. **Not independently reviewed, and not loaded.** |
| 16 | `d8d25e2` | commit `b111a64` | From the gateway review at `f32776b`: whenever a token counter exists, the complete request that will be sent after notes are added is counted, also on the short path; if it does not fit, the notes are withdrawn and the request is sent without them. The hook uses the same served-profile binding as the gateway. Preliminary independent result relayed in co-chat at `79dd21f`: 104 passed, 5 skipped; one defect: notes kept after a failed final count were not labelled. Not loaded. |
| 17 | `83a6f58` | commit `631b1ec` | Notes added on the byte rule alone, with no successful token count of the final request (no counter, or the final count failed), are counted as `byte_only` and logged as `kept-byte-rule-only:N`. Zero means every added note is covered by a successful count of exactly the request sent. **Not independently reviewed, and not loaded.** |
| 18 | `9514353` | this commit | When a token counter is configured and the count of the final request cannot be made, the notes are withdrawn and the base request is sent, reported as `omitted-uncounted`. `kept-byte-rule-only` now appears only when no counter is configured at all, where the whole gateway is on the byte rule. **Not independently reviewed, and not loaded.** |

Revisions 1 to 4 each had real defects found by the independent reviewer. The review of revision 5
is a scoped source review, not a proof of all persistence properties and not integration clearance.

Revision 18 files, byte-identical to the laptop's:

| File | SHA-256 |
|---|---|
| `teach_store.py` | `d960c9d0139f607ce133fd6e0f51a02d2ea9227f69d0e42f2f56543dde797218` |
| `teach_hook.py` | `13eca6777be17664ed5c0bedb3d1edef227faf32c8ee82c2167842cc5d5ea0ea` (unchanged since revision 17) |
| `tests/test_teach_store.py` | `621170e67356c00f302d318eb81bb76ef94465604aa08bc79a134c3cadd7cb0a` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` (unchanged since revision 1) |
| `TEACH.md` | `5b6546b9a453ff97f1dfe0545fa1634afda3cf1df30a4ea29d106451dbbda610` (unchanged since revision 11) |

The token counter itself (`token_count.py`) belongs to the gateway and is published in `../gateway-admission/`; the tests here use a stand-in counter.

## Status: keep these apart

**1. Source that has been independently reviewed offline**

| Source | Independent result |
|---|---|
| Persistence code in `teach_store.py` (save, lock, recover, purge), revision 6 | Offline pass on Linux: 72 passed, 1 skipped; no new blocking issue in the reviewed scope. Unchanged since, apart from the read-only `snapshot()` added in revision 8. |
| Hook, revision 8 | Offline pass: 76 passed, 4 skipped, with three qualifications. |
| Hook, revision 9 | Offline pass: 77 passed, 5 skipped, with the qualifications listed in the revision table. |
| Hook, revision 10 (commit `fd962cc`) | Offline pass: 78 passed, 5 skipped; canary, malformed-id, malformed-fingerprint and logging checks passed. The id check restricts what can be written; it does not prove an id was really issued by the store. |
| Hook and store read path, revision 11 (commit `829d322`) | Offline pass: 80 passed, 5 skipped. Limits noted by the reviewer: 100 ms is programmed sleep, not a wall-time bound; id shape is not provenance. |
| Token-budgeted notes, revision 12 (commit `eaf6016`) | Preliminary: 92 passed, 5 skipped; **not cleared**, two defects found. |
| Revision 13 (commit `cb98726`) | 97 passed, 5 skipped; two defects found, addressed in revision 14. |
| Revision 14 (commit `fce4615`) | Offline pass: 100 passed, 5 skipped. Still open per the reviewer: counter identity and margin, user-visible notice, loaded revision. |
| Revision 15 (commit `87351de`) | **Not reviewed.** |
| Revision 16 (commit `b111a64`) | Preliminary: 104 passed, 5 skipped; one defect found, addressed in revision 17. |
| Revision 17 (commit `631b1ec`) | Not reviewed as a whole; the reviewer's clarification at `d715ee7` asked for the change made in revision 18. |
| Revision 18 (this folder) | **Not reviewed.** |

These are results on the published source. None of them is a test of the running gateway.

**2. What Claude reports about the laptop** (Claude's own observations; not verified by anyone else)

- The gateway configuration lists the callback, so the hook is enabled.
- The gateway was last restarted on 2026-11-14 at about 18:30 local. The hook file on disk at that moment was revision 9, and the gateway imports the file when it starts, so Claude infers that revision 9 is loaded.
- The one hook line in the gateway log after that restart has the form introduced in revision 8. That is consistent with revision 8 or 9 and **cannot tell them apart**.
- The store had no active entries at that time.

**3. What is not verified by anyone**

- The exact hook revision loaded in the running process. A store fingerprint identifies the store file, not the callback code.
- That a request with no active notes is byte-for-byte the same on the wire as a request with the hook off.
- That the model treats saved notes as background. The evidence is four small requests in the live trial.
- Revision 10 in any running process: it has not been loaded.

Nothing here contains keys, chats or personal data.

## The log line and its fingerprint (as of revision 10)

For each chat request the hook writes one line to the gateway log:

- `[teach] added N entries: t001,t004 | store <fingerprint>`
- `[teach] nothing added | store <fingerprint>`
- `[teach] added N entries: ... | invalid:M | store <fingerprint>` when M values were not valid ids

Only values in a known form are written. An entry id is written only if it is exactly the form the
store issues, the letter t followed by three to nine ASCII digits. Anything else is counted under
`invalid:` and its text is never written. The fingerprint is written only if it is 12 lowercase hex
digits or one of the fixed words `none` (no store file), `unknown` (the store could not be read;
the request was left unchanged) or `not-read` (the request was not an eligible plain-text chat);
otherwise the word `invalid` is written. A valid fingerprint is the first 12 hex digits of the
SHA-256 of the `store.json` bytes that the injected entries were parsed from, taken in the same
single read. It identifies a version of the store file. It does not identify the hook's code.

Building the line and writing it are inside one guard, so an odd value or a closed or broken log
pipe cannot raise into the request. This is tested for the cases in the test file, not proven for
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

109 tests, 5 skipped when run from this folder (the check that the laptop's gateway configuration
does not list the hook needs that file, which is not published). On the laptop they run against
the real gateway rules: 109 pass, and the project suite is 237 (it now includes 18 gateway admission tests that are not part of this folder). Three tests start a second Python
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
  data block has been observed on four small requests only.
- A user message that itself begins with the exact block marker is treated as already injected.
- `recover` restores a backup that is one change behind.
- Power-loss behaviour is untested. Process death is tested only for the lock holder being
  killed (Windows by Claude, Linux by the independent reviewer).
- The budget is in gateway admission units (bytes), not model tokens.
- Live evidence is limited to the trial in co-chat ("Runtime window 5 CLOSED") and one request after the restart in window 6. See the status section above for what that does and does not show.
