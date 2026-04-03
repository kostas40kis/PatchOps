# Project packet contract

## 1. Purpose of this document

This document defines the contract for every maintained project packet in PatchOps.

A project packet is the target-facing development contract that connects generic PatchOps rules to one specific target project.

It exists so that a future LLM or operator does not need to reconstruct a target project from scattered docs, old reports, or chat memory before producing the next safe patch.

A project packet is:

- human-readable,
- LLM-readable,
- maintained during the life of a target project,
- tied to a target root and profile,
- separate from generic PatchOps documentation,
- separate from manifests,
- separate from canonical reports,
- separate from handoff run-state artifacts.

The project packet is not the target repo itself.
It is not the generic wrapper documentation.
It is the bridge between PatchOps as a wrapper and one concrete target project.

---

## 2. What must remain true

The following rules are mandatory.

### 2.1 PatchOps remains project-agnostic

Project packets must not turn the PatchOps core into target-specific workflow code.

Project-specific assumptions belong in:

- profiles,
- manifests,
- project packets,
- the target repository.

They do not belong in generic PatchOps workflow logic.

### 2.2 PowerShell remains thin

PowerShell may:

- resolve paths,
- resolve runtimes,
- stage content,
- invoke PatchOps commands,
- write one Desktop txt report,
- open the report.

PowerShell should not become the long-term home of reusable project-packet logic.

### 2.3 Python owns reusable packet logic

If PatchOps later adds scaffold, refresh, validation, or export behavior for project packets, that reusable logic should live in Python-owned surfaces.

### 2.4 One canonical report per run remains the rule

A project packet does not replace run evidence.

Patch runs still require one canonical report showing what happened during the run.

### 2.5 Profiles remain the executable abstraction

A project packet is not a replacement for profiles.

The correct relationship is:

- **profile** = executable target assumptions
- **project packet** = human-readable and LLM-readable development contract for that target

### 2.6 Handoff remains the continuation surface

Project packets do not replace handoff artifacts.

The correct relationship is:

- **project packet** = maintained target understanding
- **handoff bundle** = latest run-state and next-action continuation surface

### 2.7 Prefer additive change over redesign

Project packets should be added conservatively.

This feature is meant to strengthen onboarding and continuity, not to redesign the PatchOps architecture.

---

## 3. Official location

All maintained project packets must live under:

`docs/projects/`

Canonical path format:

`docs/projects/<project_name>.md`

Examples:

- `docs/projects/trader.md`
- `docs/projects/osm_remediation.md`
- `docs/projects/wrapper_self_hosted.md`

A project packet should be a normal maintained markdown file inside the repo.
It should not be hidden inside reports, prompts, exports, or temporary runtime output.

---

## 4. Relationship to other PatchOps surfaces

A project packet must stay clearly distinct from the following repo surfaces.

## 4.1 Generic PatchOps docs

Generic docs explain how PatchOps works as a wrapper.

Examples include:

- `README.md`
- `docs/overview.md`
- `docs/llm_usage.md`
- `docs/manifest_schema.md`
- `docs/profile_system.md`
- `docs/examples.md`
- `docs/project_status.md`

A project packet must not duplicate all generic wrapper guidance.
It should reference generic guidance where appropriate and focus on the target project.

## 4.2 Profiles

Profiles hold executable assumptions and defaults for a class of target repositories.

A project packet should name the expected profile and explain why it fits, but it must not pretend to be the executable profile layer.

## 4.3 Manifests

Manifests describe what PatchOps should do in one specific run.

A project packet should guide manifest authoring, but it is not itself a manifest and must not be treated as one.

## 4.4 Canonical reports

Reports prove what happened in one run.

A project packet may summarize the latest known status, but it must not replace the report as the evidence artifact.

## 4.5 Handoff bundle

Handoff artifacts describe the current run-state resume point.

A project packet may reference the current handoff surface, but the handoff bundle remains the first resume surface for taking over an already-running PatchOps effort.

---

## 5. Required structure for every project packet

Every maintained project packet must contain the following sections.

Headings may include small wording variations, but the meaning must remain explicit and recognizable.

## 5.1 Purpose of the target project

State what the target project is trying to do.

This section should explain the target at a practical level, not in vague marketing language.

## 5.2 Target root

State the expected target project root explicitly.

Example:

`C:\dev\trader`

If a wrapper root is also important, include it explicitly.

## 5.3 Expected runtime

State the expected runtime or runtimes that PatchOps should use when working with this target.

Examples:

- Python virtual environment path
- system Python expectation
- PowerShell expectation when relevant

## 5.4 Selected profile

State the expected PatchOps profile for the target project.

This section should also explain why that profile is the correct abstraction.

## 5.5 What must remain outside PatchOps

State what business logic, operational rules, or target-owned responsibilities must not migrate into PatchOps.

