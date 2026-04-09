# Operator script emitter

## Purpose
PatchOps can now emit maintained operator helper scripts from Python-owned templates so common helper actions do not drift back into ad hoc PowerShell.

## Supported script kinds
- `run-package-zip`
- `maintenance-gate`

## Why this exists
Recent real usage showed that one-off scripts can reintroduce old bugs such as stale command surfaces, quoting mistakes, and `ArgumentList` compatibility problems.

## Compatibility rule
Generated process-launch helpers must remain compatible with **Windows PowerShell 5.1**:
- use `ArgumentList` when that property exists on `ProcessStartInfo`
- otherwise fall back to the classic `Arguments` string

This rule is locked in the emitted script text and in tests.

## Examples
Emit a run-package helper script:

`py -m patchops.cli emit-operator-script run-package-zip C:\Users\Public\run_patch_bundle.ps1 --wrapper-root "C:\dev\patchops" --bundle-zip-path "D:\patch_bundle.zip"`

Emit a maintenance gate helper script:

`py -m patchops.cli emit-operator-script maintenance-gate C:\Users\Public\run_patchops_maintenance_gate.ps1 --wrapper-root "C:\dev\patchops"`

## Design rule
The emitted script is a thin operator-facing shim. The intelligence stays in Python and the generated script comes from one repo-owned template.
