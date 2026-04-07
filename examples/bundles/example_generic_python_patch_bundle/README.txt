PatchOps example generic Python patch bundle
==========================================

Purpose
-------
This maintained example shows the bundle shape to copy now that the native zip path is real.

How to use the example as a template
------------------------------------
1. Prefer generating a new starter bundle with `create_starter_bundle(...)` when you want the maintained Python-owned starting point.
2. Or copy this folder when a concrete bundle shape is more useful.
3. Rename it for your real patch.
4. Replace the manifest, metadata, README, staged content, and root launcher details.
5. Export the delivered zip from the bundle root contents directly.

Operator flow for the current stage
-----------------------------------
- receive one zip
- do **not** manually unzip the delivered `.zip`
- run `py -m patchops.cli run-package "<bundle.zip>" --wrapper-root "C:\dev\patchops"`
- let PatchOps extract the bundle and call the bundled launcher
- read the one canonical Desktop txt report first

Authoring posture
-----------------
- keep launchers thin
- prefer Python-owned launcher generation or normalization
- prefer preflight review before trusting a bundle
- keep classic manifest-driven PatchOps flows intact
