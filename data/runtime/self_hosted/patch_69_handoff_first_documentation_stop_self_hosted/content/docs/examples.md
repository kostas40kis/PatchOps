# PatchOps examples

This file explains how to think about examples and starter flows.

## First rule

Examples are no longer the first state-reconstruction surface for future LLM takeover.

Future takeover should begin with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Only after that should an LLM or operator look at examples.

## Why examples still matter

Examples still matter for:

- starting a new patch manifest
- learning the manifest shape
- understanding apply versus verify-only flows
- seeing how content-path patches are authored
- learning cleanup/archive shapes
- learning profile-driven usage

## Common example workflow

For a normal manifest authoring cycle:

1. choose the closest example
2. run:
   - `py -m patchops.cli check <manifest>`
   - `py -m patchops.cli inspect <manifest>`
   - `py -m patchops.cli plan <manifest>`
3. only then run:
   - `py -m patchops.cli apply <manifest>`
   - or `py -m patchops.cli verify <manifest>`

## Handoff-first operator workflow

For LLM transition, do this instead:

1. generate handoff
2. upload the bundle
3. paste `handoff/next_prompt.txt`

Use:

- `py -m patchops.cli export-handoff --report-path <path>`
- or `.\powershell\Invoke-PatchHandoff.ps1 -SourceReportPath <path>`

## When to use examples after takeover

Once the handoff says what the next task is, examples are useful when:

- the next patch needs a new manifest shape
- the next patch needs a target-profile example
- the next patch needs a docs-only, verify-only, cleanup, or archive example
- the next patch needs a starting template rather than a repair

## Bottom line

Examples help you build the next manifest.

They should not be the first tool for reconstructing current repo state.