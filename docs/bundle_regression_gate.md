# Bundle and manifest regression gate

This document defines a maintained release gate for PatchOps after the canonical bundle workflow landed.

## Goal

Keep both worlds healthy at the same time:

- classic manifest review surfaces
- bundle review/build surfaces

Do not let release checks drift toward only one workflow.

## Regression matrix

For generated proof bundles, the release gate should exercise:

- `check`
- `inspect`
- `plan`

and also:

- `bundle-doctor`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `build-bundle`

## Built zip posture

Use the bundle root for `bundle-doctor` and `check-bundle`.
Use the built zip for `inspect-bundle` and `plan-bundle`.

That keeps the gate aligned with the maintained canonical single-launcher bundle model instead of older zip-shape expectations.

## Why this exists

PatchOps now supports a standardized zip-first workflow, but the classic manifest path still remains part of the maintained surface. The regression matrix exists so both paths stay green together.

## Operator guidance

- Generate a proof bundle from Python-owned helpers.
- Review the bundle through the maintained bundle surfaces.
- Review the manifest through the maintained manifest surfaces.
- continue patch by patch from evidence
- Treat this as a release gate, not an optional smoke check.
