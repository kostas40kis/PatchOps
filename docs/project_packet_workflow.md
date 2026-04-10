# Project packet workflow

## Purpose

This workflow explains how project packets fit into normal PatchOps usage after the published Patch 29A state.

## When to use a packet

Use a project packet when you need the maintained target-facing contract for one repo.

Examples:

- `docs/projects/trader.md`
- `docs/projects/wrapper_self_hosted.md`

## Core command surfaces

Packet-oriented maintenance should keep using the normal CLI surfaces:

- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`
- `py -m patchops.cli check <manifest>`
- `py -m patchops.cli inspect <manifest>`
- `py -m patchops.cli plan <manifest>`
- `py -m patchops.cli apply <manifest>`
- `py -m patchops.cli verify <manifest>`

## Recommended flow

1. Read the packet for the target.
2. Read the current handoff if work is already in progress.
3. Use `check`, `inspect`, and `plan` before risky apply work.
4. Apply or verify narrowly.
5. Read the canonical report first.
6. Refresh the packet only after the report changes the maintained target story.

## Self-hosted workflow reminder

For PatchOps patching PatchOps, use `docs/projects/wrapper_self_hosted.md`.

The selected profile remains `generic_python`, PowerShell stays thin, and reusable logic stays in Python-owned surfaces.

## Handoff relationship

Handoff remains the resume surface for already-running work.

A project packet gives target context.
A handoff file gives current-run continuity.
A canonical report gives the evidence.

## Maintenance posture

Keep packet work additive, operator-friendly, and conservative.
