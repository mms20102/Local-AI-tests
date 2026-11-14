# Window 8: reported operation and artifact normalization

2026-11-14. Claude explicitly reported window 8 **closed** at [source `370b6765`](https://github.com/mms20102/Local-AI-tests/blob/370b6765feb4a1a5507334143eeaa575ad064092/research/co-chat.md). The [published sanitized result](https://github.com/mms20102/Local-AI-tests/blob/370b6765feb4a1a5507334143eeaa575ad064092/research/experiments-claude/2026-11-14-window8/result.json) was read as JSON and its arithmetic recomputed here in JavaScript. These are **author-reported laptop observations**, not a new PC inspection or repeated experiment.

[Machine-readable intake](experiments/2026-11-14-window8-normalized-intake.json).

## Denominators from the artifact

| Group | Published records | Outcomes |
|---|---:|---|
| Session | 20 | 18 ordinary HTTP 200/nonempty; one deliberate 413; one early-closed stream |
| Additional probes | 5 | Two 200; two 422; one 413 |
| Requests during network sampling | 3 | Three 200 |
| **Total represented records** | **28** | **Not an independently traced total of all HTTP activity** |

The 18 ordinary session records include **15 stop and 3 length** finishes. Their median elapsed time is **9.0 s**, maximum **15.3 s**, and every session row reports healthy afterward. Those timings include length-ended outputs and download contention; they are not semantic-quality or correctness-qualified speed results.

Across additional and network probes, **five** saved own-count/engine-count pairs match: 51, 1717, 50, 74 and 1717. Four of these five replies are length-ended; two explicitly used all 256 requested output tokens. This supports agreement for those recorded requests, not universal tokenizer/profile safety or a derived 32-token bound.

The narrative says the 51-token Arabic-history probe ran twice; the artifact has **one** such row. Do not fabricate a second observation. The reported 22 nothing-added hook lines have no per-request correlation in the artifact, so their coverage cannot be independently reconciled with all represented admitted/cancelled requests.

## Operation evidence, with limits

Three stop-file/start cycles report no leftover stack processes. Stops are 11.6 s each; starts 46.3/40.6/40.6 s. Post-start available RAM is 7.47/7.46/7.33 GiB and derived rounded commit headroom 2.41/2.32/2.26 GiB. These are recorded samples, not peaks or sustained resource clearance. Ctrl+C from the owner guide was not exercised.

Session request 7 reports real HTTP **413 / `local_chat_context_budget_exceeded`**. That extends the earlier stub-only component evidence for this one reason. It does not verify the other counter-error HTTP types or constitute an independent capture here.

The startup logs reportedly say profile-bound counting and teach invocation. Hook revision 18 is still **inferred from the source present at startup**. The real note store was not edited; live nonempty-note behavior and the proposed status display are untested.

## Network scope and release checks

Nine TCP samples over 82 seconds cover seven stack processes during three requests, plus one UDP snapshot. No nonloopback remote endpoints or UDP endpoints were recorded. Sampling may miss transient connections, excludes the browser/other processes and is not a packet capture or privacy proof.

These observations advance bounded context and stop-file/session evidence. They do not complete semantic CODE-Q1 quality, first-useful-text/correctness-qualified timing, Ctrl+C/guide validation, nonempty teaching or exact loaded identity. The closure does not request new traffic. The separate cloud capture fixture and offline status prototype remain unloaded.
