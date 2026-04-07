# PatchOps Zip Bundle Standard

## Purpose

This document defines the standard bundle architecture for the zip-first PatchOps patch stream.

The goal is to standardize how a patch is packaged without changing the older PatchOps execution model.

PatchOps remains:
- the wrapper,
- the place where apply / verify / reporting logic lives,
- and the place where one canonical evidence report is produced.

The bundle is only the transport container.

---

## Canonical bundle shape

Every bundle in this stream should follow this root shape:

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

### Required rules

1. Exactly one patch zip is delivered for one patch.
2. `manifest.json` lives at the bundle root.
3. `bundle_meta.json` lives at the bundle root.
4. `README.txt` lives at the bundle root.
5. `run_with_patchops.ps1` lives at the bundle root.
6. All staged target content lives under `content/`.
7. One root-level launcher is enough.
8. One canonical Desktop txt report is enough for the normal apply path.
9. The launcher stays thin and must call PatchOps instead of manually copying files.
10. The bundle must remain self-describing enough for both an operator and a future CLI surface.

---

## Delivered archive layout rule

For delivered bundles in the manual-unzip stage, the zip should contain the **bundle root contents directly**.

That means the archive should open to:
- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`
- `content/`

It should **not** add a redundant second parent folder inside the zip.

The operator should be able to extract the zip once and land immediately at the usable bundle root.
This avoids the double-nested extraction confusion seen in earlier patch attempts.

---

## Required root files

### `manifest.json`
This is the real execution contract.
It tells PatchOps what to back up, what to write, and what to validate.

### `bundle_meta.json`
This is bundle-level metadata for transport and validation.
It should not replace the manifest.

### `README.txt`
This should tell the operator:
- what the patch is,
- where to unzip it,
- which launcher to run,
- which profile and roots it assumes,
- and that PatchOps should produce one canonical Desktop txt report.

### `run_with_patchops.ps1`
This is the single operator convenience surface for the manual-unzip stage.
It should be wrapped in `& { ... }`, keep strict mode enabled, and call PatchOps instead of manually copying files.

### `content/`
This holds staged target files in their target-relative paths.

---

## Launcher rules

The root launcher must:
- resolve the bundle root,
- call PatchOps with the bundle manifest,
- keep the normal `check -> inspect -> plan -> apply` review sequence when appropriate,
- avoid manual `Copy-Item` as the main path,
- avoid becoming a mini workflow engine,
- and avoid fragile JSON handoff or clever wrapper logic.

For normal patch delivery in this stage, one root-level launcher is enough.
A second bundled verify script is no longer required.
One canonical Desktop txt report is enough for the normal apply path.

---

## Current operator workflow for this stage

This document defines the standard for the **manual unzip stage**.

At this stage the operator workflow is:

1. receive one patch zip,
2. unzip it manually on the Desktop,
3. land at the bundle root without a duplicated parent folder,
4. run the included `run_with_patchops.ps1`,
5. let PatchOps execute the patch from the bundle manifest,
6. read the one canonical Desktop txt report.

Manual unzip is still expected at this stage.
Native zip intake is a later milestone.

---

## Backward-compatibility rule

This bundle standard is additive.

It must not break or replace:
- normal manifest-based apply,
- normal verify,
- normal check / inspect / plan,
- profiles,
- reporting,
- handoff flow,
- or existing PatchOps project-packet behavior.
## Additive alignment note for packet and transport terminology

This section exists to keep the maintained zip-bundle wording explicit without redesigning the earlier standard.

- The bundle is a **bundle transport** surface for delivery and operator execution convenience.
- It does not replace the manifest contract, the selected profile, the one canonical Desktop txt report, or the existing **project packet** surfaces.
- The standard launcher directory is literally `launchers/`, and bundled launchers remain thin operator convenience surfaces only.
- During the pre-native stage, the operator still performs **manual unzip** before running the packaged PowerShell launcher.
- After the native intake milestone is proven, PatchOps may consume the zip directly while still preserving the same report chain and manifest-owned execution truth.
