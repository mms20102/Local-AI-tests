# Security and privacy

This repository is published. The laptop project it describes is not. The rules below keep it that way.

## Never commit

- Keys, tokens, passwords, or files that hold them (`local.env`, `.env`, `*.key`, `*.pem`).
- Chats, prompts typed by the owner, or the contents of the teaching store.
- Raw service logs. Publish counts and outcomes, not log text.
- Model files or tokenizer files.
- The laptop project's launchers, configuration or settings, unless the owner approved that file.
- Anything that identifies a person beyond the repository owner's public account name.

`.gitignore` blocks the common cases. It is a safety net, not the rule.

## Publishing from the laptop

A file from the private project is published only when the owner has approved it, by name or by a
clearly scoped group. Approvals so far, recorded in the shared log:

| What | Folder |
|---|---|
| The five teaching files | `research/teach-store/` |
| The gateway request check, its counter and tests | `research/gateway-admission/` |
| The model's twelve first-pass answers to the CODE-Q1 tasks | `research/coding-quality-v1/drafts-2026-11-14-first-pass/` |

Before publishing, scan the file for local paths, key-shaped strings and personal text. Result files
are published as counts, lengths, hashes and timings; answer text is removed unless it is the thing
being published.

## Third-party material

A sample of questions from a public benchmark was used once to compare models. The benchmark's
maintainers ask that items not be republished, so neither the questions nor the answers are in this
repository. Only aggregate counts are.

## Generated code

Code written by the model is data. It is never executed on the laptop. The CODE-Q1 grader runs
authored cases against a draft only when a manifest flag, a command-line flag and an environment
variable are all set, and that is done only in an isolated environment that has no access to the
laptop.

## Test credentials in this repository

Some test fixtures contain strings shaped like keys, such as
`sk-synthetic-master-key-for-the-scratch-fixture-only-…`. They are handwritten, grant access to
nothing, and exist because the code under test validates the shape of its keys.

## If something private is committed

1. Do not try to hide it with a follow-up commit; the history still has it.
2. Tell the owner at once, with the commit and file.
3. Treat any exposed credential as compromised and replace it on the laptop.
4. Rewriting published history is the owner's decision.

## Reporting a problem

Open an issue on the repository, or tell the owner directly. Do not include the sensitive content
itself in the report.
