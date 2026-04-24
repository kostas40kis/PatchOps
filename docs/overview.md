# Overview

PatchOps is a standalone wrapper and evidence system.

## Process execution note

The preferred internal path is:
- run_command_result
- normalize_execution_result
- ExecutionResult
- patchops.execution.process_runner
- patchops.execution.result_model

Avoid ad hoc subprocess loops and PowerShell patch bodies for reusable mechanics.

## Current modular package layout

The current shipped repo is modular rather than flattened.

Key maintained modules include:
- `patchops/reporting/`
- `patchops/bundles/`
- `patchops/workflows/`

Treat `patchops/cli.py` as the facade, not the whole product surface.
- `run-package` is the maintained bundle execution surface.
- `bundle-doctor`, `build-bundle`, `make-bundle`, and `make-proof-bundle` are current bundle-support surfaces.
- `check-bundle` and `inspect-bundle` are current bundle inspection surfaces.
- `plan-bundle` is the current bundle planning surface.
- The docs should describe the modular package layout rather than stale flat-file assumptions.
- `bootstrap repair` remains a narrow recovery surface rather than a second workflow engine.
- GitHub publish remains a maintained operator/support surface after the core proof frontier is green.
- The canonical root launcher shape contract remains a maintained reference surface for bundle and emitted launcher work.
