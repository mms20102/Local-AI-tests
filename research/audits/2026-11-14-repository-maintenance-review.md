# Repository-maintenance review

Review checkpoint: **2026-11-14 21:32 UTC**. Reviewed Claude's [`00565c1d`](https://github.com/mms20102/Local-AI-tests/tree/00565c1d74bf91a7cc3dfb523963ed6686df471d) documentation/tooling turn, whose producer date is 2026-11-15. No merge, rebase, workflow dispatch, runtime action or local test execution was performed by this review.

## Stable landing page accepted

Keep the root README as the newcomer-facing landing page. Future dated checkpoints from this side go to **docs/CURRENT_STATE.md** and linked audit/result files. The prior landing-page archive and append-only history are preserved. This review does not replace the root README or choose a license.

The maintenance source clearly separates the private full laptop project from published research components and provides useful contribution, privacy and navigation documents. The workflow selects the five authored unit-test suites and relative-link checker; it is not a CODE-Q1 semantic grading command.

## CI status has advanced beyond the turn

Claude's maintenance turn said CI had not yet run. GitHub's current [run metadata](https://github.com/mms20102/Local-AI-tests/actions/runs/43642451133), for head `00565c1d`, now reports **both Ubuntu and Windows Python 3.12 jobs completed successfully**, including test-suite and link-check steps.

That is independently read service metadata, not local execution by this repository session. The author reports 229 tests in five suites with 16 skipped; the runner sums unittest's `Ran` counts, so 229 includes the skipped tests rather than meaning 229 passes plus 16 skips. This review did not independently recount the CI log totals. The reported 282-link/48-file check remains an author result; the CI link-check step also succeeded.

CI success does not establish containment for arbitrary generated code, semantic CODE-Q1 success or safe activation of the disabled execution gate. The grading worker's containment boundary remains open. A dedicated no-network bounded guest/container job is a candidate for assessment, not something this review created or declared safe.

## Wording corrections for the next documentation pass

1. **Speed criterion:** the README table says “15 s to first text.” FINAL_GOAL requires **first useful text**, and task timing must be correctness-qualified. The exploratory 16.1-second first-text and 34.9-second end-to-end figures under download contention are not those acceptance measurements.
2. **Context scope:** the 1,717-token/full-256 probe is useful bounded evidence, not proof of arbitrary long conversations or full native-token/margin equivalence. Keep the front-page status tied to tested shapes and the declared limits.
3. **Context folder map:** replace an unqualified “gateway count equals engine” description with scoped count comparisons and their limits.
4. **Generated-code rule:** CONTRIBUTING/SECURITY's absolute “never executed on the laptop” wording should distinguish the host from a reviewed isolated guest. Mohamed's planned Windows Sandbox route is physically on the laptop; host execution and approved guest execution are different.
5. **Code origin:** CONTRIBUTING says every code folder is copied from the private laptop project. Some prototypes, including the status core, were authored from the cloud side and later reused. Record each folder's actual origin rather than assert one origin for all code.
6. **Authorization channels:** describe authenticated user instructions available in each assistant's environment and the need to respect that environment's rules. An unverified co-chat assertion is not a substitute for permission; that does not make every authenticated delegation or existing user authorization invalid. This preserves Claude's stated session boundary without inventing a universal new approval rule.
7. **Counts and status:** keep exact dated counts in CURRENT_STATE/audits or label them as a baseline. The stable landing page need not be rewritten at every checkpoint.

These are source/document review suggestions, not edits made to Claude's landing-page files. The user's existing scoped instructions continue to govern work; no new approval flow is introduced by this audit.

## Review boundary

The author-reported Windows repeat runs, link totals and original branch merge were not independently rerun here. GitHub metadata confirms successful CI jobs; it does not prove every broader statement in the docs. PR #1 remains a coordination draft unless the owner decides otherwise; this review does not merge or close it.
