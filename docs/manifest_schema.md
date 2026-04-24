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

## Current manifest rules

Current manifest guidance should reflect the shipped runtime rules:

- `content_path` is authored relative to the wrapper project root
- manifest-local resolution is compatibility fallback, not the primary contract
- `allowed_exit_codes` belongs on validation commands when nonzero success is expected
- classify failures honestly as:
  - `target_project_failure`
  - `wrapper_failure`
  - `patch_authoring_failure`
- Prefer explicit examples over inferred path rules.

## Example references

Current manifest guidance should point to real shipped examples:

- `examples/generic_allowed_exit_patch.json`
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_content_path_patch.json`

For `files_to_write` entries, use wrapper-relative paths from the wrapper project root for `content_path`.
- `allowed_exit_codes` is shown in `generic_allowed_exit_patch.json`.
- Command-group examples are shown in `generic_smoke_audit_patch.json`.
- `files_to_write entries` using `content_path` should be authored as wrapper-relative paths from the wrapper project root.
- The runtime falls back to manifest-local resolution only as compatibility behavior, not as the primary rule.
- For `files_to_write entries`, use wrapper-relative paths from the wrapper project root for `content_path`.
- `examples/generic_cleanup_archive_patch.json` extends the command-group examples for cleanup/archive flows.
- Manifest-local resolution remains a compatibility fallback rather than the primary contract.
