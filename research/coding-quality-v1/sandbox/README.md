# CODE-Q1 behavioural grading in Windows Sandbox

Written by Claude (laptop session), 2026-11-15, after the owner enabled Windows Sandbox on the
laptop. Two versions exist:

| Version | Commit | Status |
|---|---|---|
| First harness | `377fae14` | Graded the 12 drafts once. [Independently reviewed](../../audits/2026-11-15-windows-sandbox-grading-review.md): totals recompute, a judge false pass and several collection gaps were found |
| This harness (`cq1-sandbox-3`) | `1f32bb4e` | Judge and parsing repaired, candidates confined by a job object, source gate, hostile fixtures kept. Probe run with handwritten code only. **Not yet independently reviewed. The drafts have not been re-run on it** |

## Result so far (provisional)

With the **first** harness: **11 of the 12 first-pass drafts pass every authored case** (target: at
least 9 of 12); 112 of 116 cases; Arabic 3 of 3, English 8 of 9. All 12 drafts are in the
denominator; none was truncated, refused, repaired or regenerated. F02 (merge intervals) fails 4 of
8 cases with "mutated input".

The independent review records this as a provisional author-reported result. The per-case records
of that run were not kept, so nobody can re-judge it, and it cannot be shown from the published
file that no passing case went through the malformed-record path the review found. It is one first
pass of one model configuration (Qwen3.6-35B-A3B, Colibri 2.0.0, cache 32, thinking off, 256 output
tokens, temperature 0), and it is not the speed check.

Records: [results/drafts-first-pass-2026-11-15.json](results/drafts-first-pass-2026-11-15.json).
Drafts: [../drafts-2026-11-14-first-pass/](../drafts-2026-11-14-first-pass/index.json).

## Files

| File | Role |
|---|---|
| `sandbox_host.py` | Host side. Stages candidates and calls, writes the `.wsb`, starts and closes the sandbox, reads the report as untrusted data with a strict parser, and judges every case with `grade.judge` |
| `guest_runner.py` | Runs inside the guest from a read-only folder. One confined interpreter per entry, `grade.py`'s own driver. Reports raw records; decides nothing |
| `source_gate.py` | Reads a candidate's syntax tree, without importing or running it, and says whether it stays inside plain computation |
| `hostile/` | Eleven handwritten hostile programs, kept for re-testing the harness, with `index.json` saying what each must produce. **Never run them outside this harness** |
| `../test_sandbox_gate.py`, `../test_judge_strict.py` | Offline tests: the gate's escape routes and ordinary code; the judge and report parsing against handwritten malformed and forged records |
| `results/probe-hostile-2026-11-15.json` | The probe of this harness, as judged by the host |
| `results/probe-hostile-2026-11-15-guest-reports.json` | The guests' raw reports of that probe, per case, unedited |
| `results/probe-2026-11-15.json`, `results/drafts-first-pass-2026-11-15.json` | The first harness's probe and its grading of the drafts |

`grade.py`'s execution gate was not changed or used: the manifest still says
`generated_code_execution_enabled: false`, and this harness calls only the grader's static checks,
its driver text and its judge.

## How a hostile program could disturb the runner, and what was done about each cause

| Cause in the first harness | Change | Seen in the probe |
|---|---|---|
| The candidate could start other processes | Its interpreter is created suspended, put in a Windows job object that allows one process, then resumed. If the job cannot be applied the candidate is not run | `P_spawn`: three ways of starting a program, none started |
| Nothing limited its memory | The job caps it at 1,024 MB | `P_memory`: stopped by `MemoryError` after 1.8 s; the other entries continued |
| Output was only cut when read back; a flood wrote 20,971,608 bytes | The output file is watched while the candidate runs, and the job is ended when a sample shows it above 4 MB | `P_print_flood`: ended after 0.3 s with **8,323,324 bytes written**. This is a sampled stop (every 20 ms), not a hard quota: the overshoot here was about 4.1 MB |
| A nonzero exit or capped output could still be read as records | An entry is judged only if it finished, was confined, exited 0 and was not capped | `P_output`: 20,971,608 bytes written within its 0.4 s run, no records accepted |
| A forged line on standard output | Only the driver's last line of a clean run is parsed, strictly; every record must have exactly the driver's fields | `P_forge_line` judged on its real wrong value; `P_forge_then_hang` timed out, nothing read |
| A malformed record could pass (`raised` with no `error` against a value case) | `grade.judge` needs a positive match; see `../test_judge_strict.py` | covered offline, not in the sandbox |
| A candidate that reaches `os`, `ctypes`, frames or builtins shares the runner's guest and the driver's interpreter | `source_gate.py` lets only plain code share a session and be marked trusted. Anything else runs **alone** in its own session and is marked untrusted whatever it reports | `P_kill_runner`: see below |

