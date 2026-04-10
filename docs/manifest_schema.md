# Manifest schema

## Purpose

The manifest is the execution contract for a PatchOps run.
It describes what files will be written, what validations will run, and how the report should be produced.

## Core review loop

For manifest-driven work, the safe review sequence remains:

- `check`
- `inspect`
- `plan`

Only after that should a normal flow continue to `apply` or `verify`.

## Important manifest areas

### File staging
Each file entry should resolve to a target-relative `path` and a `content_path` inside the patch bundle or patch content tree.

### Validation commands
Validation commands should be explicit, narrow, and truthful.
Use them to prove the touched layer first, then keep the broader regression set healthy.

### Report preferences
Report preferences should still preserve one canonical Desktop txt report per run.

### Backup and write behavior
PatchOps remains responsible for deterministic writing, backup recording, and report evidence of what changed.

### Tags and notes
Tags and notes are useful for operator context, but they do not replace manifests, reports, or tests.

## Practical rules

- Keep manifests narrow.
- Prefer additive maintenance work over redesign.
- Keep PowerShell out of reusable workflow logic.
- Let Python-owned surfaces do the heavy lifting.
- Treat `check`, `inspect`, and `plan` as the first trust-building layer.

## Bundle relation

A zip bundle is the carrier.
The manifest remains the execution contract inside that bundle.
