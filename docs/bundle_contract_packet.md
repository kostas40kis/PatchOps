# PatchOps bundle contract packet

This is the maintained LLM-facing packet for authoring a correct PatchOps bundle.
A fresh LLM should be able to author a correct bundle using only this packet.

## Exact bundle tree

```text
good_example_bundle/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
```

The exact bundle tree must keep `manifest.json`, `bundle_meta.json`, `README.txt`, `run_with_patchops.ps1`, and `content/` visible.

## Exact launcher rule

Use one single saved root launcher named `run_with_patchops.ps1`.
The launcher must use top-level `param(...)` script-file form.
Do not hand-author the saved root launcher; emit it from Python.
The maintained operator flow reaches PatchOps through the `bundle-entry` / `run-package` path.

## Exact metadata fields

`schema_version`
`patch_name`
`bundle_mode`
`recommended_profile`
`target_project`
`target_project_root`
`manifest_path`
`content_root`
`launcher_path`

One good example of metadata is:

```json
{
  "schema_version": 1,
  "patch_name": "demo_bundle",
  "bundle_mode": "apply",
  "recommended_profile": "generic_python",
  "target_project": "patchops",
  "target_project_root": "C:/dev/patchops",
  "manifest_path": "manifest.json",
  "content_root": "content",
  "launcher_path": "run_with_patchops.ps1"
}
```

## Commands

- `make-bundle`
- `make-proof-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

## What not to do

- Do not create multiple launcher variants.
- Do not manually invent zip layout by hand.
- Do not skip `bundle-doctor`.

## One good example

```text
good_example_bundle/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
```

The good example keeps the root launcher single and keeps `"launcher_path": "run_with_patchops.ps1"` in metadata.

## One bad example

```text
bad_example_bundle/
  manifest.json
  bundle_meta.json
  apply_with_patchops.ps1
  verify_with_patchops.ps1
  content/
```

The bad example is wrong because `apply_with_patchops.ps1` and `verify_with_patchops.ps1` create multiple launcher variants.

## Guardrails

Reject bundle trees with stray leading `/` or `\` characters before the operator reaches run-package.
Keep PowerShell thin.
Keep reusable mechanics in Python.
Keep one canonical Desktop txt report.
Command/doc alignment proof should keep the packet and the shipped commands in sync.

continue patch by patch from evidence

