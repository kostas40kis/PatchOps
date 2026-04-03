# PatchOps Finalization Master Plan

## 1. Purpose

This file is the maintained finalization anchor for PatchOps.
It is meant to be strong enough that a future LLM can continue the project without prior chat history.

Its job is to make five things explicit:

1. what PatchOps is and is not,
2. what is already shipped,
3. what posture the repo is in now,
4. what remains in the rushed finalization sequence,
5. what must not be redesigned casually.

This is not a new architecture roadmap.
It is a maintained finalization and freeze guide.

---

## 2. Project identity

- **Project name:** PatchOps
- **Workspace root:** `C:\dev`
- **Wrapper repo root:** `C:\dev\patchops`
- **Example target repo:** `C:\dev\trader`
- **Platform:** Windows + PowerShell + Python launcher (`py -3`)
- **Design posture:** project-agnostic, manifest-driven, evidence-driven, future-LLM-friendly

---

## 3. What PatchOps is

PatchOps is a standalone wrapper / harness / patch-execution toolkit.

PatchOps owns how change is:

- planned,
- applied,
- validated,
- evidenced,
- rerun,
- handed off,
- and bootstrapped for brand-new target projects.

Simple boundary:

- **PatchOps = how change is applied, validated, evidenced, retried, and handed off**
- **target repo = what the change actually is**

### What PatchOps is not

PatchOps is not:

- trader business logic,
- OSM business logic,
- target-side strategy/application logic,
- or a second PowerShell workflow engine.

---

## 4. Non-negotiable architecture rules

### 4.1 Keep PowerShell thin
PowerShell remains operator-facing and evidence-oriented.

### 4.2 Keep reusable logic in Python
Python continues to own manifests, profile resolution, file operations, reporting helpers, handoff generation, project-packet helpers, onboarding bootstrap generation, and validation logic.

### 4.3 Keep the wrapper project-agnostic
Trader is the first serious maintained target example.
It is not the identity of the wrapper.

### 4.4 Keep one-report evidence discipline
Each patch flow should still end with one canonical Desktop txt report.

### 4.5 Prefer narrow validation and repair over redesign
The default move in this repo is now:
- verify reality,
- repair narrowly,
- refresh docs,
- lock drift with tests only when needed.

### 4.6 Do not move target-project business logic into PatchOps
PatchOps must not absorb target-repo domain behavior.

---

## 5. Current interpreted repo state

PatchOps should now be interpreted as a **maintenance / refinement** repository rather than a greenfield buildout.

The truth-reset wave has already happened:

- Patch 125 identified a narrow blocker,
- Patch 125A repaired the first wording regressions,
- Patch 125B repaired the remaining wording regressions and returned the suite to green,
- Patch 126 refreshes the self-contained documentation set that a future LLM can use without prior chat history.
- Patch 127 adds narrow contract-lock validation so the final maintenance posture is protected by tests rather than memory.
- Patch 128 re-exports the current handoff bundle from a real green report and adds maintenance tests proving the active-work continuation flow remains mechanical.
- Patch 129 proves the new-target onboarding flow with a current helper-first onboarding rehearsal against a demo generic target.

### Latest confirmed green head

- **Latest confirmed green head:** Patch 129

### Shipped layers already present in meaningful form

1. **Core wrapper engine**
   - manifests,
   - profiles,
   - apply / verify / reporting,
   - deterministic evidence posture.

2. **Handoff-first continuation**
   - handoff bundle generation surfaces,
   - current-handoff docs orientation,
   - latest-report / next-prompt continuation story.

3. **Two-step onboarding / project packets**
   - project packet contract and workflow docs,
   - `docs/projects/` target packets,
   - packet initialization / refresh / helper surfaces,
   - onboarding bootstrap artifacts.

### Current posture

The repo should be treated as:

- finished enough as an initial product,
- in maintenance-mode finalization,
- open to narrow validation, proof, and freeze work,
- not open to casual core redesign.

