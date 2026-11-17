# Evidence provenance

This map distinguishes what the repository can support from what is only
reported by another worker or remains unverified.

| Evidence class | Meaning | Examples in this repository |
|---|---|---|
| `independently_reviewed` | A scoped source/artifact review was performed without claiming live runtime proof | `research/audits/2026-11-14-*.md`; `research/audits/2026-11-15-windows-sandbox-grading-review.md` |
| `reproduced` | Arithmetic or source properties were recomputed from saved artifacts | Window-9 normalization and sandbox artifact reconciliations in `research/experiments/` |
| `reported_only` | A worker or co-chat reported an action/result not rerun in this checkout | Laptop windows, loaded callback identity, and reported `11/12` execution |
| `synthetic` | Trusted offline fixture or fake-backend evidence | Teach fixtures, planner checks, and saved context pairs |
| `unverified` | Required identity, boundary, or live behavior is missing | Runtime process identity, final wire payload, host/guest separation, clean speed |

## Evidence handling rules

1. Keep raw artifacts and their source/revision identifiers before summaries.
2. Label every aggregate with its denominator and whether it is reported or
   independently recomputed.
3. Treat missing, malformed, timed-out, truncated, refused, or unobserved cases
   as failures for a controlled run.
4. Never publish private prompts, notes, credentials, model files, or raw
   personal logs.
5. This repository session did not execute generated code, start the local
   model, access the laptop, or perform hostile probes.

## Known provenance limits

- The Windows review recomputes published totals but lacks raw per-case records
  for independent re-grading.
- Sandbox probe reports are guest/host observations, not proof of prevention.
- Source-only and fake-backend tests do not establish live process identity,
  tokenizer parity, or production readiness.
- A benchmark result cannot be called independent merely because another worker
  produced it.
