# Zip bundle standard

## Purpose

This file describes the maintained PatchOps zip bundle shape for the current live repo.
A bundle is **bundle transport**, not a replacement for the manifest, profile, report, or project packet concepts.
Keep the wrapper / target / project packet boundaries explicit.

## Core distinction

- the **manifest** is the execution contract
- the **profile** selects wrapper behavior
- the **report** is the final evidence artifact
- the zip bundle is transport around those maintained surfaces
- the project packet remains a separate maintained surface from bundle transport

## Maintained root shape

Archive the bundle root contents directly.
Do not add an extra duplicate parent folder.
Do not depend on a manual unzip stage.
Do not require a manual unzip guess.

Maintained bundle root:

```text
example_bundle/
  bundle_meta.json
  manifest.json
  run_with_patchops.ps1
  content/
  launchers/
```

`run_with_patchops.ps1` is the one maintained root launcher.
One root-level launcher is enough.
One canonical Desktop txt report is enough.

## Command sequence

Use the maintained sequence:

- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

Continue patch by patch from evidence.
In lower-case contract wording: continue patch by patch from evidence.

## Launcher and compatibility notes

The saved root launcher is a thin launcher and a compatibility shim.
Keep reusable mechanics in Python.
Keep PowerShell thin and operator-facing.
The launcher should preserve the normal bundle-entry path and end with one canonical Desktop txt report.

## Bundle doctor posture

`bundle-doctor` is the preferred troubleshooting entrypoint for shape validation and build verification before `run-package`.

## Path hygiene

Reject malformed bundle shapes early.
Be careful with stray leading `/` or `\` characters in path inputs.
Avoid stale assumptions about older PatchOps launcher layouts.

## Maintained run example

```powershell
py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
```

That normal bundle-entry path should end with one canonical Desktop txt report.

Patch 12 onward this standardized bundle flow is treated as proven self-hosted.

