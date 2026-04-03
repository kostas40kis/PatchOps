# PatchOps Final Reference

## 1. Executive identity

PatchOps is a standalone wrapper, harness, and patch-execution toolkit for repository maintenance and patch delivery on Windows.

PatchOps is **not** the target repository. It is not trader logic, strategy logic, portfolio logic, exchange logic, or any other target-project business behavior. Its job is to standardize how changes are applied, validated, evidenced, retried, and handed off across projects.

The core problem PatchOps solves is repeated workflow reinvention. Without a wrapper, each patch wave tends to reimplement the same mechanics: target-root resolution, runtime selection, backup creation, file writing, validation execution, stdout and stderr capture, report rendering, rerun logic, and LLM handoff. PatchOps exists to solve those mechanics once, keep them explicit, and keep them separate from target-project domain code.

The boundary is simple and must remain simple:

- **PatchOps = how change is applied, validated, evidenced, retried, and handed off**
- **Target repo = what the change actually is**

PatchOps should therefore be treated as a maintained engineering tool, not as a temporary pile of scripts and not as a place to absorb target-project business logic.

## 2. Project identity and current maintenance posture

Current maintained identity:

- **Project name:** `PatchOps`
- **Workspace root convention:** `C:\dev`
- **Wrapper repo root:** `C:\dev\patchops`
- **Platform/workflow:** Windows + PowerShell + Python launcher (`py`)
- **Product posture:** maintenance / finalization, not greenfield buildout
- **Latest known passed patch:** `p134z_final_proof_handoff_refresh`
- **Latest known status:** `PASS`
- **Summary-integrity repair stream:** complete unless new contrary evidence appears
- **Current blocker state for that stream:** none

PatchOps should now be read as a finished initial product that is in maintenance mode. The core wrapper engine is already shipped in meaningful form. Handoff-first continuation is already shipped in meaningful form. Two-step onboarding and project-packet support are already shipped in meaningful form. Future work, if any, should be additive and narrow rather than architectural.

## 3. Core architecture and non-negotiable rules

These rules define the lasting shape of the project.

### 3.1 Keep PowerShell thin and operator-facing

PowerShell is the operator boundary. It may resolve paths, resolve runtimes, launch the Python CLI, capture output, and produce one canonical Desktop txt report. It should not become a second workflow engine. Reusable wrapper logic belongs in Python.

### 3.2 Keep reusable workflow logic in Python

Python owns the durable mechanics: manifest handling, profile resolution, file operations, workflow execution, reporting, retry planning, handoff generation, onboarding helpers, and validation logic.

### 3.3 Keep PatchOps project-agnostic

Trader is an important profile and example target, but PatchOps is not trader-specific software. Project-specific assumptions belong in profiles, manifests, project packets, and target repositories—not in the generic wrapper core.

### 3.4 Preserve manifest-driven execution

PatchOps should do what the manifest says. It should not silently guess important behavior. Manifests are the explicit contract for file writes, command execution, report preferences, and patch intent.

### 3.5 Preserve profile-driven target assumptions

Profiles isolate target-repo assumptions from the wrapper core. Differences in target roots, runtime path conventions, backup roots, report naming, and mixed Python/PowerShell expectations belong in profiles rather than in hardcoded core logic.

### 3.6 Preserve one canonical report per run

Each patch flow should still end with one canonical Desktop txt report that stands on its own. A future reader should not need shell history, screenshots, scattered temp files, or memory of what happened interactively in order to understand the run.

### 3.7 Prefer narrow validation and repair over redesign

At the current project stage, the default move is: validate, classify drift honestly, repair narrowly, refresh docs and tests where needed, and keep moving. Broad redesign is not the default and should not be reopened unless current repo evidence proves a real missing surface.

### 3.8 Do not move target-project business logic into PatchOps

PatchOps can accelerate and stabilize target-project work. It must not absorb target-project application behavior or domain policy.

### 3.9 Use PatchOps to patch PatchOps

