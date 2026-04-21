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
PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:END

PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START
Mechanical workflow remains explicit.
PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:END
