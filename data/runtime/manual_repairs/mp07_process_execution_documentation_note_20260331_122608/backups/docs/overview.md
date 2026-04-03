# PatchOps Overview

PatchOps is a reusable harness for applying, validating, and evidencing patches across repositories.

## Core boundary

Target repositories own:

- architecture
- business logic
- tests
- policies
- domain semantics

PatchOps owns:

- manifest-driven execution
- profile resolution
- backup mechanics
- deterministic file writing
- validation command execution
- stdout/stderr capture
- deterministic report rendering
- failure classification
- verify-only reruns

## Stage 1 architecture

Python core:

- `patchops/manifest_loader.py` and `patchops/manifest_validator.py`
- `patchops/profiles/`
- `patchops/files/`
- `patchops/execution/`
- `patchops/reporting/`
- `patchops/workflows/`

Thin PowerShell surface:

- `powershell/Invoke-PatchManifest.ps1`
- `powershell/Invoke-PatchVerify.ps1`

## Stage 1 objective

Produce a first useful version that can:

1. load a manifest
2. resolve a profile
3. back up affected files
4. write files
5. run validation commands
6. capture stdout/stderr
7. emit one canonical report
8. distinguish wrapper failure from target-project failure
9. support verify-only reruns
