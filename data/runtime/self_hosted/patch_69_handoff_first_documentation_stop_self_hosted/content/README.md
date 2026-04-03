# PatchOps

PatchOps is a standalone wrapper for applying, validating, evidencing, retrying, and handing off patch work across repos.

It is not target-repo business logic.
It is the reusable mechanics around patch work.

## What PatchOps owns

PatchOps owns:

- patch application
- validation execution
- stdout/stderr capture
- one-report evidence
- failure classification
- wrapper-only retry surfaces
- handoff generation
- future-LLM continuation ergonomics

## What PatchOps does not own

PatchOps does not own:

- trader strategy
- target-repo execution logic
- product-specific business rules
- project-specific decisions that belong in the target repo

## Start here if you are a future LLM

Do not reconstruct repo state from scattered docs first.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Then produce only the next repair patch or next planned patch.

## Start here if you are the operator

The operator flow is now:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

That is the intended continuation path.

## Core rules

PatchOps should preserve these rules unless evidence forces a deeper change:

- keep PowerShell thin
- keep reusable workflow logic in Python
- preserve the one-report evidence contract
- prefer narrow repair over broad rewrite
- keep the wrapper project-agnostic
- preserve existing compatible surfaces where they are still relied on

## Current handoff-first UX

The repo now has a handoff-first continuation surface.

Important outputs include:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`

They can be generated with:

- `py -m patchops.cli export-handoff`
- or `.\powershell\Invoke-PatchHandoff.ps1`

## Where to look next

If you need orientation after the handoff files, read:

- `docs/llm_usage.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/handoff_surface.md`
- `docs/manifest_schema.md`

## Summary

PatchOps is now meant to tell the next LLM exactly how to resume, not merely provide enough background for a clever model to infer the current state.