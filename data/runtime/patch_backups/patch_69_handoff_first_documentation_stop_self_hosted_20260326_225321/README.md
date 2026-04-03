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

## Consolidation status

PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture.
The initial buildout circle is complete enough that the repo should be treated as a maintained utility rather than an open-ended experiment.

## Current status

The core wrapper surface exists, the main workflows exist, the example surface exists, and the test suite is expected to stay green.
The remaining work is maintenance-mode discipline: keep docs, examples, and traceability guidance aligned with the real repo state.

## Profile matrix

Supported profile surface includes:

- `trader`
- `generic_python`
- `generic_python_powershell`

Generic Python + PowerShell profile examples are bundled so the wrapper is visibly not trader-locked.

## What PatchOps is

PatchOps is the wrapper layer that owns how patches are applied, validated, and evidenced.

Target repo = what changes  
PatchOps = how the change is applied, validated, and evidenced

That boundary remains non-negotiable.

## See also

- `docs/patch_ledger.md`
