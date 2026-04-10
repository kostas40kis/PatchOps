# Handoff surface

## Purpose

This page explains the maintained handoff-first continuation surface.

Patch 69 is the documentation stop for the handoff-first UX.

## What to read first during continuation

Read these maintained surfaces first:
- `README.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/llm_usage.md`

Then read the live handoff artifacts:
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/next_prompt.txt`

## Practical distinction

- handoff = current run state and next action
- project packets = target-facing contract for onboarding or target understanding
- examples = starter authoring shapes when risk is low and active handoff is not the governing surface

Future onboarding should now start from the handoff artifact only when the work is already active and being resumed. Brand-new target onboarding should still start from the packet/onboarding path.

## Operator rule

Run handoff export after a meaningful passing or failing run so the next operator or LLM can continue from one current maintained continuation packet instead of scattered reports.
