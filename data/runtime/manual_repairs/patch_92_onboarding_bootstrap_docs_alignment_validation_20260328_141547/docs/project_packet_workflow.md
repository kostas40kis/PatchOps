# Project packet workflow

## 1. Purpose of this document

This document defines the two-step onboarding workflow for new target projects in PatchOps.

The goal is to make first-time project onboarding much more deliberate and much less interpretive.

PatchOps already has a continuation workflow for already-running work:

- read the handoff bundle,
- restate current state,
- perform the exact next recommended action.

This document defines the complementary workflow for a brand-new target project:

- first teach the LLM PatchOps itself,
- then create one maintained project packet for the target project,
- then begin patching the target project through normal PatchOps workflows.

This workflow is meant to keep three things separate:

- generic PatchOps orientation,
- target-specific project understanding,
- per-run execution and evidence.

---

## 2. The two-step onboarding model

The onboarding workflow for a brand-new target project should always be understood as two explicit steps.

## 2.1 Step 1 — generic PatchOps orientation

Before a future LLM touches target-specific assumptions, it should read the small stable PatchOps packet that teaches the wrapper itself.

This generic packet exists so the LLM understands:

- what PatchOps is,
- what PatchOps is not,
- how to choose a profile,
- how manifests work,
- how apply differs from verify-only,
- how failure should be classified,
- what reports prove,
- which architecture rules must not be violated.

## 2.2 Step 2 — project packet creation and use

After the generic packet is understood, the LLM should create or maintain one project-specific packet under:

`docs/projects/`

That project packet becomes the target-facing contract for that specific repo.

It should explain:

- what the target project is,
- which profile fits,
- which roots and runtimes are expected,
- what must remain outside PatchOps,
- what phase the target is in,
- what the next recommended action is.

Only after those two steps should the LLM author or adapt the next manifest.

---

## 3. When to use this workflow

This workflow is for **brand-new target-project onboarding**.

Use it when:

- the target project does not yet have a maintained project packet,
- the LLM is being introduced to the target project for the first time,
- the human wants a stable target-facing markdown contract inside PatchOps,
- the work is about starting or shaping a new project-specific PatchOps effort.

This workflow is not the primary resume flow for an already-running PatchOps effort.

---

## 4. When not to use this workflow first

If the work is already in progress and PatchOps has current handoff artifacts, the LLM should start with handoff first.

Read:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Then:

- briefly restate current state,
- perform the exact next recommended action,
- read the relevant project packet only if the task is target-specific.

This preserves the intended distinction:

- **handoff** = continuation of current run-state
- **project packet** = maintained understanding of one target project

---

## 5. Required generic onboarding packet

For a brand-new target project, the future LLM should read the following generic docs first.

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

This is the minimum generic packet that should be uploaded or reviewed before target-specific packet creation begins.

---

## 6. What the LLM should do after reading the generic packet

Once the generic docs are understood, the future LLM should restate a few things before creating the first target packet.

At minimum it should restate:

- what PatchOps owns,
- what must remain outside PatchOps,
- which profile appears to be the smallest correct fit,
- which example manifests are the closest starting point,
- whether the first run should be apply or verify-only,
- whether any obvious compatibility constraints exist.

This restatement reduces blind guessing before the target packet is written.

---

## 7. How to create the first project packet

The future LLM should then create:

`docs/projects/<project_name>.md`

The packet must follow the project packet contract.

At minimum, the first version should contain:

- target purpose,
- target root,
- wrapper root when relevant,
- expected runtime,
- selected profile,
- what must remain outside PatchOps,
- recommended example manifests,
- patch classes expected for the target,
- development phases,
- validation strategy,
- report expectations,
- current state,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action.

The first version does not need to pretend perfect certainty.

If parts of current state are unclear, the packet should say so honestly.

---

## 8. How to choose the first manifest after packet creation

Once the packet exists, the next manifest should come from the nearest safe example rather than from a blank page.

The intended flow is:

1. identify the selected profile,
2. identify the closest example manifest,
3. decide whether the first run should be apply or verify-only,
4. adapt the example conservatively,
5. run:
   - `check`
   - `inspect`
   - `plan`
6. then apply or verify,
7. inspect the canonical report,
8. update the project packet.

This keeps project-packet guidance connected to real PatchOps execution rather than leaving it as detached documentation.

---

## 9. How the project packet should be updated later

