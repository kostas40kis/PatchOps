# PatchOps LLM usage

This file is the orientation page for future coding LLMs.

It is not the main state-reconstruction surface anymore.

## Read order

If you are taking over PatchOps, read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Only after that should you read additional repo docs or source files.

## Why this changed

The handoff-first redesign makes repo continuation mechanical instead of interpretive.

A future LLM should not need to infer the current state from scattered docs.
The repo should tell the next LLM exactly:

- what state the repo is in
- what happened last
- what the next action is
- what rules must be preserved

## What each handoff file is for

### `handoff/current_handoff.md`

Read this first.

It is the human-readable resume point.
It tells you:

- current stage
- latest attempted patch
- latest passed patch
- current status
- failure class
- next action
- next recommended mode
- must-read files before acting

### `handoff/current_handoff.json`

Read this second.

It is the machine-readable version of the same state.
Use it when you want deterministic fields instead of prose interpretation.

### `handoff/latest_report_copy.txt`

Read this third.

Inspect it only if you need the full canonical report evidence:

- commands run
- stdout
- stderr
- exit code
- final result
- failure details

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

## Architecture rules that still apply

Preserve these unless the handoff explicitly proves a deeper architecture problem:

- keep PowerShell thin
- keep reusable wrapper logic in Python
- preserve the one-report evidence contract
- do not move target-repo business logic into PatchOps
- prefer narrow repair over broad rewrite
- preserve backward compatibility where it already exists

## Operator flow

The intended operator flow is now:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

That is the primary continuation path.

## When to read more docs

After reading the handoff files, read other docs only when needed.

Common next documents include:

- `docs/failure_repair_guide.md`
- `docs/manifest_schema.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/handoff_surface.md`

Read only the ones the current handoff tells you are relevant.

## If the handoff says the issue is narrow

Do not redesign the repo.

Repair the narrow surface first.
Only widen scope if the evidence forces that conclusion.

## Bottom line

`docs/llm_usage.md` is now the start page.

`handoff/current_handoff.md` is the first real resume artifact.