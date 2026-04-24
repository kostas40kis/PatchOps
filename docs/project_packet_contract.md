# Project packet contract

## Purpose

A project packet is the maintained target-facing document that tells an operator or LLM how to work on a target safely.

## required structure

A required structure is expected for docs/projects/ packets.

## Core boundaries

PatchOps remains project-agnostic.
Packets do not replace manifests, reports, project packets, or handoff.
Do not absorb target business logic into PatchOps.

## Update discipline

Stable packet sections should change rarely.
Mutable packet sections should be refreshed as validated progress changes.
A project packet is the maintained target-facing contract inside PatchOps.
A project packet does not replace profiles, manifests, reports, or handoff files.
### Stable layer
### Mutable layer
The stable layer should explain expected roots, expected runtime, selected profile, boundary rules, and recommended examples.
The mutable layer should explain current phase, current objective, latest passed patch, latest attempted patch, blockers, and next recommended action.

Project packet homes live under docs/projects/.
Reference examples include docs/projects/trader.md and docs/projects/wrapper_self_hosted.md.
A maintained packet should still declare current phase, current objective, latest passed patch, latest attempted patch, blockers, and next recommended action.

## Boundary note
This packet should explain what must remain outside PatchOps so the wrapper stays separate from target-repo business logic.

## Manifest boundary

A project packet is not a replacement for manifests.

PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START

## Project packet contract
project-agnostic
powershell remains thin
stable layer
mutable layer
update discipline contract
stable sections usually include
mutable sections usually include
current state
latest passed patch
latest attempted patch
latest report reference when relevant
for a brand-new target project, create the packet before the first manifest
for an already-running patchops effort, use handoff first
a project packet must not replace manifests, reports, or handoff files

PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:END

## Targeted project packet contract additions
python owns reusable mechanics while PowerShell remains thin

<!-- PATCHOPS_E6_PROJECT_PACKET_CONTRACT_EXECUTABLE_ABSTRACTION_LOCK_20260423 -->
profiles remain the executable abstraction

<!-- PATCHOPS_E6A_PROJECT_PACKET_CONTRACT_HANDOFF_CONTINUATION_SURFACE_LOCK_20260423 -->
handoff remains the continuation surface

<!-- PATCHOPS_E6C_PROJECT_PACKET_HANDOFF_DIFFERENCE_PHRASE_LOCK_20260423 -->
how the packet differs from handoff files
