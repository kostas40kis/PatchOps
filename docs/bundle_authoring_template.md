# Bundle authoring template

Use this workflow for normal maintained PatchOps bundles.

## Operator workflow
1. Create a starter bundle with `py -m patchops.cli make-bundle ...`.
2. Fill in `manifest.json`, `bundle_meta.json`, and `content/`.
3. Run `py -m patchops.cli check-bundle <bundle-root>`.
4. Run `py -m patchops.cli inspect-bundle <bundle-root>`.
5. Run `py -m patchops.cli plan-bundle <bundle-root>`.
6. Run `py -m patchops.cli bundle-doctor <bundle-root>` as the preferred troubleshooting entrypoint.
7. Build the zip with `py -m patchops.cli build-bundle <bundle-root> <bundle.zip>`.
8. Execute the zip with `py -m patchops.cli run-package <bundle.zip> --wrapper-root "C:\dev\patchops"`.
9. Upload the canonical Desktop txt report and continue patch by patch from evidence.

## Why bundle-doctor comes first for diagnosis
`bundle-doctor` is the preferred troubleshooting entrypoint because it combines shape validation, launcher review, and build verification in one place before you spend time rerunning a broken zip.

## What to keep true
- One root-level `run_with_patchops.ps1`.
- One canonical report.
- PowerShell stays thin and operator-facing.
- Reusable behavior stays in Python.
- Do not guess bundle layout by hand.
