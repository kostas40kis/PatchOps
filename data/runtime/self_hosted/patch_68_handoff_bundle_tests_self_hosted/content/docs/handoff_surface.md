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

Patch 67 turned `docs/llm_usage.md` into the start page that points future LLMs to the handoff files first.

Patch 68 adds broader handoff bundle tests and drift coverage.

Those tests now prove, across green and failed states, that:

- top-level handoff files and bundled copies stay consistent
- `current_handoff.json` and `latest_report_index.json` agree on core state
- `next_prompt.txt` keeps the expected read order and takeover shape
- CLI export still produces the same bundle contract
- pass/fail recommendation output remains honest for known cases

## Why this shape stays narrow

This patch remains additive.

It does not change the handoff export behavior.
It makes the already-shipped handoff surfaces harder to drift accidentally.

## Current operator flow

The intended operator flow is now:

- run handoff export
- upload the bundle
- paste `handoff/next_prompt.txt`

## What comes later

Later handoff patches can build on this safely:

- final handoff-first documentation refresh

That keeps the redesign additive, Python-owned, and patch-by-patch.