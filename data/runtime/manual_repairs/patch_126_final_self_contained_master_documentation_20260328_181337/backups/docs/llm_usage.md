# LLM Usage Guide

This file is the orientation page for future coding LLMs.

PatchOps is a **standalone wrapper / harness project**.

Target repo = what changes  
PatchOps = how the change is applied, validated, evidenced, retried, and handed off.

It is not the main state-reconstruction surface anymore.

---

## 1. Which path are you on?

Use this file to choose the correct starting path.

There are now **two different LLM entry modes**:

1. **continuing an already-running PatchOps effort**
2. **starting a brand-new target project with PatchOps**

Do not mix those two jobs together.

The right first files are different.

---

## 2. Path A — continuing an already-running PatchOps effort

For current repo-state reconstruction, start with the handoff artifacts.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

That is the maintained continuation surface.

Do **not** begin by scanning scattered docs and trying to infer the current repo state from scratch when the handoff bundle is available.

After reading the handoff, briefly restate:

- current state
- latest attempted patch
- failure class
- next action

Then produce only the next repair patch or next planned patch.

### operator flow for continuation

The intended operator path is:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

That is the default takeover flow for in-progress PatchOps work.

---

## 3. Path B — onboarding a brand-new target project

When the task is **not** “continue the current PatchOps run,” but instead “use PatchOps to start work on a new target repo,” begin with the **generic onboarding packet**.

That packet teaches PatchOps itself before you touch any target-specific surface.

Read these generic docs first:

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

After reading that generic packet, you should be able to restate:

- what PatchOps owns
- what must remain outside PatchOps
- which profile seems correct
- which examples are the closest starting point

Then create or update the target-facing project packet under:

- `docs/projects/<project_name>.md`

That project packet is the maintained contract for that target project.

---

## 4. When to use handoff files vs. project packets

This distinction must stay explicit.

### Use handoff files when:

- you are resuming already-running PatchOps work
- you need the latest repo state
- you need the last pass/fail outcome
- you need the exact next recommended action
- you need to know whether the next move is a new patch, repair patch, verify-only rerun, or wrapper-only retry

### Use a project packet when:

- you are working against a specific target project
- you need the stable target rules
- you need the target root, expected runtime, selected profile, boundaries, examples, phases, and validation posture
- you need the maintained target-facing development contract

### Simple rule

- **handoff files** = current run-state and next action
- **project packet** = longer-lived target-project contract
- **manifest** = exact instructions for this run
- **report** = evidence of what happened

Project packets do **not** replace handoff.
Handoff does **not** replace project packets.
Neither one replaces manifests, profiles, or the canonical report.

---

## 5. how to read the project when doing real work

If you are continuing PatchOps itself, start from the handoff files first.

If you are onboarding a new target, start from the generic packet first.

After the correct first step, the usual supporting docs still matter:

- `docs/overview.md`
- `docs/manifest_schema.md`
- `docs/profile_system.md`
- `docs/compatibility_notes.md`
- `docs/failure_repair_guide.md`
- `docs/examples.md`
- `docs/project_status.md`

Read only as much as the current task actually needs.
Prefer the maintained surfaces over reconstructing intent from scattered history.

---

## 6. how to pick a profile

Use the smallest correct profile.

Examples include:

- `trader`
- `generic_python`
- `generic_python_powershell`

Profiles remain the executable target abstraction.

The project packet is **not** a replacement for a profile.

Use the profile to determine executable assumptions such as:

- target root conventions
- runtime expectations
- launcher expectations
- validation environment assumptions

Use the project packet to determine the target-specific development contract.

Do not move target-repo logic into PatchOps.

---

## 7. how to build a manifest

Start from bundled examples and adapt them.

Examples remain the main starting surface for manifest authoring after orientation is complete.

Typical flow:

1. choose the correct profile
2. choose the closest bundled example
3. create or adapt a manifest
4. confirm target root, files, backups, validation commands, and report behavior
5. run:
   - `check`
   - `inspect`
   - `plan`
6. then run apply or verify-only deliberately

When the target is a maintained project-packet target, use that packet to narrow which examples and patch classes make sense.

