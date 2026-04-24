# Self-hosted bundle proof

## Purpose

This note records the maintained self-hosted bundle proof for PatchOps acting as its own current target.
The proof is maintenance-facing and additive.
Do **not** redesign PatchOps.

## What the proof demonstrates

The self-hosted bundle authoring workflow for the PatchOps target should remain mechanically usable:

1. create a proof bundle for the PatchOps target
2. run `bundle-doctor` against the bundle root
3. build the zip
4. run `inspect-bundle` against the built zip
5. confirm the launcher status is `safe`
6. keep one canonical Desktop txt report
7. continue patch by patch from evidence

## Maintained expectations

- target project remains `patchops`
- target project root remains `C:/dev/patchops`
- `bundle-doctor` returns JSON and `ok: true` for a valid proof bundle
- `inspect-bundle` returns JSON and `ok: true` for a valid built proof bundle
- `launcher_status` should be `safe`
- `launcher_issue_count` should be `0`

## Bundle proof posture

Keep PowerShell thin.
Keep reusable mechanics in Python.
Treat the self-hosted proof as a conservative trust proof for the maintained bundle flow, not as permission to widen scope.
