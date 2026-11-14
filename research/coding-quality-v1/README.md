# CODE-Q1: private coding regression suite (fixtures and grader)

Written by Claude on 2026-11-14 at Mohamed's request. It fills in what
[coding-quality-v1.proposed.json](../coding-quality-v1.proposed.json) (ChatGPT/Codex) left null: the
same 12 task ids, families, callables and contracts, now with prompts, pinned starters, reference
solutions, decoys and test cases. I did not edit the proposal file.

**Status: fixtures and grader only.** Nothing here sends a request to a model, and nothing here has
been run against a model. No pass rate exists yet.

## What is in the folder

| Path | Purpose |
|---|---|
| `fixtures/<ID>/prompt.txt` | The exact text to send for the task (English, or Arabic for A01–A03) |
| `fixtures/<ID>/starter/` | Pinned buggy or stub files for bug-fix and edit tasks (shown in the prompt) |
| `fixtures/<ID>/reference/` | A correct solution |
| `fixtures/<ID>/decoy/` | A plausible wrong answer; for bug-fix and edit tasks this is the starter |
| `fixtures/<ID>/public_tests.json` | The example shown in the prompt |
| `fixtures/<ID>/hidden_tests.json` | Cases never shown to the model |
| `manifest.json` | SHA-256 of every prompt, test file, reference, starter and decoy |
| `build_fixtures.py` | Regenerates all of the above, byte for byte |
| `grade.py` | The grader |
| `test_grade.py` | 23 offline tests for the grader |

116 cases in total across the 12 tasks. Prompts are 380 to 1,060 characters, so they fit a
2,048-token context. Whether every reference fits the 256-token output ceiling has not been checked
with the model's tokenizer.

## Use

```
python grade.py verify-fixtures        # the suite checks itself
python grade.py static F01 draft.json  # structure of one saved draft; runs nothing
python -B -m unittest test_grade       # the grader's own tests
```

`draft.json` can be a file saved by the local draft helper (`content`, `finish_reason`,
`truncated`) or a plain text file with the answer.

## What each level means

| Level | What it establishes | Runs model code? |
|---|---|---|
| transport | A complete answer arrived (`finish_reason` is `stop`, not truncated) | No |
| structure | Fences closed, each file parses, every required function is defined, files are named | No |
| semantics | Every public and hidden case passes | **Yes** |

A structural pass is reported as `semantics: not_assessed`, never as correct. The value judge is
type-strict: `True` is not `1`, `2` is not `2.0`, list order matters, dict order does not, and an
answer that modifies its input fails.

## The execution gate

`grade.py semantic` executes model-written code in a child Python process. A child process is not
isolation. The command therefore refuses unless it is given `--i-am-in-a-sandbox` **and** the
environment variable `CODE_Q1_SANDBOX=1`, which should be set only inside a disposable sandbox
(for example Windows Sandbox with networking off and a read-only copy of this folder). That sandbox
has not been set up or tested. Until it is, only the static level is available for model output.

`verify-fixtures` and the tests do run code, but only the references, starters and decoys in this
repository.

## Verified today (measured on the laptop, Python 3.12.16)

- `verify-fixtures`: all 12 references pass all their cases; all 12 decoys fail at least one hidden
  case; manifest hashes match; no hidden case appears in a prompt.
- `test_grade`: 23 tests pass.

## Not done

- No model run, so no baseline. Collecting drafts needs model traffic, which belongs to the PC
  worker and an agreed window.
- No sandbox, so no semantic grading of model output.
- The decoys for A02, F02 and F03 fail only one or two hidden cases; more cases would make those
  three tasks stricter.
- The proposal asks for a fresh holdout set and four calibration fixtures; neither exists yet.
- Twelve tasks is small. Treat results as a regression signal, not a benchmark score.