---

## 6. What is already done

The following should now be considered shipped in meaningful form:

- the manifest-driven wrapper core,
- profile-driven target resolution,
- canonical one-report evidence discipline,
- verify-only and wrapper-only recovery posture,
- handoff-first continuation,
- project-packet onboarding for new targets.

In other words:
the remaining work is not “build the product.”
The remaining work is “prove, lock, compress, and freeze the product honestly.”

---

## 7. How to continue already-running work

For an already-running PatchOps effort, the continuation path should be mechanical.

### Default reading order

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `docs/project_status.md`
5. `docs/patch_ledger.md`

### Default behavior

- restate current state briefly,
- identify the exact next recommended action,
- perform only that next action,
- prefer narrow repair over broad rewrite.

If the handoff bundle is missing or stale, do not invent state.
Trust current repo files, current tests, and the latest report over historical prompts.

---

## 8. How to start a brand-new target project

For a brand-new target project, the onboarding path should also be mechanical.

### Maintained generic packet

Read these first:

1. `README.md`
2. `docs/overview.md`
3. `docs/llm_usage.md`
4. `docs/manifest_schema.md`
5. `docs/profile_system.md`
6. `docs/compatibility_notes.md`
7. `docs/failure_repair_guide.md`
8. `docs/examples.md`
9. `docs/project_status.md`
10. `docs/operator_quickstart.md`
11. `docs/project_packet_contract.md`
12. `docs/project_packet_workflow.md`

### Target-specific step

Then create or read:

- `docs/projects/<project_name>.md`

Then choose the nearest safe example/manifest surface and continue with the normal PatchOps flow:
- `check`
- `inspect`
- `plan`
- apply or verify
- read the canonical report
- refresh the project packet

---

## 9. Remaining rushed finalization sequence

After Patch 126, the remaining sequence is:

### F3 — final contract-lock validation sweep
Lock final posture with narrow tests rather than memory.

### F6 — final release / maintenance gate
Confirm the handoff path is practically trustworthy, not just documented.

### F6 — final release / maintenance gate
Confirm the two-step onboarding/project-packet path is practically trustworthy.

### F6 — final release / maintenance gate
Use current readiness/release surfaces to produce an explicit maintenance-mode verdict.

### F7 — final documentation stop and history compression
Refresh the final maintained reading set and compress history into durable docs.

### F8 — final source bundle / freeze export
Generate the final future-LLM export bundle plus canonical freeze report.

---

## 10. What not to redesign

Do not do the following unless a validation patch proves a real missing surface:

- do not redesign the manifest model,
- do not redesign the profile system,
- do not widen PowerShell into a second workflow engine,
- do not move target-repo business logic into PatchOps,
- do not replace handoff with project packets,
- do not replace project packets with handoff,
- do not rewrite every doc from scratch when narrow refresh is enough.

---

## 11. Honest finish line

PatchOps should be considered finished enough to freeze when:

- the final docs make the core truth explicit,
- continuation is mechanical,
- onboarding is mechanical,
- the main operator surface is locked by maintenance-grade validation,
- the repo clearly says it is in maintenance mode,
- one final future-LLM export bundle exists.

At that point, the correct posture is:

- the core wrapper is done,
- handoff-first continuation is done,
- two-step onboarding / project packets are done enough for real use,
- the remaining work is optional future refinement or target-specific expansion,
- not unresolved core architecture.

---

## 12. Current next action

The next patch after this file refresh is:

- **F6 — final release / maintenance gate**

That patch should be validation-first.
It should protect the final posture that is already shipped rather than widen the product.

<!-- PATCHOPS_PATCH126_FINALIZATION_MASTER:END -->

<!-- PATCHOPS_PATCH127_FINALIZATION_MASTER:START -->
## Patch 127 - final contract-lock validation sweep

Patch 127 is the F3 validation-first patch.

