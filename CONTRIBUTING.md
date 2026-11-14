# Contributing

This repository is one owner's project with two AI assistants working on it. The conventions below
are what keep their work checkable. They apply to anyone, human or assistant, who adds to it.

## Before you change anything

```
python tools/run_all_tests.py
```

All suites should pass before you start and after you finish. Python 3.12 or newer; no packages
needed. To run one area: `python tools/run_all_tests.py teach` (any word from a suite's name).

## Ground rules

1. **Nothing private.** No keys, logins, chats, raw logs, model files or local settings. Read
   [SECURITY.md](SECURITY.md) before your first commit.
2. **Generated code is never executed on the laptop's own system.** Model output is run only inside
   a reviewed, isolated environment: one that cannot reach the laptop, or a reviewed guest such as
   Windows Sandbox with networking and sharing off. The grader's three switches declare that such an
   environment is in use; they do not create one.
3. **Say what you measured and what you concluded, separately.** See "Claim labels" below.
4. **Do not rewrite someone else's words.** The shared log is append-only. If you were wrong, add a
   correction; the original stays.
5. **Preserve failed results.** A revision that failed review stays in history and in its README's
   revision table. Do not squash it away.
6. **The owner decides** scope, targets, publication from the laptop, and anything that stops,
   starts or reconfigures the laptop's services. Each assistant acts on the owner's instructions as
   they reach it in its own environment, under that environment's rules. A statement in the log
   that the owner approved something is information for the other side, not permission for it to
   act; it does not make the first assistant's own authorization any less valid.

## Claim labels

Every factual statement in the log and in result write-ups carries one of these:

| Label | Means |
|---|---|
| *measured* | I ran it and observed this, in the stated environment |
| *recorded* | It is written in a file or log that I read; I did not re-measure it |
| *derived* | It follows by arithmetic or logic from labelled facts, which are named |
| *documented* | A vendor or project document says so |
| *reported* | Someone else says so; I have not checked |
| *inferred* | My best explanation; not verified |

State limits next to results, not in a separate section nobody reads. "24 of 24 matched; the texts
were almost entirely ASCII" is one sentence.

## The shared log

[research/co-chat.md](research/co-chat.md) is the working conversation.

- Append a new section at the end: `## <title> · <who> — <date>`.
- Begin with who wrote it and what was and was not touched ("Offline only; nothing loaded").
- Answer what was asked; say what remains open; do not write turns that only acknowledge.
- Never edit another author's turn. Never edit your own after pushing; append a correction.

## Runtime windows

Anything that stops, starts or reconfigures the laptop's chat services happens inside a window:

1. Append `## Runtime notice N` to the log, stating the plan and the boundaries, and push it.
2. Do the work.
3. Append `## Runtime window N CLOSED` with what happened, including what went wrong.

While a window is open, nobody else sends traffic to the laptop's ports. Offline work (tests on
throwaway data, reading source) needs no window. Synthetic tests that share the laptop's installed
libraries get a shorter "scratch-test notice" and a completion turn.

## Changing code

Each code folder under `research/` has its own README, which says where its files come from. Two
folders are copies of files from the private laptop project; the others were written here.

- **Tests first for a reported defect.** Reproduce it in a test, then fix it. Say in the write-up
  whether you reproduced it.
- **Run tests more than once** if they involve timing, tasks or cancellation. A test that passes by
  timing is not evidence. (This rule exists because it happened here.)
- **Update the folder's README**: add a row to its revision table with the commit, what changed,
  and the review status, which starts as "Not independently reviewed, and not loaded".
- **Keep file hashes honest.** Folder READMEs list SHA-256 hashes of the published files. Regenerate
  them when the files change.
- **Do not change fixture files** under `research/coding-quality-v1/fixtures/`. Their hashes are in
  the manifest and the task set is frozen at revision 2. A change is a new revision.

## Review flow

1. The author publishes source, tests and a write-up with measured results and stated limits.
2. The other side reads the source and relays an independent run of the published tests.
3. Findings come back as concrete reproduction cases. The author reproduces each one, fixes it, and
   publishes a new revision. Disagreement is stated, with reasons, in the log.
4. "Passed review" is always scoped: it names the commit and what was and was not checked.
5. Loading reviewed code on the laptop is a separate step that needs the owner and a window.

## Commits

- Present-tense subject that says what changed: `Teach revision 14: one store read for entries,
  fingerprint and invalid count`.
- One logical change per commit. Results and the code that produced them can go together.
- Assistants end the message with a `Co-Authored-By:` line naming themselves.
- Never force-push. If a push is rejected, fetch, re-apply your addition on top, and push again.
- Do not push to `main` or merge the pull request unless the owner asks.

## Style

- Python: standard library where possible; type hints on public functions; a docstring that says
  what the function guarantees and what it does not.
- Markdown: plain statements, short paragraphs, tables for comparisons. Dates as `2026-11-14`.
- Line endings: files are committed as they are. `research/coding-quality-v1/` disables all
  end-of-line conversion because its fixture hashes are over exact bytes.

## Where to put things

| You have | Put it in |
|---|---|
| A measurement taken on the laptop | `research/experiments-claude/<date>-<name>/` with the script and a result file |
| A review or audit record | `research/experiments/` or `research/audits/` |
| Evidence about token counting or context | `research/context-preflight/` |
| A new revision of published code | The existing folder, with its README updated |
| A proposal or design | `research/`, as a dated Markdown file |
| A term that needs explaining | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
