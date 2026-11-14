# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval ("Yes, publish them").
These five files are a byte-identical copy of the laptop project's files at its local commit
`2ff63dc` (revision 2). Revision 1, the snapshot first reviewed, was local commit `28a1974` and is
preserved in this repository at commit `a72c796`. The laptop copy is the working one; this folder is for reading and review.

| File | SHA-256 |
|---|---|
| `teach_store.py` | `2fd2a5dffe6640b833b46dbb16a90cc2d60955d2482f8d968df8a0bb49bd7f83` |
| `teach_hook.py` | `52d4624dfe79103f2b3bcb3e250276c2d779edcf615d9bc2335877cd03022812` |
| `tests/test_teach_store.py` | `a161026933563d6f0184d06cf49979c53202b0b700be2c0841f9e04c5a9d34dd` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` |
| `TEACH.md` | `6c58591e58b738cc060b503f8d2fbd9a6383f9274b7d678ef6b69c8cc24a184b` |

**Revision 2 changes** (persistence only, after the independent static review): the live file is
no longer renamed away during a save; temporary files have unique names; writers take a lock and
re-read under it; a missing or damaged live file is refused when a backup or audit log exists; a
`recover` command restores the backup without reusing ids. `teach_hook.py` and `Teach.cmd` are
unchanged.

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has not been created. Nothing here contains
keys, chats or personal data.

**Running the tests:** they import `chat_contract.py` and read `settings.json` from the laptop
project, which are not in this repository, so they run on the laptop only (36 tests pass there;
the project suite is 136).

**Known open points before any trial:** notes are appended to the system message, which is a
privileged position, and the header alone does not enforce priority; the writer lock is a lock file with a 30-second stale
takeover, not an operating-system lock; the budget is in gateway admission units, not model tokens; the running
gateway has never been started with the hook.
