# Windows isolation proposal for coding evaluation

Status: **design candidate for review, not implemented, tested or approved**, 2026-11-14. No generated code, Windows feature, VM or sandbox was started. It supports the [shared finish-line proposal](FINAL_GOAL.md); it does not establish that the coding suite is safe to execute.

## One concrete starting method

Use a fresh **Windows Sandbox session** as the candidate execution boundary, with a small synthetic-only staging bundle. Microsoft's documentation supports a custom `.wsb` configuration with networking, clipboard and GPU sharing disabled, explicit memory and read-only input mappings; default sharing settings must not be assumed safe. Feature/virtualization availability and any required restart must first be checked. Sources: [configuration](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file), [installation prerequisites](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-install).

**This is a proposed use of those facilities, not a Microsoft guarantee or independent reviewer acceptance.** This session cannot inspect Windows or the local unpublished runner. If the required guest process separation and bounded observation cannot be demonstrated with Sandbox, use a dedicated disposable VM design instead; do not substitute an ordinary host subprocess.

## Design that still needs review and implementation

1. Create a unique disposable per-run bundle with pinned task IDs, input hashes and a trusted offline Python distribution. Copy only required candidate files and input data; reject unexpected paths, symlinks/reparse points and oversized files before reading/importing. No model, personal repository, home directory, credentials, taught store or private log is shared.
2. Keep expected answers, hidden grading decisions and the final run manifest outside the candidate environment. Candidate outputs are observations, not a self-reported pass/fail. Define a bounded request/response protocol and validate it outside the guest. For file-edit tasks, inspect the resulting files/diffs as data; never import/evaluate guest results on the host.
3. Separate the trusted observation wrapper from candidate execution, with candidate privileges and writable paths restricted. Sandbox containment alone does not prove honest reporting: guest code may try to alter the wrapper, output or other candidates. Demonstrate the separation or explicitly keep semantic scoring blocked.
4. Use read-only inputs. If a result transfer directory is necessary, dedicate an empty per-run directory and treat every returned byte as untrusted. The host parses only a capped, validated format and checks expected cases itself. Never execute returned commands, follow returned paths or map a real project for writes.
5. Enforce declared task deadlines, total wall time, output/file-size limits and resource admission. Record guest/process termination and incomplete observations. Stop only processes/sessions created for this run, with their recorded identities. Missing telemetry/cleanup evidence fails the run rather than implying success.
6. Test the design first with **handwritten** good/bad fixtures and deliberate failures: wrong result, attempted result spoofing, timeout, huge output, path escape, failed startup and interrupted transfer. Verify host synthetic markers remain unchanged and no external route is available. Only then seek the independent review of actual code/configuration.
7. Pin and preserve the exact candidate, grader, runtime and protocol identities. Count crashes, truncations, invalid reports and unobserved cases in the denominators. A sandbox can contain execution while the scoring protocol remains invalid; both need evidence.

The current host historically showed little commit headroom. Those samples are not current clearance. Do not start a VM beside a resident model merely because physical RAM looks free; plan inference and grading in separate admitted windows if needed. The feature may be absent, and lightweight feature activation is not assumed.

## Acceptance before any generated candidate runs

- A read-only prerequisites/capacity check and an explicit staged configuration exist.
- Actual containment, guest/wrapper separation, bounded IPC, host parsing/judging and cleanup are implemented and independently reviewed on handwritten fixtures.
- Expected-value leakage/spoofing and process-death tests are included.
- The normal host has no generated-code execution path.
- The scoped run is separately coordinated, with recoverable baseline and no competing model/VM.

No claim is made that the existing grader already meets these requirements. Blinded human inspection of draft text can continue while this remains unresolved; it must not be called an automated semantic pass.
