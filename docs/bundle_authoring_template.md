# Bundle authoring template

## Purpose

This template is the maintained authoring checklist for a new PatchOps bundle.
Use it to keep the bundle shape, launcher shape, and command order aligned with the current live repo.

## Maintained authoring posture

- copy the maintained example bundle
- one folder is enough
- one root-level PowerShell file is enough
- one canonical Desktop txt report is enough
- use the saved root launcher name `run_with_patchops.ps1`
- keep `bundle_mode` in metadata
- do not manually unzip during the normal operator path
- older PatchOps flows often relied on a manual unzip stage
- the current maintained flow avoids that manual unzip stage
- preserve a thin launcher
- avoid an extra duplicate parent folder when packaging
- archive the bundle root contents directly
- continue patch by patch from evidence
- Generate the bundle from Python when possible.

## Maintained bundle tree

```text
example_bundle/
  bundle_meta.json
  manifest.json
  run_with_patchops.ps1
  content/
```

## Maintained command order

- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

## Launcher notes

The maintained root launcher is `run_with_patchops.ps1`.
One root-level PowerShell file is enough.
The launcher stays thin and operator-facing.
The normal run path reaches PatchOps through the bundle-entry / run-package path rather than hand-authored unzip logic.

## Normal run command

```powershell
py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
```

The maintained bundle uses a single saved root launcher.

## Troubleshooting entrypoint

`bundle-doctor` is the preferred troubleshooting entrypoint when a bundle root or built zip does not behave as expected.

Use it before rerunning broader workflows so you can separate:
- shape validation
- build verification

Treat `bundle-doctor` as the fastest maintained way to confirm whether the bundle shape, saved launcher family, and buildable export all still match the current PatchOps contract.
