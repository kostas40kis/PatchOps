# PatchOps

PatchOps is a project-agnostic patch execution harness for Windows-first patch workflows.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## Current status

PatchOps has completed its initial buildout circle and should now be treated as a maintained reusable utility.

The core wrapper surface exists, the main workflows exist, the example surface exists, and the test suite is green.
The remaining job is maintenance-mode discipline: keep docs, examples, and traceability guidance aligned with the real repo state.