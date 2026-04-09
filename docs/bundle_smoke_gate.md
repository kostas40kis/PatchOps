# Post-build bundle smoke gate

This document defines the maintained post-build bundle smoke gate for PatchOps bundles.

## Purpose

A bundle is not treated as shippable immediately after `build-bundle` succeeds.
The built zip should also survive the modern zip review surfaces before operators or LLMs rely on it.

## Maintained smoke sequence

1. Generate or update the bundle root.
2. Run `bundle-doctor` on the bundle root.
3. Build the zip with `build-bundle`.
4. Review the built zip with `inspect-bundle`.
5. Review the built zip with `plan-bundle`.
6. Only then treat the built zip as shippable.

## Why this exists

This catches authoring drift that can hide between:
- a healthy bundle root
- a successful deterministic zip export
- the real post-build zip review path

It also keeps the release gate honest across both worlds:
- classic manifest review surfaces
- bundle review/build surfaces

## Operator rule

For bundle roots:
- use `bundle-doctor`
- use `check-bundle`

For built zips:
- use `inspect-bundle`
- use `plan-bundle`

Do not treat raw `check-bundle` against a built zip as the maintained smoke gate for shippable proof bundles.

## Evidence rule

Read the canonical report, continue patch by patch from evidence, and do not claim the bundle is ready if the post-build smoke gate is still red.
