# Handoff surface status

This document records the current handoff-first surface that exists inside PatchOps.

## Current shipped surface

Patch 60A added the Python-owned human-readable handoff writer in:

- `patchops/handoff.py`

That shipped the ability to write:

- `handoff/current_handoff.md`

Patch 61 extended the same Python-owned handoff surface so it can also write:

- `handoff/current_handoff.json`

Patch 62 extended the same additive handoff surface again so it can now also write:

- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`

Patch 63 makes the handoff surface recommend the next move instead of only restating the last run.

That means the handoff surfaces now carry actionable guidance for:

- `new_patch`
- `repair_patch`
- `verify_only`
- `wrapper_only_retry`
- `manual_review`

## Why this shape stays narrow

This patch remains additive.

It does not add CLI export yet.
It strengthens the Python-owned recommendation logic inside the existing handoff module so later export surfaces can reuse it.

## What the recommender now does

The handoff logic now uses existing PatchOps distinctions to recommend the narrowest trustworthy next step.

It considers:

- pass versus fail
- target-project failure versus wrapper failure
- whether expected target files exist
- whether a narrow rerun is still trustworthy
- when escalation to manual review is required

## What comes later

Later handoff patches can build on this safely:

- `export-handoff` CLI support
- a thin PowerShell handoff launcher
- generated `handoff/next_prompt.txt`

That keeps the redesign additive, Python-owned, and patch-by-patch.