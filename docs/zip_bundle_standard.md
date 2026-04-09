# PatchOps zip bundle standard

The maintained bundle workflow now uses one canonical root layout and one canonical saved launcher.

## Canonical flow
1. Scaffold a bundle from Python with `py -m patchops.cli make-bundle ...`.
2. Edit `manifest.json`, `bundle_meta.json`, and the files under `content/`.
3. Run `py -m patchops.cli bundle-doctor <bundle-root>` as the preferred troubleshooting entrypoint.
4. Build the zip with `py -m patchops.cli build-bundle <bundle-root> <bundle.zip>`.
5. Run the zip with `py -m patchops.cli run-package <bundle.zip> --wrapper-root "C:\dev\patchops"`.
6. Read one canonical Desktop txt report and continue patch by patch from evidence.

## Canonical tree
```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

## Launcher rule
- `run_with_patchops.ps1` is the only maintained saved launcher.
- The saved launcher is a thin compatibility shim.
- Apply versus verify selection is metadata-driven.
- Do not hand-author multiple launcher variants for the normal maintained path.

## Review surfaces
- `check-bundle` validates the bundle contract.
- `inspect-bundle` previews the resolved bundle information.
- `plan-bundle` previews write targets without writing.
- `bundle-doctor` is the preferred troubleshooting entrypoint because it combines shape validation, launcher review, and build verification.

## Default maintained workflow from Patch 12 onward
The standardized bundle process is now proven self-hosted:
- scaffold from Python,
- diagnose with bundle checks,
- build the zip from Python,
- run the zip through `run-package`,
- read one canonical report.
