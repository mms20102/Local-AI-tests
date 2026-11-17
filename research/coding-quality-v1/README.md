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
| `test_grade.py` | 31 offline tests for the grader |
| `token_preflight.py`, `token_preflight_result.json` | Real token counts for prompts and references, and the result |

116 cases in total across the 12 tasks (fixture revision 2).

**Token preflight (measured 2026-11-14, offline).** `token_preflight.py` counts tokens with the
installed model's own `tokenizer.json` (SHA-256 `5f9e4d49...cb42`, `tokenizers` 0.23.3); no model is
run. Requests are rendered the way the installed server renders them for this model with thinking
off, read from its source (Colibri 2.0.0 `openai_server.py`, SHA-256 `67817219...d43d`, function
`render_chat_qwen`): ChatML frames, no default system text, and a generation prompt that ends with a
pre-closed think block. With the draft helper's one-line system text, the largest request is
**300 tokens** (E03) and the largest reference answer is **137 tokens** (E02), against a
2,048-token context and a 256-token output ceiling. Every prompt and every reference fits. Full
table: [token_preflight_result.json](token_preflight_result.json).

Two limits on that result. Whether the engine binary adds a beginning-of-sequence token or anything
else after rendering is not established (recorded as null); it would be a small constant. And a
reference answer fitting says nothing about how long the model's own answer will be.

The prompts restate the proposal's contracts. The three Arabic prompts keep the proposal's meaning
but are not verbatim copies: each adds the file name and one example. Answer format, frozen with
this revision: one fenced Python block per file; for the two-file task each block starts with
`# file: invoice.py` or `# file: summary.py`. A format failure is reported under structure, not
semantics.

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
isolation. The command refuses unless all three hold: `manifest.json` has
`generated_code_execution_enabled: true` (it is `false`), the flag `--i-am-in-a-sandbox` is given,
and the environment variable `CODE_Q1_SANDBOX=1` is set. The flag and variable are an
acknowledgement by whoever runs it; this program does not create or verify a sandbox, and it has no
memory, process-tree or network limits of its own. A reviewed runner that enforces isolation is
still to be built. Until then only the static level is available for model output.

**Judging boundary.** The child process receives only the function calls and their arguments. It
reports what each call returned or raised and the arguments afterwards; the parent process holds
the expected values and decides pass or fail. Expected values are never written into the
candidate's folder. Residual limit: candidate code runs in the same process as the small reporting
driver, so it could falsify the report of *its own* behaviour (for example hide that it modified an
input). The call file does not give it the expected answers and it cannot declare a pass. Nothing here
stops it from reading other files on the machine, including this folder's fixtures: that needs real
filesystem and process isolation.

## Acceptance items for a future execution runner (not built)

Recorded from ChatGPT's round 13 review. Generated-code execution stays disabled until a separately
reviewed runner meets all of these:

1. Host containment: no network, no host credentials, and no access to fixture answers from inside
   the sandbox.
2. Integrity of observations, separate from containment: return values, exceptions and input
   mutation must be observed by something the candidate cannot alter. An in-process reporter is not
   that, inside a VM or not.
3. Bounded capture: read the child's stdout and stderr incrementally with a hard limit, and record
   an overflow as a failure. Today `MAX_CHILD_OUTPUT_BYTES` only limits what is parsed;
   `capture_output=True` collects everything first, and stderr is unbounded.
4. Whole process-tree termination on timeout, plus memory and process-count limits.
5. The manifest gate stays authoritative, and the runner's evidence boundary is reviewed before the
   gate is opened.

`verify-fixtures` and the tests do run code, but only the references, starters and decoys in this
repository.

## Verified today (measured on the laptop, Python 3.12.16)

- `verify-fixtures`: all 12 references pass all their cases; all 12 decoys fail at least one hidden
  case; manifest hashes match; no hidden case appears in a prompt.
- `test_grade`: 31 tests pass, including: a candidate cannot see expected values or print its own
  verdict; a tuple is not a list; input mutation is caught on the exception path; known truncation
  overrides a missing finish reason; the manifest gate refuses even with the sandbox flag.

## Not done

- No model run, so no baseline. Collecting drafts needs model traffic, which belongs to the PC
  worker and an agreed window.
- No sandbox and no reviewed runner, so no semantic grading of model output.
- "Returns a new object" is checked only on three cases (E01 twice, F02 once), and only that the
  result is not the very object passed in.
- The decoys for A02, F02 and F03 fail only one or two hidden cases; more cases would make those
  three tasks stricter.
- The proposal asks for a fresh holdout set and four calibration fixtures; neither exists yet.
- Twelve tasks is small. Treat results as a regression signal, not a benchmark score.