Self-hosting is part of the maintained workflow. PatchOps should be used to repair and validate PatchOps itself where possible, because that proves the wrapper’s own mechanics under realistic conditions.

## 4. The three shipped product layers

PatchOps should be understood as one product with three major intent layers.

### 4.1 Core wrapper engine

This is the reusable execution layer. It owns:

- manifest-driven `apply`, `verify`, `inspect`, and `plan` style workflows
- profile-driven target-root and runtime resolution
- deterministic reporting and evidence rendering
- backup and file-writing discipline
- validation execution and failure classification
- cleanup and archive workflow support
- example manifests and profile-aware template generation

### 4.2 Handoff-first continuation for already-running work

This is the continuation layer for active PatchOps work that already exists. It owns:

- human-readable handoff state
- machine-readable handoff state
- stable latest-report copy and indexing
- generated next-prompt support
- continuation guidance that is meant to be mechanical rather than interpretive

### 4.3 Two-step onboarding and project-packet flow for brand-new target projects

This is the new-project startup layer. It owns:

- generic PatchOps orientation docs that stay stable across projects
- project-specific packet or contract files under `docs/projects/`
- onboarding bootstrap surfaces and starter artifacts
- helper surfaces that speed up profile choice and first-manifest authoring
- explicit separation between first-time onboarding and already-running work continuation

These layers are additive. Handoff does not replace the core wrapper. Project packets do not replace manifests. Onboarding does not replace handoff. Each layer solves a different part of the operator and LLM workflow.

## 5. Current shipped capabilities

The current repo materials indicate the following capabilities are shipped and maintained.

### 5.1 Manifest workflow surfaces

PatchOps exposes a manifest-centered workflow with at least these operator-facing surfaces:

- `apply`
- `verify`
- `inspect`
- `plan`
- `check`
- `schema`
- `template`
- `examples`
- `profiles`
- `doctor`
- `wrapper-retry`
- `release-readiness`
- `export-handoff`
- onboarding helper surfaces such as `bootstrap-target`, `recommend-profile`, and starter-oriented helpers

The maintained reading surfaces and contract tests also show that the operator surface is treated as a locked interface rather than an informal CLI that can drift casually.

### 5.2 Profile system

The maintained profiles include at least:

- `trader`
- `generic_python`
- `generic_python_powershell`

Profiles define target-facing assumptions such as target-root defaults, runtime path resolution, report preferences, backup-root conventions, and mixed Python/PowerShell behavior. The mixed profile exists to support target repositories that need both Python and PowerShell execution without turning that into a new global architecture rule. The profile discovery surface is also first-class and JSON-readable.

### 5.3 Apply / verify / inspect / plan behavior

PatchOps supports:

- real apply flows
- verification-only rerun flows
- normalized manifest inspection
- plan previews before execution
- wrapper-only retry planning where the patch content likely succeeded but wrapper mechanics or reporting need recovery

This is important because PatchOps is designed to distinguish between target-repo failures and wrapper-mechanics failures, and to support narrow reruns instead of blind full reruns.

### 5.4 Reporting and evidence model

The reporting model is deterministic and central to the tool. The maintained report contract includes:

- explicit roots and runtime information
- target file lists
- backup evidence
- write evidence
- exact command sections
- full stdout and stderr capture
- summary-facing output with final `ExitCode` and `Result`

The report is the canonical evidence artifact. PatchOps is not supposed to scatter evidence across multiple unrelated files and then ask the next operator to reconstruct the run manually.

### 5.5 Backup and write discipline

PatchOps backs up existing files before overwriting them, preserves relative paths under patch-specific backup roots, records missing files honestly, and treats file writing as part of the explicit contract instead of as an invisible side effect.

### 5.6 Help, launcher, and operator surfaces

The project includes a thin PowerShell launcher layer and maintenance-mode tests that protect the operator surface against drift. Current materials indicate launcher inventory and help-contract validation for the shipped command set. The launcher set includes the usual manifest and verify entrypoints and, by the later maintenance waves, also includes discovery and maintenance entrypoints such as profiles, doctor, examples, template, check, plan, handoff export, readiness, and wrapper-retry.

