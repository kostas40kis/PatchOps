# Bundle authoring template

## Purpose

This template is the maintained authoring checklist for a new PatchOps bundle.

## Exact files to create

- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`
- `content/`

## Authoring checklist

1. Generate the bundle from Python when possible.
2. Stage target-relative files under `content/`.
3. Fill `manifest.json` writes and validation commands.
4. Keep `bundle_meta.json` aligned with the bundle root.
5. Keep `run_with_patchops.ps1` as the single saved root launcher.
6. Run `check-bundle`, `inspect-bundle`, `plan-bundle`, and `bundle-doctor`.
7. Build the zip.
8. Run the built zip through `run-package`.
9. Continue from the canonical Desktop txt report.

## Launcher guidance

The saved root launcher should stay boring.
It should remain a compatibility shim that delegates to `bundle-entry`.
Do not widen it into a second workflow engine.
