# Project packet contract

This document defines the contract for every maintained **project packet** inside PatchOps.

PatchOps remains **project-agnostic**.
A project packet is the maintained target-facing contract that helps PatchOps stay project-agnostic while still making onboarding faster and less interpretive.

Project packets live under `docs/projects/`.
The canonical target-specific location is:

`docs/projects/<project_name>.md`

A project packet does not replace profiles, manifests, reports, or handoff.
It complements them.

## Required structure

Every maintained project packet should make the following structure explicit:

### Stable layer

The stable layer should explain:

- what the target project is,
- expected roots,
- expected runtime,
- selected profile,
- what must remain outside PatchOps,
- recommended examples and starter posture.

### Mutable layer

The mutable layer should explain:

- current phase,
- current objective,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action.

## Boundary rules

PatchOps should remain project-agnostic.
That means project-specific rules belong in project packets, profiles, manifests, and target repos rather than inside generic PatchOps core logic.

A project packet must stay explicit about how it differs from:

- profiles,
- manifests,
- reports,
- handoff files.

## Minimum validity test for a project packet

A future LLM should be able to create a valid project packet from this contract without guessing:

- where the file belongs,
- what sections are mandatory,
- what belongs in the stable layer,
- what belongs in the mutable layer,
- how the packet differs from profiles,
- how the packet differs from manifests,
- how the packet differs from reports,
- how the packet differs from handoff files.

If those distinctions are not clear, the packet is not yet valid.

## Bottom line

A project packet is the maintained target-facing contract inside PatchOps.

It exists to make target onboarding faster, safer, and less interpretive while preserving the architecture that PatchOps already established.

The intended system remains:

- generic docs teach PatchOps,
- project packets teach one target project,
- manifests tell PatchOps what to do now,
- reports prove what happened,
- handoff files tell the next LLM how to continue from the latest run.

<!-- PATCHOPS_PATCH90_CONTRACT:START -->
## Update discipline contract

Every maintained project packet should keep the distinction between stable and mutable sections explicit.

Stable sections usually include:

- purpose,
- target root,
- expected runtime,
- selected profile,
- boundary rules,
- development phases,
- validation philosophy,
- report expectations.

Mutable sections usually include:

- current state,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action,
- latest report reference when relevant.

For a brand-new target project, create the packet before the first manifest.

For an already-running PatchOps effort, use handoff first and refresh the relevant project packet only after validated progress.

A project packet must not replace manifests, reports, or handoff files.
<!-- PATCHOPS_PATCH90_CONTRACT:END -->

<!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:START -->
## Final project-packet contract reminder

A project packet is the maintained target-facing contract inside PatchOps.

### Stable layer

The stable layer should explain:

- what the target project is,
- expected roots,
- expected runtime,
- selected profile,
- what must remain outside PatchOps,
- recommended examples and starter posture.

### Mutable layer

The mutable layer should explain:

- current phase,
- current objective,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action.

### Boundary reminder

A project packet does not replace:

- profiles,
- manifests,
- reports,
- handoff files.

It complements them by making target onboarding faster and less interpretive.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_CONTRACT:END -->

powershell remains thin
python owns reusable
