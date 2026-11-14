# Teach store: source snapshot for review

Published by Claude on 2026-11-14 after Mohamed's explicit approval ("Yes, publish them").
These five files are a byte-identical copy of the laptop project's files at its local commit
`28a1974`. The laptop copy is the working one; this folder is for reading and review.

| File | SHA-256 |
|---|---|
| `teach_store.py` | `be96b2843913866fa64ba3b506dbe4059b085dc3326442349c4c2ce994b0afdb` |
| `teach_hook.py` | `52d4624dfe79103f2b3bcb3e250276c2d779edcf615d9bc2335877cd03022812` |
| `tests/test_teach_store.py` | `57b1d4d13282d7996ddfc7985ccdb0856023be5f3d44e4cbfff8ca839af45d78` |
| `Teach.cmd` | `c8a401f3ca6a2b69cff1291c161643f13c5e5859e0b88828173f889f2379b3c7` |
| `TEACH.md` | `f89ed9da644592781973229295c2debb7429548ecb368f3ab86cd1fa9fe95efb` |

`teach_store.py` differs from the hash in co-chat round 12 by one change: the injected header now
reads "Owner's saved notes (the current request takes priority if they conflict):".

**Status:** the gateway hook is not enabled on the laptop and the gateway configuration is
unchanged. No taught entries exist; the store folder has not been created. Nothing here contains
keys, chats or personal data.

**Running the tests:** they import `chat_contract.py` and read `settings.json` from the laptop
project, which are not in this repository, so they run on the laptop only (25 tests pass there;
the project suite is 125).

**Known open points before any trial:** notes are appended to the system message, which is a
privileged position, and the header alone does not enforce priority; there is no lock against two
simultaneous edits; the budget is in gateway admission units, not model tokens; the running
gateway has never been started with the hook.
