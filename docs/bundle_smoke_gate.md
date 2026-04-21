# Bundle smoke gate

## Purpose

This post-build bundle smoke gate records the maintained smoke pass that a shippable bundle should clear before final operator use.

## Maintained surface split

Use these bundle surfaces in order:
- `bundle-doctor`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `build-bundle`

Do not treat raw `check-bundle` against a built zip as the maintained smoke gate.
The maintained smoke story is broader than one raw command because it must keep bundle shape, review, build, and final operator flow aligned.

## Gate posture

A shippable bundle should preserve one canonical Desktop txt report and should continue patch by patch from evidence.
Keep PowerShell thin and operator-facing.
Keep reusable mechanics in Python.
