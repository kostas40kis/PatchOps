# Handoff surface status

This document records the current handoff-first surface that exists inside PatchOps.

## Current shipped surface

Patch 60A added the Python-owned human-readable handoff writer in:

- `patchops/handoff.py`

That shipped the ability to write:

- `handoff/current_handoff.md`

Patch 61 extends the same Python-owned handoff surface so it can also write:

- `handoff/current_handoff.json`

## Why this shape stays narrow

This patch remains additive.

It does not force CLI export automation yet.
It adds the machine-readable handoff payload and writer beside the existing markdown writer so later patches can build on a stable base.

## What the JSON file is for

`handoff/current_handoff.json` is the machine-readable state artifact for future LLM transition.

It is intended to carry deterministic fields such as:

- current stage
- latest patch info
- latest report path
- failure classification
- next recommended mode
- next action
- required reading

## What comes later

Later handoff patches can build on this safely:

- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- richer recommendation logic
- `export-handoff` CLI support
- a thin PowerShell handoff launcher
- generated `handoff/next_prompt.txt`

That keeps the redesign additive, Python-owned, and patch-by-patch.