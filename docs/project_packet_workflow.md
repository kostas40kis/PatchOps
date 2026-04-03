# Project packet workflow

## 1. Purpose of this document

This document defines the **two-step onboarding** workflow for a **brand-new target project** in PatchOps.

The goal is to make first-time target onboarding much more deliberate and much less interpretive.

PatchOps already has a continuation workflow for an **already-running PatchOps effort**:

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

## 2. Generic PatchOps orientation

The first step is **generic PatchOps orientation** through the generic onboarding packet.

The generic onboarding packet should include the maintained generic docs, especially:

- `README.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`

The distinction between onboarding and continuation is explicit.
The distinction between project packets and handoff is explicit.

## 3. Project packet creation and use

After the generic onboarding packet, create or refresh:

`docs/projects/<project_name>.md`

That file is the **project packet**.
It should capture target-specific understanding, while the **manifest** still describes what PatchOps should do now and the **report** still proves what happened.

For a brand-new target project, the intended flow is:

1. read the generic PatchOps packet,
2. restate what PatchOps owns,
3. restate what must remain outside PatchOps,
4. choose the most appropriate profile,
5. create `docs/projects/<project_name>.md`,
6. generate the first manifest from the closest example or starter helper,
7. run check / inspect / plan / apply or verify,
8. inspect the canonical report,
9. update the project packet,
10. continue patch by patch.

## 4. Boundary between onboarding and continuation

For a brand-new target project, start from the generic onboarding packet and the project packet workflow.

For an already-running PatchOps effort, do not start from project-packet onboarding.
Start from:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Then perform the exact next recommended action and read the relevant project packet only if target context is needed.

That separation must remain clear.

<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:START -->
## Patch 79 - self-hosted operator flow

Self-hosted operator flow should remain explicit in the docs.

For self-hosted maintenance of PatchOps itself:

1. start with current handoff when work is already in progress,
2. confirm the smallest correct profile and example posture,
3. use the same manifest-driven command order:
   - `check`
   - `inspect`
   - `plan`
   - `apply` or `verify`
4. inspect the canonical report,
5. refresh the relevant packet or handoff surface after validated progress.

This keeps self-hosted work conservative and evidence-first rather than interpretive.
<!-- PATCHOPS_PATCH80_SELF_HOSTED_COMMAND_FLOW:END -->

<!-- PATCHOPS_PATCH84_WORKFLOW_MECHANICAL:START -->
## Mechanical onboarding sequence

The onboarding sequence should be mechanical rather than interpretive.

For a brand-new target project:

1. read the generic onboarding packet,
2. create the project packet,
3. choose the smallest plausible profile,
4. select the nearest example or starter helper,
5. author the first manifest conservatively,
6. run `check`, `inspect`, and `plan`,
7. then apply or verify,
8. inspect the canonical report,
9. update the project packet.

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

<!-- PATCHOPS_PATCH91_WORKFLOW:START -->
## Helper-first onboarding command surface

The onboarding workflow now includes a helper-first onboarding command surface that should remain explicit in the docs.

For brand-new target onboarding, the maintained helper flow is:

1. use `recommend-profile` to choose the smallest plausible profile,
2. use `init-project-doc` to create the first maintained packet,
3. use `starter` to choose the nearest manifest shape by intent,
4. use onboarding bootstrap artifacts when a compact startup bundle is helpful,
5. use `refresh-project-doc` after validated progress.

These helpers reduce ambiguity during first use.
They do not replace manifests, reports, or handoff.
<!-- PATCHOPS_PATCH91_WORKFLOW:END -->

<!-- PATCHOPS_PATCH92_WORKFLOW:START -->
## Onboarding bootstrap artifact surface

The onboarding workflow now includes onboarding bootstrap artifacts that can accelerate first use for a brand-new target project.

The maintained bootstrap artifact set is:

- `onboarding/current_target_bootstrap.md`
- `onboarding/current_target_bootstrap.json`
- `onboarding/next_prompt.txt`
- `onboarding/starter_manifest.json`

These artifacts are for brand-new target onboarding.

They should summarize:
- project identity,
- target root,
- selected profile,
- project packet path,
- suggested reading order,
- recommended command order,
- initial goals when provided.

They do not replace manifests, reports, project packets, or handoff.
<!-- PATCHOPS_PATCH92_WORKFLOW:END -->

<!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:START -->
## Final onboarding-versus-continuation rule

Use the project-packet workflow only for brand-new target projects.

### Brand-new target onboarding

1. read the generic PatchOps packet,
2. read `docs/project_packet_contract.md`,
3. read `docs/project_packet_workflow.md`,
4. read or create the relevant file under `docs/projects/`,
5. choose a starter helper, template, or example,
6. continue with normal manifest-driven PatchOps work.

### Already-running PatchOps continuation

Do not start from project-packet onboarding when the work is already in progress.
Start from the handoff bundle instead and let the handoff define the next action.

### Final boundary reminder

- generic docs teach PatchOps,
- project packets teach one target project,
- manifests tell PatchOps what to do now,
- reports prove what happened,
- handoff files tell the next LLM how to continue from the latest run.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_PROJECT_PACKET_WORKFLOW:END -->

docs/projects/wrapper_self_hosted.md
bootstrap-target
Keep PowerShell thin