This is a required boundary section.

## 5.6 Recommended example manifests

Point to the closest starter examples or manifest patterns that should be reused first.

The goal is to reduce blank-page authoring.

## 5.7 Patch classes expected for this target

Explain the types of patches that are likely for this project.

Examples:

- documentation patches
- validation/test patches
- launcher/reporting patches
- profile extensions
- target-safe starter patches

## 5.8 Development phases

Describe the target project in practical development phases so a future LLM can orient quickly.

## 5.9 Validation strategy

Describe how correctness should be validated for this target.

This should name the most important tests, checks, or cautious first-run patterns.

## 5.10 Report expectations

Describe what a successful PatchOps run should produce for this target.

This section should reinforce the one-report evidence contract.

## 5.11 Current state

Summarize the currently understood target state.

This should be concise, practical, and grounded.

## 5.12 Latest passed patch

State the latest known passed patch relevant to the target packet.

If unknown, say so honestly.

## 5.13 Latest attempted patch

State the latest known attempted patch relevant to the target packet.

If unknown, say so honestly.

## 5.14 Blockers

State known blockers, unresolved decisions, or missing confirmations.

If there are no known blockers, say that explicitly.

## 5.15 Next recommended action

State the narrowest useful next action.

This should help a future LLM continue without broad reinterpretation.

---

## 6. Stable layer versus mutable layer

Every project packet should be understood as having two layers.

## 6.1 Stable layer

The stable layer changes rarely.

It should usually include:

- purpose of the target project,
- target root,
- wrapper root when relevant,
- expected runtime,
- selected profile,
- what must remain outside PatchOps,
- patch classes expected for the target,
- development phases,
- validation strategy,
- report expectations.

These sections should change only when the target project itself meaningfully changes.

## 6.2 Mutable layer

The mutable layer changes as the project progresses.

It should usually include:

- current state,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action,
- latest report reference when included.

This layer should be updated conservatively and honestly.

## 6.3 Why this distinction matters

The stable layer prevents repeated re-explanation.
The mutable layer prevents stale status drift.

Together they let a future LLM understand both:

- what the target project fundamentally is,
- and where the work currently stands.

---

## 7. Required maintenance rules

Project packets must follow these maintenance rules.

## 7.1 Do not pretend certainty

If the current status is unclear, say so.
Do not invent passed patches, failed patches, or validated states.

## 7.2 Prefer explicit fields over prose-only ambiguity

Important state should be easy to scan.

Packet sections should be written so a future LLM or operator can identify:

- target root,
- profile,
- current status,
- blockers,
- next action,
- latest known patch state,
- without hunting through paragraphs.

## 7.3 Keep the packet target-focused

Do not turn the project packet into a second general PatchOps manual.

The generic docs already teach the wrapper.
The project packet should teach the target-facing contract.

## 7.4 Keep packet status conservative

A project packet may summarize current status, but it should never outrank:

- the canonical report,
- the explicit handoff bundle,
- validated repo reality.

## 7.5 Refresh without destroying stable guidance

When the packet is updated, the mutable layer should be refreshed without unnecessarily rewriting the stable layer.

## 7.6 Keep paths explicit

When roots, runtime paths, report paths, or important file paths matter, write them explicitly.

## 7.7 Maintain wording compatibility where useful

Future tests may check for required packet concepts.

Section wording may evolve, but the required contract concepts should remain plainly present.

---

## 8. Optional sections

A project packet may include extra sections when they are genuinely helpful.

Examples:

- wrapper root,
- recommended starter commands,
- known environment assumptions,
- current report reference,
- acceptance criteria for the next wave,
- links to major target-side docs,
- glossary or terminology notes.

Optional sections must not replace the required contract sections.

---

## 9. Generated versus manually maintained content

Project packets may eventually contain both manually maintained and generated content.

The intended model is:

- **manually maintained**: target purpose, boundaries, development phases, validation philosophy
- **generated or refreshed conservatively**: latest passed patch, latest attempted patch, latest report reference, next recommended action

If generation or refresh support is added later, it must preserve the stable layer and update the mutable layer conservatively.

---

## 10. How a future LLM should use a project packet

For a brand-new target project:

1. read the generic PatchOps onboarding packet first,
2. choose the smallest correct profile,
3. create or read `docs/projects/<project_name>.md`,
4. restate the target boundary and current state,
5. pick the closest example manifest or starter surface,
6. produce the next narrow patch.

For an already-running PatchOps effort:

1. read the handoff bundle first,
2. perform the exact next recommended action,
3. if the task is target-specific, also read the relevant project packet,
4. keep the packet aligned with the validated state afterward.

This keeps onboarding and continuation separate while still allowing the packet to remain useful across the life of the project.

---

## 11. Minimum validity test for a project packet

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

---

## 12. Bottom line

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