For trader-first work, the existing starter examples remain important low-risk surfaces.

---

## 8. how to decide between apply and verify-only

Use `apply` when files need to be written or rewritten.

Use verify-only when files are already on disk and the goal is narrow validation, re-evidence, or wrapper-only recovery without widening back into a full rewrite pass.

See also:

- `powershell/Invoke-PatchVerify.ps1`
- `docs/failure_repair_guide.md`

If you are unsure, start narrower and justify widening only when necessary.

---

## 9. how to classify failure

Treat failures as one of these broad classes:

- target-repo content failure
- wrapper mechanics failure

When classification is unclear, do not widen blindly.
Reclassify first.

Prefer narrow repair over broad rewrite.

The important question is not “how do I rerun this?”
The important question is “what failed, and what is the narrowest trustworthy recovery path?”

---

## 10. how to avoid moving target-repo logic into PatchOps

Keep target-specific or project-specific assumptions in:

- the target repo
- the selected profile
- the target project packet
- the manifest for the current run

Keep the generic PatchOps core focused on:

- patch application mechanics
- backup behavior
- validation execution
- evidence/report generation
- rerun and repair classification
- handoff generation
- operator-facing launcher behavior

Do not move target-repo business logic into PatchOps.

---

## 11. target boundary reminder

Target repos own:

- target-repo business logic
- target-repo code correctness
- target-repo policy and domain behavior

PatchOps owns:

- how the change is applied
- how the change is validated
- how the change is evidenced
- how reruns and repairs are classified
- how handoff is generated

Never move target-repo business logic into PatchOps.

---

## 12. trader profile identity note

Trader is the first serious profile, not the identity of the wrapper.

Use trader-specific docs and examples when the target really is `C:\dev\trader`.

Do not let trader assumptions leak into generic PatchOps workflow logic.

---

## 13. bottom line

Use the correct starting surface for the actual job:

- for **continuation**, start from handoff
- for **new target onboarding**, start from the generic packet
- for **target-specific guidance**, use the relevant project packet
- for **the exact run**, use the manifest
- for **proof**, use the canonical report

That is the intended LLM operating model for PatchOps.

<!-- PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START -->
## Project-packet onboarding now includes helpers

For a brand-new target project, the onboarding flow is now:

1. read the generic PatchOps packet,
2. determine the smallest correct profile with `recommend-profile`,
3. create or refresh the target packet under `docs/projects/`,
4. generate the first manifest from the closest example or `starter --profile ... --intent ...`,
5. run `check`, `inspect`, `plan`, then apply or verify,
6. inspect the canonical report,
7. refresh the project packet and continue patch by patch.

For already-running PatchOps work, continuation still begins with:
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Project packets and onboarding helpers speed up new-target startup.
They do not replace handoff for current-state continuation.
<!-- PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:END -->

<!-- PATCHOPS_PATCH87_LLM_USAGE:START -->
## Current continuation entry point

For already-running PatchOps work, the handoff bundle is the first maintained entry point.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

After reading the handoff bundle:

- briefly restate current state,
- restate latest attempted patch,
- restate failure class,
- perform the exact next recommended action.

Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists.

Use project packets for brand-new target onboarding, not as the primary resume surface for PatchOps itself.
<!-- PATCHOPS_PATCH87_LLM_USAGE:END -->

<!-- PATCHOPS_PATCH88B_LLM_USAGE:START -->
## Legacy-tested orientation wording that remains current

This guide still teaches:

- how to read the project,
- how to pick a profile,
- how to build a manifest,
- how to decide between apply and verify-only,
- how to classify failure,
- how to avoid moving target-repo logic into patchops.

Maintained reference surfaces still include:

- `docs/failure_repair_guide.md`
- `examples/trader_first_verify_patch.json`
- `powershell/Invoke-PatchVerify.ps1`

These older references remain valid even though the handoff bundle is now the first continuation surface for already-running PatchOps work.
<!-- PATCHOPS_PATCH88B_LLM_USAGE:END -->

## Boundary reminder

- prefer narrow repair over broad rewrite
- do not move target-repo business logic into PatchOps
