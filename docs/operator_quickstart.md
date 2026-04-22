# Operator Quickstart

## Final maintenance-mode quickstart

This file is the fastest maintained reading surface for the current operator flow.
Patch 12 onward no longer requires ad hoc launcher authoring or manual zip guesswork.
Use `C:\dev\patchops` as the maintained wrapper root in the normal examples.
This is the default maintained workflow.
Continue patch by patch from evidence.

## Normal bundle flow

Use this maintained sequence:

1. `make-bundle`
2. `check-bundle`
3. `inspect-bundle`
4. `plan-bundle`
5. `bundle-doctor`
6. `build-bundle`
7. `run-package`

The normal bundle-entry path is:

```powershell
py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
```

This path should end with one canonical Desktop txt report as the final evidence artifact.

## Bundle shape reminders

- `run_with_patchops.ps1` is the maintained saved launcher name
- one root-level launcher is enough
- `bundle_mode` lives in metadata
- do not manually unzip
- keep PowerShell thin and operator-facing
- keep reusable mechanics in Python

## Repair and recovery entrypoints

Direct module recovery surface: `patchops.bootstrap_repair`
CLI recovery surface: `patchops.cli bootstrap-repair`

`bundle-doctor` is the preferred troubleshooting entrypoint for bundle shape validation and build verification before a final run-package invocation.

## Operator-script surfaces

Use `emit-operator-script` when the operator needs a repo-owned PowerShell helper instead of a hand-written launcher.

Current maintained emitted surfaces:
- `run-package-zip`
- `maintenance-gate`

Useful related maintained surfaces:
- `patchops.bootstrap_repair`
- `bootstrap-repair`
- `Push-PatchOpsToGitHub.ps1`

Reading anchors for the current operator flow:
- `docs/root_launcher_shape_contract.md`
- `docs/post_publish_snapshot.md`

Return to the normal `check` / `inspect` / `plan` / `apply` / `verify` flow after the operator-only or recovery surface is no longer needed.
