# Operator Quickstart

This file is the compact procedural guide for daily PatchOps use.

## 1. Baseline health commands

Run the baseline health sequence before a new maintenance patch when repo state is uncertain:

```powershell
py -m pytest -q
py -m patchops.cli profiles
py -m patchops.cli doctor --profile generic_python
py -m patchops.cli examples
py -m patchops.cli template --profile generic_python --mode apply --patch-name example_patch
```

## 2. Safe authoring loop

The normal low-risk operator loop is:

1. `profiles`
2. `doctor`
3. `examples`
4. `template`
5. `check`
6. `inspect`
7. `plan`
8. `apply` or `verify`

Use `verify` when the patch content is already correct and the goal is validation-first evidence rather than fresh file writes.

## 3. Read-the-report-first rule

Always read the canonical report before guessing what failed.
The report is the main evidence artifact.
Do not start by re-explaining the run from memory when the canonical report already exists.

## 4. Failure classification quick table

- content failure -> repair target content
- wrapper failure -> repair wrapper/reporting mechanics first
- suspicious-run -> inspect the canonical report and any artifact emission before inferring truth
- verify-only -> use when writes are not needed and the main need is rerun evidence

## 5. Active continuation flow

For already-running PatchOps work, start with:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Then confirm the current report and current repo tests before widening scope.

## 6. New-target onboarding flow

For a brand-new target project, start with:

- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`
- the relevant file under `docs/projects/`

This is the project-packet-aware usage path.
Use `docs/projects/` as the home of maintained target packets.

<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START -->
## Patch 79 - project-packet operator commands

The project-packet-aware usage surface keeps the operator story explicit without widening PowerShell into a second workflow engine.

Recommended packet-related commands:

- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`

These commands support self-hosted and target-facing packet usage while keeping the handoff bundle as the first continuation surface for already-running PatchOps work.

One canonical report remains required for packet-aware usage and for ordinary maintenance flows.
The operator should still read one canonical report before widening scope.
<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:END -->

## Final maintenance-mode quickstart

PatchOps should now be operated as a maintenance-mode wrapper utility.

### Already-running PatchOps work

Handoff-first continuation quickstart:

- read `handoff/current_handoff.md`
- read `handoff/current_handoff.json`
- read `handoff/latest_report_copy.txt`
- run `export-handoff` when the handoff bundle needs refresh
- paste `handoff/next_prompt.txt` when continuing with another LLM

Path A - continue already-running PatchOps work with the handoff bundle first, then verify current repo truth, then continue narrowly.

### Brand-new target onboarding

Path B - brand-new target onboarding starts from the generic packet and then the project packet for the target.

Brand-new target onboarding should use:

- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`
- `docs/projects/<project_name>.md`

This keeps continuation and onboarding separate.

### Onboarding bootstrap reminder

Onboarding bootstrap reminder:

- `onboarding/current_target_bootstrap.md`
- `onboarding/current_target_bootstrap.json`
- `onboarding/next_prompt.txt`
- `onboarding/starter_manifest.json`

For already-running PatchOps work, use handoff first instead.

### Onboarding helper reminder

Onboarding helper reminder:

- `recommend-profile`
- `init-project-doc`
- `starter`
- onboarding bootstrap artifacts
- `refresh-project-doc`

These helpers reduce ambiguity during first use, but for already-running PatchOps work, use handoff first.

### Final posture reminder

- use the safe command flow,
- prefer narrow repair over broad rewrite,
- preserve one canonical report,
- and keep continuation separate from onboarding.

## Suspicious-run note

A suspicious-run should be read through the canonical report first.
If optional artifact emission occurred, read that artifact as a wrapper health aid rather than as a replacement for the report itself.

<!-- PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START -->
## Final documentation stop - operator split

The operator surface must keep the continuation-versus-onboarding boundary explicit.

Path A - continue already-running PatchOps work through the handoff bundle.
Path B - brand-new target onboarding through the generic packet plus project packet.

One canonical report remains required.
The one canonical report rule applies before and after project-packet-aware usage.

For already-running PatchOps work, use handoff first instead of onboarding bootstrap artifacts.

Onboarding bootstrap reminder:
- `onboarding/current_target_bootstrap.md`
- `onboarding/current_target_bootstrap.json`
- `onboarding/next_prompt.txt`
- `onboarding/starter_manifest.json`

Onboarding helper reminder:
- `recommend-profile`
- `init-project-doc`
- `starter`
- onboarding bootstrap artifacts
- `refresh-project-doc`

Brand-new target onboarding should remain explicit rather than blended into continuation.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:END -->

## When not to write a giant PowerShell runner

Do not write a giant PowerShell runner when a narrow manifest-driven PatchOps path or a tiny direct repair will do.

PowerShell should stay thin.
Use it for path resolution, runtime invocation, one Desktop report, and report opening.
