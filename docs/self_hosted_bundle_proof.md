# Self hosted bundle proof

## Purpose

This file records the maintained self-hosted bundle proof expectations for PatchOps.
The bundle authoring path should be able to prove itself without ad hoc launcher guesswork.

## Proof expectations

- the authoring flow is self-hosted
- `run_with_patchops.ps1` remains the saved root launcher
- the launcher stays thin and operator-facing
- `bundle_mode` stays in metadata
- bundle content lives under `content/`
- the final operator path ends in one canonical Desktop txt report

## Proof surfaces

- `patchops/bundles/authoring.py`
- `patchops/bundles/launcher_emitter.py`
- `create_starter_bundle`
- `emit_root_bundle_launcher`
- `build-bundle`
- `run-package`

## Proof posture

Use this proof to keep the self-hosted story truthful.
Continue patch by patch from evidence.
