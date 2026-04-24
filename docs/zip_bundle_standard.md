# Zip bundle standard

The maintained zip bundle process is:

- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

Always continue patch by patch from evidence.

## Maintained bundle tree

- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`
- `content/`

## Launcher standard

- `run_with_patchops.ps1`
- one root-level launcher is enough
- do not manually unzip in the maintained flow
- use metadata-driven mode through `bundle_mode`
- the compatibility shim remains documented only as a historical compatibility shim, not the maintained authoring path.
- the compatibility shim also guards against stray leading `/` or `\` characters in pasted or generated command surfaces.
- `create_starter_bundle` and `emit_root_bundle_launcher` are the maintained emission surfaces
- do not hand-author the saved root launcher unless you are deliberately repairing it
- use a top-level `param(...)` script-file form for the saved launcher
- keep inline `& { ... }` wrapping only for inline or paste-safe scenarios

## Authoring note

Generate the bundle from Python when possible.

## Proof note

Patch 12 onward the process is proven self-hosted.

<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:STANDARD:START -->
## Patch G1 - bundle standard wording contract

This section locks the current bundle documentation wording without redesigning the bundle system.

- `manifest`, `profile`, `report`, and `project packet` are distinct PatchOps concepts.
- The `bundle transport` is the zip or folder package that carries the manifest, metadata, launcher, and content.
- The historical `manual unzip` stage remains documented for older PatchOps and old delivered bundles.
- For the maintained raw-zip path, do not manually unzip before the normal command; use `py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"`.
- A normal delivery is one patch zip.
- Archive the bundle root contents directly.
- Do not add an extra duplicate parent folder.
- `run_with_patchops.ps1` is the maintained saved root launcher.
- One root-level launcher is enough.
- `bundle_mode` in metadata owns apply, verify, and proof mode selection.
- The legacy `launchers/` folder can still appear in examples or compatibility material, but the maintained root launcher is `run_with_patchops.ps1`.
- Every normal run must end in one canonical Desktop txt report.
- `bundle-doctor` is the preferred troubleshooting entrypoint for shape validation and build verification.
- Maintained command order: `make-bundle`, `check-bundle`, `inspect-bundle`, `plan-bundle`, `bundle-doctor`, `build-bundle`, `run-package`.
- After every run, continue patch by patch from evidence.
- Patch 12 onward the process is proven self-hosted.
<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:STANDARD:END -->
