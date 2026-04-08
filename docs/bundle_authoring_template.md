# PatchOps bundle authoring template

Use this checklist for every maintained bundle.

## Start from Python

- `py -m patchops.cli make-bundle <bundle-root> --mode apply`
- `py -m patchops.cli make-bundle <bundle-root> --mode verify`

## Fill the bundle

1. Put target-relative staged files under `content/`.
2. Add matching `files_to_write` entries in `manifest.json`.
3. Keep one root-level `run_with_patchops.ps1`.
4. Set `bundle_mode` in `bundle_meta.json` instead of inventing extra launcher variants.

## Diagnose before zipping

- `py -m patchops.cli bundle-doctor <bundle-root>`
- `py -m patchops.cli check-bundle <bundle-root>`

`bundle-doctor` is the preferred troubleshooting entrypoint because it covers shape validation, launcher-risk review, and build verification before bundle export.

## Build and run

- `py -m patchops.cli build-bundle <bundle-root> --output <zip>`
- `py -m patchops.cli run-package <zip> --wrapper-root C:\dev\patchops`

## Maintained example bundles

- `examples/bundles/generic_apply_bundle`
- `examples/bundles/generic_verify_bundle`

These examples are the maintained defaults for operators and future LLMs.
