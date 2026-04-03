# PatchOps

PatchOps is a project-agnostic patch execution harness for Windows-first patch workflows.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## Current Stage 1 command surface

- `patchops apply <manifest>`
- `patchops verify <manifest>`
- `patchops inspect <manifest>`
- `patchops plan <manifest> [--mode apply|verify]`
- `patchops profiles`
- `patchops template --profile ... --mode ... [--patch-name ...] [--output-path ...]`
- `patchops check <manifest>`
- `patchops doctor [--profile ...] [--target-root ...]`
- `patchops examples [--profile ...]`
- `patchops schema`

Thin PowerShell launchers under `powershell/` mirror the main authoring and discovery commands.

## Recommended safe first-use flow

1. `patchops profiles`
2. `patchops doctor --profile ...`
3. `patchops examples`
4. `patchops schema`
5. `patchops template ...`
6. `patchops check ...`
7. `patchops inspect ...`
8. `patchops plan ...`
9. `patchops apply ...` or `patchops verify ...`

## Example coverage

PatchOps ships example manifests for:

- generic apply
- backup proof
- verify-only
- trader examples
- Generic Python + PowerShell profile examples
- `generic_python_powershell`
- report preference examples
- command-group examples
- content-path examples
- allowed-exit-code examples

Both `content_path` and `allowed_exit_codes` now have dedicated apply-flow tests, so they should be treated as proven authoring patterns rather than inspect-only examples.


The command-group examples are also covered by dedicated apply-flow tests, so smoke/audit and cleanup/archive behavior are proven end to end, not just inspectable as manifest shapes.
The report-preference examples are also covered by a dedicated apply-flow test, so custom report directory and prefix behavior are proven end to end.
The backup example is also covered by a dedicated apply-flow test, so overwrite-plus-backup behavior is proven end to end.
The Generic Python + PowerShell profile examples are also covered by a dedicated apply-flow test, so mixed PowerShell-plus-Python execution is proven end to end.

## Consolidation status

Patch 25_26 consolidates the late-Stage-1 PatchOps baseline and prepares the repo for first deliberate trader-facing usage.

This means the repo now includes:
- `docs/patch_ledger.md`
- `docs/stage1_freeze_checklist.md`
- `docs/release_checklist.md`
- `docs/trader_first_usage.md`
- `docs/stage2_entry_criteria.md`

These docs are meant to stabilize project handoff, define what it means to treat Stage 1 as a trusted baseline, and make the first real trader-facing PatchOps run easier to execute deliberately.

Patch 27 adds concrete trader-first starter assets so the first real trader-facing PatchOps run can begin from explicit low-risk examples instead of a blank manifest.

Patch 28 adds an explicit trader execution sequence doc so the first real trader-facing PatchOps run can follow a concrete review-before-apply path.

Patch 29 adds a trader rehearsal runbook and first-real-run checklist so the first real trader-facing PatchOps usage can be executed with less ambiguity.

<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:START -->
## Trader-first readiness index

For the first trader-facing usage wave, start with `docs/trader_readiness_index.md`.

It is the single operator map that ties together:

- trader starter manifests,
- the trader manifest authoring checklist,
- safe first patch types,
- the trader execution sequence,
- the trader rehearsal runbook,
- the first real trader run checklist,
- and the Stage 2 entry criteria.

Use that document before drafting or running trader-first manifests.
<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:END -->

<!-- PATCHOPS_PATCH37_LLM_USAGE:START -->
## LLM-first usage

Future coding models should start with `docs/llm_usage.md`.

That document explains:

- how to read the project in the right order,
- how to pick a profile,
- how to build a manifest from current examples,
- how to choose between apply and verify-only,
- how to classify failure honestly,
- and how to avoid moving target-repo logic into PatchOps.
<!-- PATCHOPS_PATCH37_LLM_USAGE:END -->

<!-- PATCHOPS_PATCH38_TRADER_PROFILE:START -->
## Trader-specific usage

Use `docs/trader_profile.md` when PatchOps is being aimed at `C:\dev\trader`.

That document explains the trader profile's expected roots, runtime, backup conventions, report expectations, and the boundary between wrapper behavior and trader business logic.
<!-- PATCHOPS_PATCH38_TRADER_PROFILE:END -->
