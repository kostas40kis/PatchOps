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

## Internal execution path note

For internal command execution, PatchOps should prefer the Python-owned execution path instead of reintroducing ad hoc subprocess loops inside individual workflow files or PowerShell patch bodies.

The preferred internal path is:

- `patchops.execution.process_runner.run_command_result(...)` for direct execution,
- `patchops.execution.result_model.normalize_execution_result(...)` for reusable normalization,
- `ExecutionResult` as the reusable internal result shape,
- and the shared workflow adapter in `patchops.workflows.common` instead of workflow-local subprocess handling.

Contributors should treat `patchops.execution.process_runner` and `patchops.execution.result_model` as the maintained execution surfaces and avoid adding new ad hoc execution helpers in docs examples, workflow files, or one-off PowerShell runners unless current repo evidence proves a narrow exception is required.