### 5.7 Handoff bundle surfaces

The handoff bundle is a shipped continuation surface, not a future idea. Current maintained handoff artifacts include:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`

The default continuation flow is: export handoff, upload the bundle, and begin from the generated reading order rather than reconstructing state from scattered docs.

### 5.8 Onboarding, project-packet, and bootstrap surfaces

The onboarding layer is also shipped in meaningful form. Current materials indicate support for:

- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`
- `docs/projects/` as the maintained packet location
- target-facing packet examples and tests
- onboarding bootstrap artifacts under `onboarding/`
- helper flows that recommend a profile, create bootstrap artifacts, and provide conservative starter-manifest help

The project packet remains the human-readable target contract. Profiles remain the executable target abstraction. Manifests remain the immediate run contract. Reports remain the proof of what happened.

### 5.9 Maintenance-grade validation and contract-lock posture

The maintenance wave added narrow contract tests that protect shipped truth rather than relying on memory. Current materials indicate validation for:

- help text and exact command wording
- PowerShell launcher inventory
- CLI subcommand inventory
- operator-surface partitioning and boundaries
- onboarding and continuation guidance boundaries
- final maintenance-mode wording
- summary-integrity repair behavior
- current handoff and onboarding proof layers

This means PatchOps is no longer just a collection of features; it is a tool whose public operator and documentation surfaces are intentionally locked.

## 6. Directory and file-map reference

This section explains the maintained repo layout in practical terms.

### 6.1 Top-level directories

#### `patchops/`

The Python package. This is the core wrapper implementation.

Important subareas include:

- `patchops/workflows/` — apply, verify-only, cleanup, archive, and other workflow execution logic
- `patchops/profiles/` — target-profile definitions and profile abstractions
- `patchops/reporting/` — report rendering and report-section logic
- `patchops/files/` — path helpers, backup helpers, and file-writing mechanics
- supporting modules such as CLI entrypoints, manifest models, loaders, validators, planning helpers, handoff helpers, and readiness helpers

#### `tests/`

The maintenance-grade test suite. This protects manifest contracts, profile behavior, workflow behavior, reporting truth, launcher behavior, onboarding surfaces, handoff surfaces, and maintenance-mode wording.

#### `powershell/`

Thin operator-facing PowerShell launchers. These expose the Python-owned workflows in Windows-friendly form and help preserve the one-report evidence discipline.

#### `examples/`

Example manifests and starting surfaces for common patch classes. These are part of the supported authoring story and are meant to reduce guesswork for both humans and LLMs.

#### `docs/`

The main human-readable documentation set.

Important areas include:

- core orientation docs such as `overview.md`, `manifest_schema.md`, `profile_system.md`, `compatibility_notes.md`, `failure_repair_guide.md`, `examples.md`, `llm_usage.md`, `operator_quickstart.md`, `project_status.md`, and `patch_ledger.md`
- maintenance and freeze docs such as `finalization_master_plan.md`
- continuity docs such as `handoff_surface.md` and `summary_integrity_repair_stream.md`
- onboarding docs such as `project_packet_contract.md`, `project_packet_workflow.md`, and `docs/projects/`

#### `handoff/`

The stable continuation bundle for already-running work. This is the first place a future LLM should look when resuming active PatchOps work.

#### `onboarding/`

The stable bootstrap area for brand-new target-project onboarding. This holds generated onboarding artifacts such as current bootstrap summaries, starter manifests, and next-prompt material for first-time target work.

#### `data/runtime/`

Runtime artifacts generated during patch work. This includes patch backups, generated templates, self-hosted manual repair artifacts, process output fragments, and other operational evidence that should not be confused with the main maintained docs.

### 6.2 How to read the repo structure

A future reader should use this mental model:

- `patchops/` = implementation
- `tests/` = proof and drift protection
- `powershell/` = thin Windows operator entrypoints
- `examples/` = authoring aids
- `docs/` = maintained explanation and contracts
- `handoff/` = active-work continuation bundle
- `onboarding/` = new-target bootstrap bundle
- `data/runtime/` = operational artifacts, backups, generated outputs, and self-hosted repair evidence