**What was not eliminated.** `P_kill_runner` ended the guest runner: its session produced no report,
hit the 15-minute host deadline, was closed by the host and refused. So a candidate that reaches
the Windows API can still stop the runner. The effect is contained rather than prevented: such a
candidate is not plain, so it runs alone, no other entry shares its session, and no result is
accepted from it.

## The probe of this harness (handwritten code only)

One run, seven sandbox sessions, 35 entries, `probe_ok: true`.

| Entries | Expected | Observed |
|---|---|---|
| 12 references | pass every case | 12 of 12 |
| 12 decoys | fail at least one case | 12 of 12 fail |
| `P_loop` | stopped at the deadline | `timeout` at 10.0 s, session continued |
| `P_print_flood` | stopped as a flood | `output_flood`, 8,323,324 bytes written |
| `P_memory` | fails, runner unharmed | `raised MemoryError` |
| `P_forge_line`, `P_forge_then_hang` | forged line not believed | failed on value; `timeout` |
| `P_output` (alone) | no pass | output capped, failed |
| `P_network` (alone) | reaches nothing | empty list |
| `P_host_files` (alone) | sees and writes nothing | empty list |
| `P_spoof` (alone) | fabricated report not accepted | runner's own report judged; wrong value failed |
| `P_spawn` (alone) | starts nothing | empty list |
| `P_kill_runner` (alone) | never a trusted pass | no report; session refused |

In the six sessions that reported, the guest said: four network checks failed, input folder not
writable, only drive `C:`, host user folder and `\\tsclient` not visible; each guest shut itself
down and the host found no sandbox process afterwards.

## How it is contained

The `.wsb` file sets: networking disabled; virtual GPU, audio input, video input, printer and
clipboard redirection disabled; protected client mode on; 2 GB of memory. The host does not start a
session with less than 3,584 MB free. Three folders are mapped:

| Guest path | Host content | Access |
|---|---|---|
| `C:\cq1\in` | candidate files, `__calls__.json` (calls and arguments only), the driver, the guest runner | read-only |
| `C:\cq1\py` | a standalone CPython 3.12.16 | read-only |
| `C:\cq1\out` | empty at start; the guest writes `results.json` and `DONE` at the very end | writable |

Expected values and `raises` expectations never leave the host; the stager refuses to proceed if it
finds them in the staged input. The host refuses the whole report if the guest does not report all
four network checks as failed, could write to its input folder, could see host folders, repeated a
key in its JSON, or did not shut itself down after reporting.

## What it does not give

- **The source gate is a triage rule, not a safety boundary or a proof.** It decides who shares a
  session and whose observation is called trusted. It is unreviewed.
- **The report driver still runs in the candidate's interpreter.** For a plain candidate the
  returned value, the exception and the state of the arguments are the driver's word, protected
  only by the gate's reading of the source.
- **The output limit is sampled**, as shown above, and the writable report folder has no quota.
- **Sandbox processes are identified by image name**, not by ownership, and cleanup is not verified
  beyond a second listing.
- **Isolation evidence is the guest's own report.** Nothing here tests the hypervisor, IPv6, or the
  `.wsb` settings from outside.
- **The 10 s deadline is per entry**, as in `grade.py`, not per case.

## Run

Needs Windows 10/11 Pro or Enterprise with the Windows Sandbox feature enabled, and a standalone
Python folder containing `python.exe` to map into the guest. Only one sandbox can run at a time.

```
python sandbox_host.py probe  --python <python folder> --run-dir <empty folder> --out probe.json
python sandbox_host.py drafts --python <python folder> --run-dir <empty folder> --drafts ..\drafts-2026-11-14-first-pass --out drafts.json
```

Run the probe first. Do not run drafts if the probe does not report `"probe_ok": true`. The probe
takes about 20 minutes because `P_kill_runner` waits out the host deadline.
