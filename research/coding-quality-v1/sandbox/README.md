# CODE-Q1 behavioural grading in Windows Sandbox

Written by Claude (laptop session), 2026-11-15, after the owner enabled Windows Sandbox on the
laptop.

| Version | Commit | Status |
|---|---|---|
| First harness | `377fae14` | Graded the 12 drafts once. [Independently reviewed](../../audits/2026-11-15-windows-sandbox-grading-review.md): totals recompute; a judge false pass and several collection gaps were found |
| Runner revision 7 (`cq1-sandbox-7`) | `48ded74` | Judge and parsing repaired; candidates confined; hostile fixtures kept outside the repository. Sixth probe, handwritten code only: all 36 outcomes as indexed. Drafts re-graded on it: 11 of 12. **Not independently reviewed** |

## Result so far (provisional)

With the **first** harness: **11 of the 12 first-pass drafts pass every authored case** (target: at
least 9 of 12); 112 of 116 cases; Arabic 3 of 3, English 8 of 9. All 12 drafts are in the
denominator; none was truncated, refused, repaired or regenerated. F02 (merge intervals) fails 4 of
8 cases with "mutated input".

The independent review records this as a provisional author-reported result. The per-case records
of that run were not kept, so nobody can re-judge it. It is one first pass of one model
configuration (Qwen3.6-35B-A3B, Colibri 2.0.0, cache 32, thinking off, 256 output tokens,
temperature 0), and it is not the speed check.

Records: [results/drafts-first-pass-2026-11-15.json](results/drafts-first-pass-2026-11-15.json).
Drafts: [../drafts-2026-11-14-first-pass/](../drafts-2026-11-14-first-pass/index.json).

## Files

| File | Role |
|---|---|
| `sandbox_host.py` | Host side. Stages candidates and calls, writes the `.wsb`, starts and closes the sandbox, reads the report as untrusted data with a strict parser, and judges every case with `grade.judge` |
| `guest_runner.py` | Runs inside the guest from a read-only folder. Protects its own process, runs one confined interpreter per entry with `grade.py`'s own driver, reports raw records; decides nothing |
| `source_gate.py` | Reads a candidate's syntax tree, without importing or running it, and says whether it stays inside plain computation |
| hostile fixtures (**not in the repository**) | Twelve handwritten hostile programs with an `index.json` saying what each must produce. Removed from the repository on 2026-11-15 by the owner's decision and kept on the laptop for re-testing. Pass their folder with `--hostile`. Commits up to `d9c0d7d` still contain them at `sandbox/hostile/`. **Never run them outside this harness** |
| `../test_sandbox_gate.py`, `../test_judge_strict.py` | Offline tests: the gate's escape routes and ordinary code; the judge and report parsing against handwritten malformed and forged records |
| `results/` | Every probe, including the failed ones, each with the guests' raw reports |

`grade.py`'s execution gate was not changed or used: the manifest still says
`generated_code_execution_enabled: false`, and this harness calls only the grader's static checks,
its driver text and its judge.

## How a hostile program could disturb the runner, the cause, and what was done

| What it could do | Cause | Change | Seen in the sixth probe |
|---|---|---|---|
| End the guest runner | It ran as the same user, and a process's default access list grants that user the right to terminate it. Low integrity does **not** remove that right (measured) | The runner replaces its own access list with one granting SYSTEM only, checks that a fresh terminate handle on itself is refused, and runs no candidate otherwise | `P_kill_runner` returned `refused`; the runner reported normally |
| Start other processes | No limit | Created suspended, placed in a job object allowing one process, membership checked before resume | `P_spawn`: none started |
| Use unlimited memory | No limit | Job caps memory at 1,024 MB | `P_memory`: `MemoryError` inside the candidate |
| Flood output (first harness: 20,971,608 bytes written) | Output went to a file, cut only when read back | Output goes to a pipe the runner reads; it stops reading at 1 MiB and ends the job. Bound: the limit plus one pipe buffer | `P_print_flood` 1,048,606 bytes accepted; `P_output` 1,114,112 |
| Write files in the guest | Ran with the runner's full token | Restricted token, removable privileges removed, low integrity; integrity verified before resume | `P_write` could not write the work folder, Windows temp or its own folder |
| Write into the report folder | It is a host share; integrity levels are not applied there (measured in the fifth probe) | **Not prevented.** Detected: after each candidate the runner removes anything but its own log and fails the entry as tampering; the host refuses a report folder with unexpected files and closes the sandbox above 16 MiB (sampled every 2 s) | `P_write` and `P_spoof`: `report_folder_tampered` |
| Forge a result line | Parser took the last line | Only the last line of a clean, confined run is parsed, strictly; records must have exactly the driver's fields | `P_forge_line` failed on its real value; `P_forge_then_hang` timed out |
| Pass with a malformed record | Judge compared absent fields as equal | `grade.judge` needs a positive match | covered offline in `../test_judge_strict.py` |
| Reach `os`, `ctypes`, frames, builtins and share a session with others | Nothing sorted candidates | `source_gate.py`: only plain code shares a session and can be marked trusted; anything else runs alone and is never trusted | seven fixtures ran alone, untrusted |

## Probe history (handwritten code only)

