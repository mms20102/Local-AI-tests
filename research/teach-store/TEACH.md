# Teaching the local assistant

Added 2026-11-14. **Status: the store and command line work; the gateway hook is written and
tested offline but is switched off.** Until it is switched on, taught entries are saved and can
be previewed, but they are not yet added to chats.

## What it is

A small list of rules, facts and corrections that you write and approve. For each chat request,
the entries that apply are added to the system message, so the model sees them every time. This
is memory, not retraining: the model's weights do not change, and nothing is learned
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
```

- An entry without `--when` applies to every chat. With `--when`, it applies only when the
  message contains one of the keywords (case and Arabic diacritics are ignored).
- `preview` shows exactly what would be added for a message. It sends nothing.
- Entries are one line, at most 300 characters. Text shaped like a key or password is refused,
  because entries are stored as plain text and sent to the model.

## Where the data is

`.runtime/teach/store.json` (current entries), `store.json.bak` (the version before the last
change) and `audit.jsonl` (every add, disable, enable and delete, with time). The folder is
ignored by git. To undo everything, delete the folder.

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

`python -B -m unittest tests.test_teach_store` — 25 tests, no model and no network.
