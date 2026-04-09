# Maintenance gate

This document defines the maintained combined health gate for PatchOps.

## Purpose

Use one command when you need the current answer to:

> Is PatchOps healthy enough to trust today?

The combined gate keeps three already-shipped surfaces together:

- the bundle and manifest regression gate
- the post-build bundle smoke gate
- the bundle-aware `release-readiness` surface

## Maintained command

`py -m patchops.cli maintenance-gate`

Use `--core-tests-green` only when the green core-test state was already proven externally.

## What it runs

1. `tests/test_bundle_manifest_regression_gate_current.py`
2. `tests/test_bundle_post_build_smoke_gate_current.py`
3. the existing `release-readiness` logic

## Output shape

The command returns stable JSON and can also write a deterministic text artifact through `--report-path`.

## Rules

- this command does not replace the separate surfaces
- this command is the maintained combined entrypoint
- continue patch by patch from evidence
- keep PowerShell thin and keep the reusable gate logic in Python