A project packet is not a one-time startup note.

It is meant to be maintained as the target project evolves.

## 9.1 Stable sections

The stable sections should change rarely.

These usually include:

- purpose,
- target root,
- expected runtime,
- selected profile,
- boundary rules,
- development phases,
- validation philosophy,
- report expectations.

## 9.2 Mutable sections

The mutable sections should be refreshed as work progresses.

These usually include:

- current state,
- latest passed patch,
- latest attempted patch,
- blockers,
- next recommended action,
- latest report reference when relevant.

## 9.3 Update discipline

Packet updates should be:

- conservative,
- grounded in reports and handoff when available,
- explicit about uncertainty,
- careful not to rewrite stable sections without real reason.

---

## 10. Relationship between project packets and handoff

Project packets and handoff bundles are related, but they are not the same thing.

## 10.1 What the project packet does

The project packet preserves target-specific understanding across time.

It helps a future LLM understand:

- what the target project is,
- how it should be developed with PatchOps,
- what boundaries must not be violated,
- what the current target state roughly is.

## 10.2 What handoff does

The handoff bundle preserves the immediate continuation surface for the latest run.

It helps a future LLM understand:

- what just happened,
- whether the run passed or failed,
- what the failure class was,
- what the exact next recommended action is.

## 10.3 The correct order of use

For a brand-new target project:

1. generic packet,
2. project packet creation,
3. manifest authoring,
4. report review,
5. packet update.

For an already-running PatchOps effort:

1. handoff bundle,
2. exact next recommended action,
3. relevant project packet if target context is needed,
4. packet refresh after validated progress.

That separation must remain clear.

---

## 11. Daily-use workflow for a future LLM

Once the feature is fully supported, the daily-use workflow should look like this.

## 11.1 Brand-new target project

1. read the generic PatchOps packet,
2. restate PatchOps boundaries and likely profile,
3. create `docs/projects/<project_name>.md`,
4. choose the nearest example manifest,
5. run `check`, `inspect`, and `plan`,
6. apply or verify,
7. inspect the canonical report,
8. update the project packet,
9. continue patch by patch.

## 11.2 Already-running target project inside PatchOps

1. read the handoff bundle,
2. perform the exact next recommended action,
3. consult `docs/projects/<project_name>.md` when target context is needed,
4. keep the packet aligned with validated state,
5. continue patch by patch.

---

## 12. Operator expectations

The operator path should remain simple.

The human should not have to explain the whole project from scratch every time a new LLM takes over.

The intended operator experience is:

### For new target-project startup

- provide the generic PatchOps packet,
- ask the LLM to create the project packet,
- review the first manifest,
- run the workflow,
- keep the packet maintained.

### For continuation of existing work

- export or upload the handoff bundle,
- provide the generated or maintained continuation prompt,
- let the LLM continue from the exact current state,
- refresh the project packet when the validated state changes.

---

## 13. What this workflow must not do

This workflow must not:

- replace profiles,
- replace manifests,
- replace canonical reports,
- replace handoff bundles,
- move target business logic into generic PatchOps code,
- weaken the one-report evidence contract,
- turn PowerShell into the home of reusable onboarding logic.

The project-packet workflow exists to make onboarding better, not to blur the architecture.

---

## 14. Minimum success criteria for this workflow

This workflow is valid when all of the following are true:

- a future LLM can identify which docs to read first,
- a future LLM can create a compliant project packet without guessing,
- the distinction between onboarding and continuation is explicit,
- the distinction between project packets and handoff is explicit,
- the distinction between project packets and profiles is explicit,
- the distinction between project packets and manifests is explicit,
- the first manifest can be chosen from examples more mechanically,
- packet updates can happen without rewriting the whole document each time.

---

## 15. Bottom line

The project-packet workflow gives PatchOps a clean first-time onboarding path that complements the existing handoff-first continuation path.

The intended system is:

- generic docs teach PatchOps,
- project packets teach one target project,
- manifests tell PatchOps what to do now,
- reports prove what happened,
- handoff files tell the next LLM how to continue from the latest run.

That is how PatchOps can make both startup and continuation more mechanical without violating the architecture it already established.

<!-- PATCH_79_SELF_HOSTED_WORKFLOW_START -->
## Patch 79 - self-hosted operator flow

When PatchOps patches PatchOps itself, keep using the same model that PatchOps applies to other targets.

### Self-hosted read order

