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

Patch 65 adds the thin PowerShell launcher:

- `powershell/Invoke-PatchHandoff.ps1`

It stays thin and simply calls the Python export surface, captures stdout/stderr reliably, writes one Desktop txt report, and opens that report for the operator.

## Why this shape stays narrow

This patch remains additive.

It does not move handoff logic into PowerShell.
It adds one operator-facing launcher that delegates the real work into the existing Python-owned export surface.

## What Invoke-PatchHandoff.ps1 now does

The launcher supports:

- project root override
- Python runtime override
- optional source report path
- current stage override
- bundle name override

It calls:

- `py -m patchops.cli export-handoff`

or the resolved repo Python runtime equivalent, then records:

- command
- stdout
- stderr
- exported handoff summary
- final `ExitCode`
- final `Result`

inside one Desktop txt report.

## Current operator shape

Use:

- `.\powershell\Invoke-PatchHandoff.ps1`

or, with an explicit canonical report:

- `.\powershell\Invoke-PatchHandoff.ps1 -SourceReportPath <path-to-latest-report>`

## What comes later

Later handoff patches can build on this safely:

- generated `handoff/next_prompt.txt`
- lighter `docs/llm_usage.md`
- broader handoff bundle tests
- final handoff-first documentation refresh

That keeps the redesign additive, Python-owned, and patch-by-patch.