# Handoff surface status

This document records the current handoff-first surface that exists inside PatchOps.

## Current shipped surface

Patch 60A added the Python-owned human-readable handoff writer in:

- `patchops/handoff.py`

That shipped the ability to write:

- `handoff/current_handoff.md`

Patch 61 extended the same Python-owned handoff surface so it can also write:

- `handoff/current_handoff.json`

Patch 62 extends the same additive handoff surface again so it can now also write:

- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`

## Why this shape stays narrow

This patch remains additive.

It does not force CLI export automation yet.
It adds stable latest-report preservation and indexing beside the existing handoff writers so later export patches can build on a deterministic base.

## What the latest-report files are for

`handoff/latest_report_copy.txt` preserves the text of the latest canonical report in a stable handoff location.

`handoff/latest_report_index.json` records where the latest canonical report came from and where the stable copy lives.

Together they remove manual report hunting for a future LLM or operator.

## What comes later

Later handoff patches can build on this safely:

- richer recommendation logic
- `export-handoff` CLI support
- a thin PowerShell handoff launcher
- generated `handoff/next_prompt.txt`

That keeps the redesign additive, Python-owned, and patch-by-patch.