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

Patch 63 made the handoff surface recommend the next move instead of only restating the last run.

Patch 64 adds the first CLI export surface:

- `py -m patchops.cli export-handoff`

That command now generates the stable handoff files and a compact bundle directory under:

- `handoff/bundle/current`

## Why this shape stays narrow

This patch remains additive.

It does not move handoff logic into PowerShell.
It adds one Python-owned CLI export surface on top of the existing Python-owned handoff module.

## What export-handoff now does

Given a canonical PatchOps report, the command generates:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`

and then copies them into a compact bundle directory:

- `handoff/bundle/current`

This means one command can now prepare the current takeover package.

## Current operator shape

Use:

- `py -m patchops.cli export-handoff --report-path <path-to-latest-report>`

or, after a prior export already exists:

- `py -m patchops.cli export-handoff`

if `handoff/latest_report_copy.txt` is already present.

## What comes later

Later handoff patches can build on this safely:

- thin PowerShell launcher for handoff export
- generated `handoff/next_prompt.txt`
- lighter `docs/llm_usage.md`
- stronger handoff bundle tests and final handoff-first doc refresh

That keeps the redesign additive, Python-owned, and patch-by-patch.