# Handoff surface status

This document records the current handoff-first surface that now exists inside PatchOps.

## Current shipped surface

Patch 60A adds a Python-owned human-readable handoff writer in:

- `patchops/handoff.py`

It can write:

- `handoff/current_handoff.md`

from a `WorkflowResult` without moving handoff logic into PowerShell.

## Why this shape is narrow

The previous Patch 60 attempt failed because it tried to force a brittle direct rewrite into `patchops/cli.py`.

This repair keeps the scope narrower:

- add the human-readable handoff generator itself,
- add tests that prove the output shape,
- add one small doc for current handoff status,
- do not widen into CLI/export automation yet.

## What comes later

Later handoff patches can build on this safely:

- machine-readable handoff JSON,
- latest-report indexing,
- richer next-action recommendation,
- `export-handoff` CLI support,
- a thin PowerShell handoff launcher,
- generated next-prompt output.

That keeps the redesign additive and patch-by-patch.