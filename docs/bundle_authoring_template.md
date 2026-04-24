# Bundle authoring template

Use this template for the maintained flow.

## Bundle tree

- manifest.json
- bundle_meta.json
- README.txt
- run_with_patchops.ps1
- content/

## bundle-entry

Use the root bundle-entry launcher contract through `run_with_patchops.ps1`.

The maintained flow ends in one canonical Desktop txt report.

Use a single saved root launcher for the maintained flow.

## Command order

1. `make-bundle`
2. `check-bundle`
3. `inspect-bundle`
4. `plan-bundle`
5. `bundle-doctor`
6. `build-bundle`
7. `run-package`

After each real run, continue patch by patch from evidence.

## Launcher template rules

- saved root launcher name: `run_with_patchops.ps1`
- one root-level launcher is enough
- use metadata-driven mode
- launcher emission comes from `create_starter_bundle` and `emit_root_bundle_launcher`
- do not hand-author the saved root launcher unless you are repairing it
- the saved launcher should use the top-level `param(...)` script-file form
- keep inline `& { ... }` wrapping where inline execution needs it

## Authoring note

Generate the bundle from Python when possible.

## Proof note

Patch 12 onward the process is proven self-hosted.

<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:TEMPLATE:START -->
## Patch G1 - authoring wording contract

This section preserves exact wording required by the maintained bundle-authoring tests.

- This is the historical manual unzip stage for older PatchOps and older patch zips.
- Copy the maintained example bundle before editing a new bundle by hand.
- The maintained example bundle lives under `examples/bundles/example_generic_python_patch_bundle/`.
- One folder is enough.
- One root-level PowerShell file is enough.
- One canonical Desktop txt report is enough.
- Use the thin launcher named `run_with_patchops.ps1`.
- Keep `run_with_patchops.ps1` as the saved root launcher.
- `bundle_mode` in `bundle_meta.json` owns mode selection.
- Do not manually unzip for the current raw-zip `run-package` path.
- When packaging manually, archive the bundle root contents directly.
- Do not create an extra duplicate parent folder.
- Avoid an extra duplicate parent folder because it makes the extracted root ambiguous.
- `bundle-doctor` is the preferred troubleshooting entrypoint for shape validation and build verification.
- Maintained command order: `make-bundle`, `check-bundle`, `inspect-bundle`, `plan-bundle`, `bundle-doctor`, `build-bundle`, `run-package`.
- After every run, continue patch by patch from evidence.
- Patch 12 onward the process is proven self-hosted.
<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:TEMPLATE:END -->