## 7. How PatchOps is supposed to be used

PatchOps has two distinct starting flows. They should not be mixed together.

### 7.1 Flow A — already-running continuation

Use this when PatchOps work is already in progress and the next human or LLM needs to continue from the current state.

The maintained continuation order is:

1. read `handoff/current_handoff.md`
2. read `handoff/current_handoff.json`
3. read `handoff/latest_report_copy.txt`
4. briefly restate the current state
5. perform the exact next recommended action
6. if the task is target-specific, read the relevant packet under `docs/projects/<project_name>.md`

This flow is meant to be mechanical rather than interpretive.

### 7.2 Flow B — brand-new target onboarding

Use this when PatchOps is being applied to a target project that does not yet have an established packet and bootstrap state.

The maintained onboarding order is:

1. read the generic PatchOps packet docs
2. choose the smallest correct profile
3. create or read the target project packet under `docs/projects/`
4. use examples or starter/bootstrap surfaces to create the first conservative manifest
5. run the usual `check -> inspect -> plan -> apply or verify` loop
6. preserve one-report evidence and keep the project packet up to date

### 7.3 How manifests fit in

Manifests are the run contract. They tell PatchOps what files to back up and write, what commands to run, what exits are tolerated, what report preferences apply, and what profile is active.

### 7.4 How examples fit in

Examples are the starting surface for authoring. They reduce guesswork, show maintained manifest shapes, and help both humans and LLMs choose the smallest correct pattern for a patch.

### 7.5 How handoff surfaces fit in

Handoff surfaces answer: “What just happened, what is the current state, and what should happen next?” They are for active continuation, not first-time target onboarding.

### 7.6 How the one-report evidence model fits in

The canonical report is the proof of what happened for a specific run. Handoff references it. Project packets describe ongoing target context. Docs explain the system. None of those replace the report.

## 8. Handoff-first continuation

Handoff-first continuation is a first-class product feature.

### 8.1 Files to read first

For active PatchOps continuation, the maintained reading order begins with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

### 8.2 How current state is conveyed

Current state is conveyed through both human-readable and machine-readable forms. The markdown handoff explains the state in plain language. The JSON handoff gives structured state for deterministic consumption. The latest report copy preserves the real evidence artifact in a stable location.

### 8.3 Why continuation is supposed to be mechanical

The point of the handoff redesign was to stop asking the next LLM to reconstruct repo state from multiple docs and guesses. The desired experience is to receive the exact current state, the exact failure class if any, the exact next action, and the exact recommended mode.

### 8.4 What the handoff files mean

- `current_handoff.md` — primary human-readable active-work summary
- `current_handoff.json` — machine-readable continuation state
- `latest_report_copy.txt` — stable copy of the latest canonical report
- `latest_report_index.json` — index or pointer layer for latest-report lookup
- `next_prompt.txt` — generated continuation prompt for the next LLM or operator

### 8.5 How a future LLM should resume active PatchOps work

A future LLM should start with the handoff files above, restate the current repo state, then perform the exact next recommended action without reopening broad architecture questions unless current repo evidence demands it.

### 8.6 Current maintained interpretation

The current maintained handoff interpretation is that no further action is required for the just-closed summary-integrity repair stream unless new contrary evidence appears. The stream is closed through `p134z_final_proof_handoff_refresh`, and the handoff bundle was refreshed from a green report after the report-path fixes landed.

## 9. Two-step onboarding and project-packet flow

The onboarding model is also a first-class product feature.

### 9.1 Generic PatchOps packet

The generic packet teaches PatchOps itself. It explains what the wrapper is, how profiles work, how manifests work, how to choose between apply and verify, how to classify failures, and what architecture rules must not be violated.

### 9.2 Project-specific packet or project contract

The project packet is the maintained target-facing markdown contract under `docs/projects/`. It explains:

- what the target project is
- which profile to use
- what roots and runtimes are expected
- what must remain outside PatchOps
- what validation posture applies
- what current phase and next action are relevant for that target

