# Teaching the local assistant

Added 2026-11-14. **Status: switched on.** After a live trial on 2026-11-14 the gateway hook is
enabled: entries you save are added to chats from the next message, with no restart. The list is
empty until you add something.

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
  For scripts: the command ends with status 4, not 0, when the purge is not complete.
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
swapped in. If a save fails before that swap, the last saved version stays. If the swap
succeeds but the log line cannot be written, the change did happen and the command says "Saved,
with a problem". Only one edit runs at a time; a second
one waits. If `store.json` ever goes missing or is damaged while a backup or log exists, the tool
refuses to start with an empty list and tells you to run:

```
python teach_store.py recover
```

That restores the backup, which is one change behind; compare `list` with `audit.jsonl` and
re-add anything missing. If `recover` itself fails, `store.json` is not replaced, but two things
may be left behind: a higher number in `store.idmark` (harmless: a number may be skipped) and a
`store.json.damaged.*` copy of the unreadable file (it may contain note text). Run `recover` again.

Entry numbers (t001, t002, ...) are not given out twice. Each number is reserved in a small
file, `store.idmark`, before the entry is saved, and that file only ever counts upward. A number
can be skipped after a failed save but not repeated. If that file is missing or unreadable, both
`add` and `recover` refuse, because they could not be sure which numbers were already used. Then:

```
python teach_store.py reconcile-ids
```

rebuilds it from the store, the backup and the log, and warns that a number used after the newest
of those records could be given out again.

What "saved" means here: each file is written beside the old one, flushed to disk, and swapped in.
That has been tested against failed writes and interrupted commands. It has **not** been tested
against a power cut.

## Limits you will notice

- The current request budget is small (2,048 units for the whole conversation). Taught entries
  get at most 320 units of it by default, which is roughly four to eight short rules. Entries
  that do not fit are left out whole; none is cut, and a request is never pushed over the limit.
- Always-on entries are added first, then keyword matches. If you have more always-on entries
  than fit, the later ones are silently left out; `preview` shows which.
- Matching is by exact words, not meaning. "tests" does not match the keyword "test".

## How it is switched on, and how to switch it off

The hook is `teach_hook.py`. It is enabled by one line under `litellm_settings` in
`litellm.base.json`:

```
"callbacks": ["teach_hook.teach"]
```

To switch it off, remove that line and restart the chat. Your saved entries stay where they are.
Without switching it off you can also just `disable` entries: with nothing active, requests are
sent exactly as before.

What the live trial on 2026-11-14 showed, with two test notes that were removed afterwards: the
gateway calls the hook on every chat request and logs only entry numbers; a "docstring" rule and a
date-format fact changed the answers as intended, in English and for an Arabic request; an explicit
"do not include a docstring" in the message won over the saved rule; and with no active entries the
answers were as before. That is four small coding requests, not a guarantee that the model always
follows a note. Answers with notes took longer, because the request and the answer were longer.

Not tested: chats typed in the web page itself (the trial used the draft helper, which goes
through the same gateway), long conversations, and many entries at once.

## Tests

`python -B -m unittest tests.test_teach_store` — 80 tests, three of which start a second process
to check the lock, no model and no network. They include
simulated write failures, a missing or damaged store file, two editors, and four writers with two
readers at once.