### What it locks

- the final maintenance-mode reading story in `README.md`,
- the final maintenance-mode takeover story in `docs/llm_usage.md`,
- the final maintenance-mode quickstart split in `docs/operator_quickstart.md`,
- the current maintenance posture in `docs/project_status.md`,
- the freeze/finalization posture in `docs/finalization_master_plan.md`.

### Why this matters

The earlier maintenance wave already tightened:
- help text contracts,
- launcher inventory contracts,
- exact CLI subcommand set contracts,
- onboarding-versus-continuation boundary wording,
- project-packet wording.

This patch adds the missing final layer:
the maintenance-mode final docs are now protected by explicit tests instead of memory.

### Current next action

- **F6 — final release / maintenance gate**

### Rule

This patch locks what is already shipped.
It does not widen the product.
<!-- PATCHOPS_PATCH127_FINALIZATION_MASTER:END -->

<!-- PATCHOPS_PATCH128_FINALIZATION_MASTER:START -->
## Patch 128 - prove active-work continuation flow

Patch 128 is the F4 proof patch from the rushed finalization sequence.

### What it proves

- the handoff bundle is not only documented but also refreshed from a real current PASS report,
- `export-handoff` continues to produce the maintained continuation surfaces under `handoff/`,
- the active-work continuation path remains mechanical:
  1. read the handoff bundle,
  2. restate current state,
  3. perform the next recommended action.

### Validation posture

The repo already had handoff surfaces and handoff-oriented tests.
This patch adds one current-state proof layer:
the generated `handoff/` outputs are now treated as a maintained active-work continuation surface.

### Current next action

- **F6 — final release / maintenance gate**

### Rule

This patch proves and refreshes an already-shipped continuation path.
It does not reopen handoff architecture.
<!-- PATCHOPS_PATCH128_FINALIZATION_MASTER:END -->

<!-- PATCHOPS_PATCH129_FINALIZATION_MASTER:START -->
## Patch 129 - prove new-target onboarding flow

Patch 129 is the F5 proof patch from the rushed finalization sequence.

### What it proves

- the helper-first onboarding path remains mechanical for a brand-new generic target,
- `recommend-profile` still suggests the correct profile for a generic Python target,
- `init-project-doc` still scaffolds a packet from explicit inputs,
- `starter` still produces the smallest useful starter manifest surface,
- onboarding bootstrap artifacts still summarize the target, reading order, and safest command order.

### What this patch deliberately does not claim

This patch does not redesign onboarding.
It does not replace manifests, reports, project packets, or handoff.
It proves that the already-shipped onboarding path still works in the current repo.

### Current next action

- **F6 — final release / maintenance gate**

### Rule

Treat onboarding as target-startup flow.
Treat handoff as active-work resume flow.
Keep those roles separate.
<!-- PATCHOPS_PATCH129_FINALIZATION_MASTER:END -->

<!-- PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:START -->
## F7 completion note

F6 has already passed.
F7 is the final documentation stop and history-compression pass.

After this doc stop, the maintained reading order should be treated as:

1. handoff bundle first for already-running work,
2. generic packet plus project packet for brand-new target onboarding,
3. project status, operator quickstart, examples, patch ledger, and this finalization plan as the durable repo-level orientation set.

The purpose of this step is not to redesign PatchOps again.
Its purpose is to make the repo readable and mechanically usable even if earlier chat history disappears.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_FINALIZATION_PLAN:END -->

<!-- PATCHOPS_F8_FREEZE_EXPORT_FINALIZATION:START -->
## F8 completion note

F8 is the final source bundle / freeze export step.

The preferred history-compression artifact after this step is:

`handoff/final_future_llm_source_bundle.txt`

That file should be treated as the durable future-LLM export bundle when a single upload artifact is preferred.
<!-- PATCHOPS_F8_FREEZE_EXPORT_FINALIZATION:END -->