1. Read `handoff/current_handoff.md`.
2. Read `handoff/current_handoff.json`.
3. Read `handoff/latest_report_copy.txt`.
4. Read `docs/projects/wrapper_self_hosted.md` for target-level rules.

### Self-hosted operating rules

- Treat `C:\dev\patchops` as both the wrapper root and the current target root.
- Keep PowerShell thin. Use it only for path resolution, runtime invocation, one Desktop txt report, and report opening.
- Keep reusable packet logic in Python-owned surfaces such as `patchops/project_packets.py` and `patchops/cli.py`.
- Prefer narrow repair over broad rewrite when the handoff classifies a wrapper-only problem.
- Keep the canonical report as the main evidence artifact.

### Stable command surfaces

Use the CLI rather than custom PowerShell logic for packet operations:

- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`

### Self-hosted continuation rule

When the current work is already running, the handoff bundle is still the first resume surface.
The self-hosted packet exists to explain target-level rules and current project state, not to replace the handoff bundle.
<!-- PATCH_79_SELF_HOSTED_WORKFLOW_END -->

<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START -->
## Self-hosted project-packet command flow

When PatchOps patches itself, treat `docs/projects/wrapper_self_hosted.md` as the target-facing packet for the wrapper repo.

### Recommended self-hosted order

1. Start with the handoff bundle when work is already in progress.
2. Read `docs/projects/wrapper_self_hosted.md` when project-packet context is needed.
3. Use `py -m patchops.cli init-project-doc` only when creating a brand-new packet surface.
4. Use `py -m patchops.cli refresh-project-doc --name wrapper_self_hosted` after validated progress changes the mutable state.
5. Keep PowerShell thin: resolve paths, invoke the CLI, and produce one canonical report.
6. Keep reusable project-packet logic in Python-owned surfaces.

### Self-hosted examples

```text
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted
py -m patchops.cli check <manifest>
py -m patchops.cli inspect <manifest>
py -m patchops.cli plan <manifest>
py -m patchops.cli apply <manifest>
```

Use the smallest correct patch class.
For docs-only self-hosted work, prefer a documentation patch.
If files are already correct and only evidence is needed, prefer a verify-only rerun.
<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:END -->

<!-- PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START -->
## Mechanical onboarding sequence

A future LLM should treat new-target onboarding as mechanical:

1. read the generic PatchOps packet,
2. run `recommend-profile --target-root ...`,
3. inspect the closest starter examples,
4. use `init-project-doc` for a brand-new packet when needed,
5. use `bootstrap-target` when a stronger onboarding bundle is helpful,
6. use `starter --profile ... --intent ...` to avoid blank-page manifest authoring,
7. use `refresh-project-doc` after validated progress changes mutable packet state,
8. continue with `check`, `inspect`, `plan`, and then apply or verify.

The onboarding story should now feel closer to the handoff story:
structured, conservative, and evidence-first.
<!-- PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:END -->

<!-- PATCHOPS_PATCH90_WORKFLOW:START -->
## Maintained update discipline

The project-packet workflow must stay explicit about update discipline.

Stable packet sections should change rarely.
Mutable packet sections should be refreshed as validated progress changes.

Packet updates should be:

- conservative,
- grounded in reports and handoff when available,
- explicit about uncertainty,
- careful not to rewrite stable sections without real reason.

For an already-running PatchOps effort:

1. handoff bundle first,
2. perform the exact next recommended action,
3. read the relevant project packet if target context is needed,
4. refresh the packet after validated progress.

This keeps project-packet updates tied to real execution evidence instead of drifting into speculative rewrites.
<!-- PATCHOPS_PATCH90_WORKFLOW:END -->
\n\n<!-- PATCHOPS_PATCH91_WORKFLOW:START -->
## Helper-first onboarding command surface

The onboarding workflow now includes a helper-first command layer that should remain explicit in the docs.

For brand-new target onboarding, the maintained helper flow is:

1. use `recommend-profile` to choose the smallest plausible profile,
2. use `init-project-doc` to create the first maintained packet,
3. use `starter` to choose the nearest manifest shape by intent,
4. use onboarding bootstrap artifacts when a compact startup bundle is helpful,
5. use `refresh-project-doc` after validated progress.

These helpers reduce ambiguity during first use.
They do not replace manifests, reports, or handoff.
<!-- PATCHOPS_PATCH91_WORKFLOW:END -->\n