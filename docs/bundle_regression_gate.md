# Bundle regression gate

## Purpose

This release gate keeps the regression matrix visible in the maintained release story.
It must keep both worlds visible at the same time:
- classic manifest review surfaces
- bundle review/build surfaces

## Regression matrix

### Classic manifest review surfaces
- `check`
- `inspect`
- `plan`

### Bundle review/build surfaces
- `bundle-doctor`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `build-bundle`

## Gate posture

This is a release gate for the maintained workflow, not a redesign note.
Keep PowerShell thin and operator-facing.
Keep reusable mechanics in Python.
continue patch by patch from evidence

## Expected outcome

A shippable repo keeps the classic manifest review surfaces and the bundle review/build surfaces aligned instead of letting one drift from the other.
