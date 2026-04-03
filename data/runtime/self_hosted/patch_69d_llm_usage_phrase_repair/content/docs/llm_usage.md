# PatchOps LLM usage

PatchOps is a **standalone wrapper / harness project**.

This file is the orientation page for future coding LLMs.

It is not the main state-reconstruction surface anymore.

## Target repos own:

Target repos own:

- actual business and domain behavior
- target-side workflows
- project-specific architecture
- target-repo tests

Never move target-repo business logic into PatchOps.

## How to read the project

If you are taking over PatchOps, read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Only after that should you read additional repo docs or source files.

## Why this changed

The handoff-first redesign makes repo continuation mechanical instead of interpretive.

The repo should tell the next LLM exactly:

- what state the repo is in
- what happened last
- what the next action is
- what rules must be preserved

## What each handoff file is for

### `handoff/current_handoff.md`

Read this first.

It is the human-readable resume point.

### `handoff/current_handoff.json`

Read this second.

It is the machine-readable version of the same state.

### `handoff/latest_report_copy.txt`

Read this third.

Inspect it when you need the full canonical report evidence.

## How to pick a profile

Use profile-aware surfaces deliberately:

- `py -m patchops.cli profiles`
- `py -m patchops.cli doctor --profile trader`

Pick the profile that matches the target repo and keep target assumptions inside the target profile or manifest.

Trader is the first serious profile, not the identity of the wrapper.

## How to build a manifest

Use examples and templates instead of inventing a manifest from scratch.

Typical authoring flow:

- start from `examples/trader_first_verify_patch.json` or another close example
- or use `py -m patchops.cli template`
- then run:
  - `py -m patchops.cli check <manifest>`
  - `py -m patchops.cli inspect <manifest>`
  - `py -m patchops.cli plan <manifest>`

## How to decide between apply and verify-only

Use apply when the patch should write content.

Use verify-only when the narrowest trustworthy move is to re-check existing target files and evidence.

Useful launcher:

- `powershell/Invoke-PatchVerify.ps1`

## How to classify failure

Use `docs/failure_repair_guide.md`.

That guide explains:

- content failure
- wrapper failure
- verification-only rerun
- wrapper-only repair
- escalation rules

## How to avoid moving target-repo logic into PatchOps

Keep reusable wrapper logic in Python-owned PatchOps surfaces.
Keep target-repo business logic in the target repo.
do not move target-repo business logic into PatchOps
prefer narrow repair over broad rewrite

## Default future-LLM workflow

When taking over PatchOps:

1. read `handoff/current_handoff.md`
2. read `handoff/current_handoff.json`
3. read `handoff/latest_report_copy.txt` only if needed
4. briefly restate:
   - current state
   - latest attempted patch
   - failure class
   - next action
5. produce only the next repair patch or next planned patch

## Operator flow

The intended operator flow is now:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

In plain terms: run handoff export, upload the generated bundle, and paste `handoff/next_prompt.txt`.

## Bottom line

`docs/llm_usage.md` is the orientation page.

`handoff/current_handoff.md` is the first real resume artifact.