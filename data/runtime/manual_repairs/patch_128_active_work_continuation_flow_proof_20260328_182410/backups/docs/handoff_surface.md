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

Patch 66 added the generated next-prompt surface:

- `handoff/next_prompt.txt`

Patch 67 turned `docs/llm_usage.md` into the start page that points future LLMs to the handoff files first.

Patch 68 added broader handoff bundle tests and drift coverage.

Patch 69 is the documentation stop for the handoff-first UX.

It refreshes the major docs so onboarding now starts from the handoff artifact instead of scattered repo docs.

## Current start points

For a future LLM:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

For the operator:

1. run handoff export
2. upload the bundle
3. paste `handoff/next_prompt.txt`

## What this stop proves

The handoff-first UX is now reflected across the main docs, not only in implementation code and tests.

That means the repo now communicates the new continuation path consistently in:

- `README.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/llm_usage.md`
- `docs/handoff_surface.md`

## Why this shape stays narrow

This patch is a documentation stop.

It does not widen the engine.
It aligns the maintained docs with the already-shipped handoff surfaces while preserving older doc-contract expectations.

## Result

Future onboarding should now start from the handoff artifact, not from scattered documentation.

<!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:START -->
## Current operator contract

The handoff surface is now a maintained continuation contract.

Operator-facing reality:

- `export-handoff` is the standard way to produce the current continuation bundle.
- `handoff/current_handoff.md` is the first human-readable resume surface.
- `handoff/current_handoff.json` is the machine-readable resume surface.
- `handoff/latest_report_copy.txt` is the stable copy of the latest canonical report.
- `handoff/next_prompt.txt` is the generated takeover prompt for the next LLM.

Current expectation:

- use handoff first for already-running PatchOps continuation,
- use project packets first only for brand-new target-project onboarding,
- preserve the one-report evidence contract and narrow-repair discipline.
<!-- PATCHOPS_PATCH87_HANDOFF_SURFACE:END -->
