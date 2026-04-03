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

Patch 64 added the first CLI export surface:

- `py -m patchops.cli export-handoff`

That command generates the stable handoff files and a compact bundle directory under:

- `handoff/bundle/current`

Patch 65 added the thin PowerShell launcher:

- `powershell/Invoke-PatchHandoff.ps1`

It stays thin and simply calls the Python export surface, captures stdout/stderr reliably, writes one Desktop txt report, and opens that report for the operator.

Patch 66 added the generated next-prompt surface:

- `handoff/next_prompt.txt`

That means the handoff export now produces both the state bundle and the ready-to-paste takeover prompt.

Patch 67 turns `docs/llm_usage.md` into a real start page.

It now tells future LLMs to begin with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

instead of reconstructing repo state from scattered docs.

## Why this shape stays narrow

This patch remains additive.

It does not change the export machinery.
It changes the orientation document so the repo has one obvious first file for future LLMs.

## Current operator flow

The intended operator flow is now one sentence:

- run handoff export, upload the bundle, paste the generated prompt

## What comes later

Later handoff patches can build on this safely:

- broader handoff bundle tests and drift coverage
- final handoff-first documentation refresh

That keeps the redesign additive, Python-owned, and patch-by-patch.