### 9.3 What belongs in project packets

A project packet should carry both a stable layer and a mutable layer.

Stable layer:

- target identity
- target root
- expected runtime
- selected profile
- target boundary rules
- recommended example manifests
- development phases and patch-class guidance
- validation philosophy
- report expectations

Mutable layer:

- current phase
- current objective
- latest passed patch
- latest attempted patch
- blockers
- latest report path if relevant
- next recommended action

### 9.4 How onboarding differs from continuation

Onboarding is for a target that is not yet in motion under PatchOps. Continuation is for work that is already in motion. Handoff files solve continuation. Project packets solve first-time target startup. They are related, but they are not interchangeable.

### 9.5 Why onboarding exists

Without an onboarding layer, a future LLM has to infer too much about a new target project. The project-packet model makes target-specific assumptions explicit without polluting the generic wrapper core.

### 9.6 Boundary rule for target-specific extension work

Target-specific extension work should stay outside the generic wrapper core unless it is genuinely reusable across multiple target repositories. The generic wrapper must remain generic.

## 10. Historical development summary

This section compresses the project history without turning the document into a patch ledger.

### 10.1 Initial core wrapper buildout

PatchOps began as the effort to replace repeated PowerShell patch plumbing with one reusable manifest-driven wrapper. The early goal was to standardize target-root resolution, runtime selection, backups, file writes, validation commands, and one-report evidence.

### 10.2 Verify-only and wrapper-only retry buildout

The project then made rerun logic more deliberate by separating normal apply behavior from verification-only flows and wrapper-only retry paths. This established the idea that a failed run should be classified rather than blindly rerun.

### 10.3 Release-readiness and operator-surface validation wave

A later wave hardened the operator surface with explicit readiness checks, launcher coverage, help-contract tests, subcommand inventory protection, and exact-set validation. This turned PatchOps into a more stable operator-facing tool rather than an evolving internal script.

### 10.4 Handoff-first continuation buildout

The handoff redesign then made active continuation more mechanical. Current and latest-report surfaces, generated next-prompt support, and handoff export behavior were added so the next LLM would not need to reconstruct state from scattered documents.

### 10.5 Project-packet and onboarding buildout

The project then extended the same philosophy to brand-new targets. Generic PatchOps packet docs, target-specific project packets, onboarding bootstrap surfaces, and helper flows made first-time project startup faster and more deterministic.

### 10.6 Late maintenance and finalization wave

Once the major surfaces existed, the repo moved into a maintenance and finalization posture. The focus shifted from broad buildout to contract locking, truth resets, continuation proofs, onboarding proofs, maintenance-gate checks, and durable source-bundle export.

### 10.7 Summary-integrity repair stream and closure

A late maintenance stream repaired a real reporting-truth bug and the related workflow-facing consequences. That stream matters because it explains the current fail-closed and report-path reliability posture.

## 11. Summary-integrity repair stream and why it matters

The summary-integrity stream must be preserved as history because it explains the wrapper’s current reporting and handoff reliability model.

### 11.1 Original confirmed bug

The original confirmed bug was a contradiction between required command evidence and rendered summary output. Required command failure evidence could coexist with a final summary that still said `PASS`. That was not just a cosmetic issue; it was a truth failure in the wrapper’s summary-facing surfaces.

### 11.2 What was repaired

The repair stream narrowed the problem rather than redesigning the system.

It established that:

- required failures outside `allowed_exit_codes` render `FAIL`
- earlier required failure remains sticky even if later required commands succeed
- explicitly tolerated nonzero exits still render `PASS`
- workflow-facing surfaces fail closed instead of trusting stale success state
- summary and handoff layers do not silently override contradictory command evidence

### 11.3 Report-path and Windows-hostile custom `report_dir` issues

The stream also had to repair Windows-hostile self-hosted custom `report_dir` behavior. Long custom report-path shapes could break runs before safe report creation. The maintained interpretation is that a fallback repair was required so unsafe report-directory choices are avoided before hostile mkdir or write behavior can break the run.

