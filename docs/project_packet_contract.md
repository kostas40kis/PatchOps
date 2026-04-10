# Project packet contract

## Purpose

A project packet is the maintained target-facing document that tells an operator or LLM how to work on one target repo through PatchOps without rebuilding context from scattered reports.

A packet is a **target contract**, not a replacement for manifests, reports, or handoff files.

Use project packets to keep these things explicit:

- target project identity
- target root and wrapper root
- selected profile
- what must remain outside PatchOps
- recommended command surfaces
- current mutable development status
- next recommended action

## Official packet location

Maintained target packets live under `docs/projects/`.

Current maintained examples include:

- `docs/projects/trader.md`
- `docs/projects/wrapper_self_hosted.md`

## Required packet sections

Every maintained packet should make the following easy to find:

1. target identity
2. target roots and expected runtime
3. selected profile and why it is correct
4. what PatchOps owns
5. what must remain outside PatchOps
6. recommended examples and command surfaces
7. current maintenance posture or phase guidance
8. mutable status fields such as latest passed patch and next recommended action

## What a packet must not become

A project packet must not become:

- target business logic
- a replacement for manifests
- a replacement for canonical reports
- a replacement for handoff files
- a reason to move reusable workflow logic back into PowerShell

## Relationship to other maintained surfaces

Use the packet together with:

- `README.md`
- `docs/project_status.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- canonical Desktop txt reports

## Maintenance rule

Refresh the packet when a meaningful report-producing run changes the maintained story for a target.

Keep packets narrow, explicit, and maintenance-oriented.
