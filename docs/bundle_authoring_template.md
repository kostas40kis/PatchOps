# PatchOps Bundle Authoring Template

## Purpose

This document explains how to author a new patch bundle under the simplified single-launcher delivery rule.

Patch 04 clarifies the flat archive export rule so one extract action lands at the usable bundle root.

This is still part of the **manual unzip stage**.
At this point the operator still:
1. receives one zip,
2. unzips it manually,
3. opens the extracted folder,
4. runs the included `run_with_patchops.ps1`,
5. and reads one canonical Desktop txt report written by PatchOps.

Native zip intake is a later milestone.
The older PatchOps `check`, `inspect`, `plan`, `apply`, and `verify` flows remain unchanged.

---

## Where the maintained example lives

Copy the maintained example bundle from:

```text
examples/bundles/example_generic_python_patch_bundle/
```

That example now reflects the root-level single-launcher rule.

---

## The required bundle shape

Every future bundle should follow this root shape:

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

One folder is enough.
One root-level PowerShell file is enough.
One canonical Desktop txt report is enough for the normal apply path.

---

## Archive/export rule

When creating the delivered zip, archive the bundle root contents directly.
Do not wrap the bundle in an extra duplicate parent folder inside the archive.

The operator should be able to unzip the delivered archive once and immediately see:
- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`
- `content/`

This keeps the manual-unzip stage simple and removes the earlier nested-folder confusion.

---

## Recommended authoring workflow

### Step 1 — copy the maintained example bundle

Copy the maintained example bundle and rename it for the new patch.

### Step 2 — prepare the root metadata files

Create or update:
- `manifest.json`
- `bundle_meta.json`
- `README.txt`
- `run_with_patchops.ps1`

At minimum, replace:
- patch name,
- target project,
- profile,
- target root,
- content file list,
- and validation commands.

### Step 3 — replace staged content under `content/`

Put the target files under `content/` using target-relative paths.

### Step 4 — keep the root launcher thin

The single launcher should remain boring.
It should:
- locate the bundle root,
- find `manifest.json`,
- call PatchOps,
- and let PatchOps own the real apply / reporting behavior.

It should not:
- manually copy files as the main path,
- become a mini workflow engine,
- or bypass one canonical report.

If a launcher is being generated from Python, it should be wrapped in `& { ... }` and formatted consistently.
This stream now treats the Python helper as the preferred way to format launcher text.

### Step 5 — export the zip without an extra parent layer

Zip the bundle root contents directly.
The extracted result should be one folder deep, not two copies of the patch name nested inside each other.

At this stage the operator still unzips it manually before running the launcher.

---

## What the maintained example should teach

The maintained example bundle should make these things obvious:
- what the root shape looks like,
- where staged content goes,
- how `content_path` references are written,
- what a thin launcher looks like,
- what the flat archive export rule looks like,
- and that one canonical Desktop txt report remains required.

---

## Acceptance rule for this stage

This stage is healthy when:
- the docs describe the manual unzip stage clearly,
- the docs describe the flat archive export rule clearly,
- the maintained example bundle uses one root-level launcher,
- and the tests lock those expectations.