The final closure story is:

1. the original summary contradiction was repaired
2. fail-closed workflow-facing behavior was repaired
3. the Windows-hostile custom report-path issue was repaired through fallback behavior
4. the maintained proof layer returned to green
5. the handoff bundle was refreshed from a green report
6. the stream closed through `p134z_final_proof_handoff_refresh`

### 11.4 Why this history must not be erased

This stream explains why current PatchOps reporting is maintenance-grade and why the wrapper now treats contradictory evidence conservatively. Future readers should not mistake this for optional lore. It is part of the product’s reliability story.

## 12. What was planned historically but is not an active obligation now

Older planning documents remain valuable as historical compression artifacts, but they should not be treated as the primary source of current truth.

### 12.1 Older plans that still matter as history

Historical planning surfaces include:

- early patch-by-patch development plans
- Stage 2 buildout plans
- handoff redesign plans
- two-step onboarding plans
- finalization plans
- future-LLM source bundles
- takeover prompts and maintenance prompts

These documents matter because they preserve why the project evolved the way it did.

### 12.2 How to interpret them now

Older plans often describe surfaces as future work that later became shipped. Those surfaces should now be documented as shipped, not as unfinished obligations.

Examples of ideas that moved from plan to shipped surface include:

- handoff bundle export and generated next-prompt behavior
- project-packet onboarding docs and packet locations
- onboarding bootstrap helper behavior
- maintenance-mode contract locking around help text, command inventory, and docs

### 12.3 What should now be treated as historical rather than active blockers

Historical references to early Stage 2 uncertainty, old freeze-point ambiguity, or once-future continuation/onboarding designs should be read as origin history rather than as live blockers, unless current repo evidence shows a real regression.

### 12.4 What future work remains

Future work, if undertaken, should be additive only. Examples include:

- new target profiles
- more target-project packets
- narrower operator ergonomics improvements
- additional contract tests where drift risk remains high
- further helper surfaces that do not widen the core architecture

None of that should be described as proof that the core product is unfinished.

## 13. What should not be redesigned

The following areas are not candidates for casual redesign:

- the manifest model, unless current repo evidence proves a real missing surface
- the profile system, unless a reusable multi-target need proves a real missing surface
- the handoff-vs-onboarding split
- the thin PowerShell boundary
- the one-report evidence model
- the project-agnostic wrapper boundary
- the rule that PatchOps should not absorb target-project business logic

A future maintainer should assume that broad redesign is unjustified unless current validated repo evidence proves otherwise.

## 14. Practical reading order for future humans and LLMs

### 14.1 For already-running PatchOps work

Start with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `docs/project_status.md`
5. `docs/patch_ledger.md`

Then perform the exact next recommended action.

### 14.2 For a brand-new target project

Start with:

1. `README.md`
2. `docs/llm_usage.md`
3. `docs/operator_quickstart.md`
4. `docs/project_packet_contract.md`
5. `docs/project_packet_workflow.md`
6. the relevant packet under `docs/projects/`, if it already exists
7. the example manifests and starter/bootstrap surfaces

Then choose the smallest correct profile, author conservatively, and preserve one-report evidence.

## 15. Final maintenance stance

PatchOps should now be treated as a maintained wrapper product.

That means:

- the core wrapper is already shipped
- handoff-first continuation is already shipped
- two-step onboarding and project packets are already shipped
- no broad redesign is currently justified
- future work should be additive only
- narrow maintenance, validation, proof refresh, and target-specific extension remain valid
- the correct starting point for active work is the current handoff bundle
- the correct starting point for brand-new target work is the generic onboarding flow plus the relevant project packet

PatchOps is no longer best understood as an architecture experiment. It is best understood as a maintained workflow product whose core job is to make patch execution, evidence, continuation, and onboarding explicit and reliable.

---

PatchOps should now be treated as a maintained wrapper product. No broad redesign is currently justified. Optional future work is additive only. Future LLMs should begin from the current handoff for active work or the generic onboarding flow for new targets.
