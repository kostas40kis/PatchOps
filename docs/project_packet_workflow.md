# Project packet workflow

## Purpose

This workflow explains how project packets fit into normal PatchOps usage.

## two-step onboarding

A brand-new target project uses two-step onboarding.
An already-running PatchOps effort should prefer handoff/current_handoff.md first.

## onboarding bootstrap artifact surface

- onboarding/current_target_bootstrap.md
- onboarding/current_target_bootstrap.json
- onboarding/next_prompt.txt
- onboarding/starter_manifest.json

they do not replace manifests, reports, project packets, or handoff.

## helper-first onboarding command surface

- recommend-profile
- init-project-doc
- starter
- refresh-project-doc

These helper surfaces reduce ambiguity during first use and do not replace manifests, reports, or handoff.

## maintained update discipline

stable packet sections should change rarely
mutable packet sections should be refreshed as validated progress changes
grounded in reports and handoff when available
careful not to rewrite stable sections without real reason
handoff bundle first
refresh the packet after validated progress

PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START
Patch 79 - self-hosted operator flow
Read the generic PatchOps orientation first.
Then use docs/projects/wrapper_self_hosted.md as the self-hosted packet.
For self-hosted work the maintained helper command flow remains:
- bootstrap-target
- recommend-profile
- init-project-doc
- starter
- refresh-project-doc
PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:END

PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START
Mechanical workflow remains explicit.
- generic PatchOps orientation first
- two-step onboarding for brand-new targets
- handoff-first continuation for already-running work
- onboarding bootstrap artifacts remain helper outputs, not replacements for manifests or reports
PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:END
onboarding bootstrap artifacts
For already-running PatchOps work, use handoff first.

Patch 79 - self-hosted operator flow
This workflow is structured, conservative, and evidence-first.
It covers generic PatchOps orientation plus project packet creation and use.
Keep PowerShell thin.
Use py -m patchops.cli init-project-doc and py -m patchops.cli refresh-project-doc.
The wrapper self-hosted packet lives at docs/projects/wrapper_self_hosted.md.

## Handoff relationship
Use `py -m patchops.cli export-handoff` when the work is already in progress and the continuation packet needs to be refreshed.

## Packet role reminder

A project packet gives target context.

## Evidence reminder

A canonical report gives the evidence.

PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START

## Project-packet boundary
use the project-packet workflow only for brand-new target projects
start from the handoff bundle instead

## Workflow split
brand-new target project
already-running patchops effort
handoff/current_handoff.md
handoff/current_handoff.json
handoff/latest_report_copy.txt
docs/projects/<project_name>.md
generic onboarding packet
project packet
manifest
report

## Maintained update discipline
stable packet sections should change rarely
mutable packet sections should be refreshed as validated progress changes
grounded in reports and handoff when available
careful not to rewrite stable sections without real reason
handoff bundle first
refresh the packet after validated progress

## Onboarding bootstrap artifact surface
- onboarding/current_target_bootstrap.md
- onboarding/current_target_bootstrap.json
- onboarding/next_prompt.txt
- onboarding/starter_manifest.json
- they do not replace manifests, reports, project packets, or handoff

PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:END

## Targeted project packet workflow additions
the distinction between onboarding and continuation is explicit

<!-- PATCHOPS_E6_PROJECT_PACKET_WORKFLOW_BOUNDARY_LOCK_20260423 -->
brand-new target project
already-running patchops effort
handoff/current_handoff.md
handoff/current_handoff.json
handoff/latest_report_copy.txt
docs/projects/<project_name>.md
generic onboarding packet
project packet
manifest
report
the distinction between onboarding and continuation is explicit
the distinction between project packets and handoff is explicit
onboarding bootstrap artifact surface
helper-first onboarding command surface
they do not replace manifests, reports, project packets, or handoff
do not replace manifests, reports, or handoff
reduce ambiguity during first use
