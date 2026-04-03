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

Patch 66 adds the generated next-prompt surface:

- `handoff/next_prompt.txt`

That means the handoff export now produces both the state bundle and the ready-to-paste takeover prompt.

## Why this shape stays narrow

This patch remains additive.

It does not move handoff logic into PowerShell.
It extends the existing Python-owned handoff export surface so the operator no longer has to manually write the takeover prompt.

## What the generated next prompt now does

The generated prompt tells the next LLM exactly:

- what files to read first
- what current state the repo is in
- what the next action is
- what rules to preserve

This reduces manual explanation burden and makes the transition more mechanical.

## Current operator shape

Use:

- `py -m patchops.cli export-handoff --report-path <path-to-latest-report>`

or:

- `.\powershell\Invoke-PatchHandoff.ps1 -SourceReportPath <path-to-latest-report>`

Then upload the generated bundle and paste:

- `handoff/next_prompt.txt`

## What comes later

Later handoff patches can build on this safely:

- simplify `docs/llm_usage.md`
- broader handoff bundle tests and drift coverage
- final handoff-first documentation refresh

That keeps the redesign additive, Python-owned, and patch-by-patch.