| Probe | Runner | Outcome |
|---|---|---|
| 1 | first harness | 29 entries as expected; flood wrote 20,971,608 bytes |
| 2 | 3 | as indexed, but the index accepted the runner being killed: `P_kill_runner` session gave no report (902 s) |
| 3 | 4 | **failed**: `P_kill_runner` no report again; `P_write` not started (host memory) |
| 4 | 5 | **failed closed**: all 36 interpreters exited 0xC0000142 after the Administrators group was made deny-only |
| 5 | 6 | **failed**: `P_kill_runner` refused for the first time; `P_write` wrote the report folder |
| 6 | 7 | `probe_ok: true`: 12 references pass, 12 decoys fail, 12 fixtures as indexed; 8 sessions, 8 reports, 8 guest shutdowns |
| 7 | 7 | fixtures moved outside the repository; the 12 original ones as indexed again. Nine new threat checks: **four found something** |
| partial | 8, 9 | runner leaves its console; candidates detached from any console; thread check rewritten |
| 8 | 9 | 45 entries, 17 sessions: 43 as indexed. **Two findings remain open**: a candidate can read the report folder and the harness's own input |

Sixth probe: [host result](results/probe6-runner7-2026-11-15.json),
[raw guest reports](results/probe6-runner7-2026-11-15-guest-reports.json). `probe_ok` means every
outcome matched the fixtures' `index.json`; it is not a statement that every safety property holds.

## Threat checks added after the first twelve (probe 8, runner revision 9)

These only ask and report; none ends, suspends or shuts anything down.

| Check | Question | Observed |
|---|---|---|
| `T_thread_runner` | handles to suspend or end the runner's threads, by guessing thread numbers | none granted; its own threads were found, so the method works |
| `T_other_processes` | a terminate handle on any other guest process | none. On runner 7 it was granted one on `conhost.exe`; candidates are now created detached from any console and the runner leaves its own |
| `T_shutdown_privilege` | switch on the shutdown privilege | refused |
| `T_breakaway` | start a process outside the job, in a new group, or detached | none started |
| `T_threads` | 500 busy threads, never returns | `timeout` |
| `T_done_then_hang` | write `DONE` early, then never return | `report_folder_tampered`; session closed normally |
| `T_fill_share` | write 64 MB into the report folder | wrote it; detected and removed, `report_folder_tampered`. The host's sampled 16 MiB check did not trigger in the time it took |
| `T_read_share` | read the report folder | **open**: read `progress.log` |
| `T_read_harness` | read the harness's input | **open**: read `entries.json`, the runner's source, the driver, and listed the entries and work folders |

The two open findings mean a candidate that shares a session with others could read their source
files and the calls made to them. It cannot read expected values, which never enter the guest. Only
candidates the source gate calls plain share a session, and plain code cannot open files; that is
the gate's reading, not a boundary.

Results: [probe 7](results/probe7-runner7-2026-11-15.json), [probe 8](results/probe8-runner9-2026-11-15.json),
each with its raw guest reports beside it. The drafts were graded on runner 7; runners 8 and 9
change only how the console is handled, and the drafts have not been re-run on them.

## How it is contained

The `.wsb` file sets: networking disabled; virtual GPU, audio input, video input, printer and
clipboard redirection disabled; protected client mode on; 2 GB of memory. The host does not start a
session with less than 3,584 MB free. Three folders are mapped:

| Guest path | Host content | Access |
|---|---|---|
| `C:\cq1\in` | candidate files, `__calls__.json` (calls and arguments only), the driver, the guest runner | read-only |
| `C:\cq1\py` | a standalone CPython 3.12.16 | read-only |
| `C:\cq1\out` | empty at start; the guest writes `progress.log`, then `results.json` and `DONE` at the very end | writable |

Expected values and `raises` expectations never leave the host. The host refuses the whole report
if the guest does not report all four network checks as failed, could write to its input folder,
could see host folders, did not report its runner as protected, repeated a key in its JSON, left
unexpected files in the report folder, or did not shut itself down after reporting.

## What it does not give

- **Writes to the report folder are detected, not prevented**, and the size check is sampled. A
  candidate has up to its 10-second deadline to write to the host's scratch folder at disk speed.
- **Read access inside the guest is not restricted.** A candidate can read the report folder and the
  harness's input, including other entries staged in the same session.
- **The source gate is a triage rule, not a safety boundary or a proof.** It is unreviewed.
- **The report driver still runs in the candidate's interpreter.** For a plain candidate the
  returned value, the exception and the state of the arguments are the driver's word.
- **Sandbox processes are identified by image name**, not ownership. After a session the host has
  to close by force, a `vmmemWindowsSandbox` process holding about 1.6 GB stays for some tens of
  minutes; it cannot be inspected or ended without administrator rights.
- **Isolation and confinement evidence is the guest's own report.** Nothing here tests the
  hypervisor, IPv6, or the `.wsb` settings from outside.
- **A check on the host does not stand in for the guest.** Token and access behaviour differed
  between the two (probe 4).

## Run

Needs Windows 10/11 Pro or Enterprise with the Windows Sandbox feature enabled, and a standalone
Python folder containing `python.exe` to map into the guest. Only one sandbox can run at a time; a
leftover `WindowsSandboxServer.exe` (the `wsb list` command starts one) must be closed first.

```
python sandbox_host.py probe  --python <python folder> --run-dir <empty folder> --out probe.json [--hostile <fixtures folder>]
python sandbox_host.py drafts --python <python folder> --run-dir <empty folder> --drafts ..\drafts-2026-11-14-first-pass --out drafts.json
```

Run the probe first (about three minutes with the hostile fixtures; without `--hostile` it runs the
references and decoys only, which checks grading but not containment). Do not run drafts if it does not report
`"probe_ok": true`.
