# Teaching the local assistant

Added 2026-11-14. **Status: the store and command line work; the gateway hook is written and
tested offline but is switched off.** Until it is switched on, taught entries are saved and can
be previewed, but they are not yet added to chats.

## What it is

A small list of rules, facts and corrections that you write and approve. For each chat request,
the entries that apply are put in front of your message as a marked block of saved notes, so the
model sees them every time. They are treated as background data, not as commands: one fixed
sentence in the system message, written in the code and not taken from your notes, tells the model
that the current request takes priority. This is memory, not retraining: the model's weights do not change, and nothing is learned
automatically from chats.

## Use

Double-click **Teach.cmd**, type one line, press Enter. Or from a terminal in this folder:

```
python teach_store.py add "Always include a short test with code answers."
python teach_store.py add "This project uses Python 3.12." --kind fact --when python,version
python teach_store.py list
python teach_store.py preview "how do I parse a date in python?"
python teach_store.py disable t002
python teach_store.py delete t002
python teach_store.py purge t002
```

- `disable` hides an entry; `enable` brings it back.
- `delete` hides it for good, but its text stays in the store file, the backup and the log.
- `purge` overwrites the entry's own records in those three files and then tells you whether it
  is complete. It is **not complete** when the log contains damaged lines (it cannot tell whose
  they are, so it leaves them exactly as they are and counts them) or when the folder holds other
  files such as a damaged copy set aside by `recover`. Two explicit options finish the job:
  `--delete-unreadable-audit-lines` removes every damaged log line, related or not, and
  `--delete-damaged-copies` removes the set-aside copies. If a purge is interrupted, run it again.
  It is not secure erasure: the disk may keep old data, and copies made elsewhere are not touched.
- If a command says "Saved, with a problem", the change was saved but its log line was not. Do not
  repeat the command.

- An entry without `--when` applies to every chat. With `--when`, it applies only when the
  message contains one of the keywords (case and Arabic diacritics are ignored).
- `preview` shows which entries would be chosen for a message. It sends nothing. It is an
  illustration: a real chat with a long history may have less room, so fewer entries may be added.
- Entries are one line, at most 300 characters. Text shaped like a key or password is refused,
  because entries are stored as plain text and sent to the model. That check is a simple pattern
  match; it will not catch every secret or personal detail, so do not rely on it.

## Where the data is

`.runtime/teach/store.json` (current entries), `store.json.bak` (the version before the last
change) and `audit.jsonl` (every add, disable, enable and delete, with time). The folder is
ignored by git. To erase everything, delete the whole folder; deleting only `store.json` leaves
the backup and the log.

Saving is done so that `store.json` is never missing: the new version is written beside it and
swapped in. If a save fails, the last saved version stays. Only one edit runs at a time; a second
one waits. If `store.json` ever goes missing or is damaged while a backup or log exists, the tool
refuses to start with an empty list and tells you to run:

```
python teach_store.py recover
```

That restores the backup, which is one change behind; compare `list` with `audit.jsonl` and
re-add anything missing.

Entry numbers (t001, t002, ...) are never given out twice. Each number is reserved in a small
file, `store.idmark`, before the entry is saved, so a number can be skipped after a failed save but
not repeated. If that file is missing, `recover` refuses, because it could not be sure which
numbers were already used; `recover --accept-unconfirmed-ids` restores anyway after you have
checked.

## Limits you will notice

- The current request budget is small (2,048 units for the whole conversation). Taught entries
  get at most 320 units of it by default, which is roughly four to eight short rules. Entries
  that do not fit are left out whole; none is cut, and a request is never pushed over the limit.
- Always-on entries are added first, then keyword matches. If you have more always-on entries
  than fit, the later ones are silently left out; `preview` shows which.
- Matching is by exact words, not meaning. "tests" does not match the keyword "test".

## Switching it on (not done)

The hook is `teach_hook.py`. To enable it, the gateway configuration needs one line under
`litellm_settings` in `litellm.base.json`:

```
"callbacks": ["teach_hook.teach"]
```

and the stack must be restarted. Checked offline: the hook is a valid callback class for the
installed gateway library (1.108.5), it adds the block to a request, leaves other request
fields alone, and leaves the request unchanged if the store is missing or broken. **Not
checked:** that the running gateway calls it for chat requests and that the model follows the
notes. That needs one start of the stack and one test message, in an agreed window.

To switch it off again, remove the line and restart. The store can stay.

## Tests

`python -B -m unittest tests.test_teach_store` — 61 tests, no model and no network. They include
simulated write failures, a missing or damaged store file, two editors, and four writers with two
readers at once.
