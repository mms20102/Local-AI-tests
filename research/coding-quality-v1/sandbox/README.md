# CODE-Q1 behavioural grading in Windows Sandbox

Written by Claude (laptop session), 2026-11-15, after the owner enabled Windows Sandbox on the
laptop. **Not independently reviewed.** The design follows `research/WINDOWS_ISOLATION_PROPOSAL.md`
as far as described under "What it does not give".

## Result

**11 of the 12 first-pass drafts pass every authored case** (target: at least 9 of 12).
112 of 116 cases pass. Arabic tasks 3 of 3; English tasks 8 of 9. All 12 drafts are in the
denominator; none was truncated, refused, repaired or regenerated.

| Task | Cases passed | Result |
|---|---|---|
| A01, A02, A03 | 8/8, 8/8, 10/10 | pass |
| B01, B02, B03 | 9/9, 9/9, 8/8 | pass |
| E01, E02, E03 | 8/8, 21/21, 10/10 | pass |
| F01, F03 | 7/7, 10/10 | pass |
| **F02** (merge intervals) | **4/8** | **fail**: four cases report "mutated input". The draft writes into the caller's own inner lists |

Full records: [results/drafts-first-pass-2026-11-15.json](results/drafts-first-pass-2026-11-15.json).
Drafts: [../drafts-2026-11-14-first-pass/](../drafts-2026-11-14-first-pass/index.json).

This is one first pass of one model configuration (Qwen3.6-35B-A3B, Colibri 2.0.0, cache 32,
thinking off, 256 output tokens, temperature 0). It says nothing about a second sample, and it is
not the speed check: the timings of the drafts were taken while a large download was running.

## Files

| File | Role |
|---|---|
| `sandbox_host.py` | Host side. Stages candidates and calls, writes the `.wsb`, starts and closes the sandbox, reads the report as untrusted data, and judges every case with `grade.judge` |
| `guest_runner.py` | Runs inside the guest from a read-only folder. One fresh interpreter per entry, `grade.py`'s own driver, 10 s deadline, 1 MB output cap. Reports raw records; decides nothing |
| `results/probe-2026-11-15.json` | The probe with repository-authored code only |
| `results/drafts-first-pass-2026-11-15.json` | The grading of the model's drafts |

Identities at the run (SHA-256, also inside each result file): `grade.py` `e9f21618…`,
`manifest.json` `58a0546e…`, `sandbox_host.py` `3a5b2dff…`, `guest_runner.py` `86fe7246…`,
fixture revision 2. `grade.py`'s execution gate was **not** changed or used: the manifest still says
`generated_code_execution_enabled: false`, and this harness calls only the grader's static checks,
its driver text and its judge.

## How it is contained

The `.wsb` file sets: networking disabled; virtual GPU, audio input, video input, printer and
clipboard redirection disabled; protected client mode on; 4 GB of memory. Three folders are mapped:

| Guest path | Host content | Access |
|---|---|---|
| `C:\cq1\in` | candidate files, `__calls__.json` (calls and arguments only), the driver, the guest runner | read-only |
| `C:\cq1\py` | a standalone CPython 3.12.16 | read-only |
| `C:\cq1\out` | empty at start; the guest writes `results.json` and `DONE` | writable |

Expected values and the `raises` expectations never leave the host; the stager refuses to proceed
if it finds them in the staged input. The guest reports what each call returned, raised, and left
in its arguments. The host compares.

Before any case runs, the guest records what it can reach, and the host **refuses the whole
report** if the guest says it connected to any network target, could write to its input folder,
could see the host's user folder or a redirected drive, or did not shut itself down after reporting.

Measured in every session so far: connections to a public address, a public name, a gateway guess
and a link-local address all failed; the input folder was not writable; the only drive was `C:`;
the host's user folder and `\\tsclient` were not visible; the guest shut itself down and no
sandbox process started by the run remained.

## The probe (repository-authored code only)

Run twice, same outcome: 29 entries, 237 cases, every entry as expected.

| Entries | Expected | Observed |
|---|---|---|
| 12 references | pass every case | 12 of 12 pass every case |
| 12 decoys | fail at least one case | 12 of 12 fail |
| Endless loop | stopped at the deadline | status `timeout` after 10.1 s; the session continued |
| 20 MB of output | capped, counted as failed | 20,971,608 bytes written, capped at 1 MB, failed |
| Network attempts from inside a candidate | nothing reached | returned an empty list |
| Looking for host folders, writing to the input folder | nothing seen, nothing written | returned an empty list |
| Overwriting the report and the DONE marker | no effect on the judged result | judged from the runner's own report; the case failed as it should |

## Before the drafts were run

`sandbox_host.py` reads each draft's syntax tree, without importing or running it, and records what
it reaches for. All 12 drafts import nothing outside their own files and use none of `open`, `exec`,
`eval`, `compile`, `__import__`, `getattr` and similar, and no double-underscore attributes. A draft
that did would be given a sandbox session of its own.

## What it does not give

- **No protection of the guest runner from a hostile candidate inside the guest.** They share the
  guest and its administrator account. A candidate written to attack the runner could make cases
  look like crashes, or interfere with other entries in the same session. It still could not report
  a pass without producing the expected values, because those never enter the guest. For these 12
  drafts this rests on the source scan above, which is a reading and not a proof. `--isolate` runs
  one session per entry.
- **The report driver runs in the candidate's interpreter.** The returned value, the raised
  exception and the state of the arguments are observed by `grade.py`'s driver in the same process
  as the candidate. This is the limit the readiness audit on `main` describes; it is unchanged.
- **The 10 s deadline and 1 MB cap are per entry**, as in `grade.py`, not per case.
- **Windows Sandbox is the boundary.** Nothing here tests the hypervisor. The settings are the
  documented ones; their effect was observed only through the guest's own probes.
- **Not independently reviewed, and not reproducible by the reviewer's Linux environment.**

## Run

Needs Windows 10/11 Pro or Enterprise with the Windows Sandbox feature enabled, and a standalone
Python folder containing `python.exe` to map into the guest. Only one sandbox can run at a time.

```
python sandbox_host.py probe  --python <python folder> --run-dir <empty folder> --out probe.json
python sandbox_host.py drafts --python <python folder> --run-dir <empty folder> --drafts ..\drafts-2026-11-14-first-pass --out drafts.json
```

Run the probe first. Do not run drafts if the probe does not report `"probe_ok": true`.
