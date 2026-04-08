# PatchOps zip bundle standard

The maintained bundle workflow now uses one canonical root layout and one canonical root launcher.

## Canonical layout

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

## Maintained workflow

1. `py -m patchops.cli make-bundle <bundle-root> --mode apply|verify|proof`
2. Edit `manifest.json`, `bundle_meta.json`, and staged files under `content/`.
3. `py -m patchops.cli bundle-doctor <bundle-root>`
4. `py -m patchops.cli build-bundle <bundle-root> --output <zip>`
5. `py -m patchops.cli run-package <zip> --wrapper-root C:\dev\patchops`

`bundle-doctor` is the preferred troubleshooting entrypoint for bundle authoring problems because it combines shape validation, launcher-risk review, and build verification in one Python-owned check before you build or run the zip.

## Maintained examples

The maintained examples now live under:

- `examples/bundles/generic_apply_bundle`
- `examples/bundles/generic_verify_bundle`

Both examples keep:

- one root-level `run_with_patchops.ps1`
- metadata-driven mode selection through `bundle_mode`
- staged content under `content/`
- a bundle shape that passes self-check and deterministic zip export

Do not treat older multi-launcher layouts as the maintained default.
