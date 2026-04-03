# PatchOps

PatchOps is a **project-agnostic patch wrapper** for applying, validating, evidencing, and handing off changes to a target project.

It exists to make patch-based development safer, more repeatable, more auditable, and easier for both humans and future LLMs to continue.

PatchOps is **not** the target project.
It is the harness around the target project.

---

## Core idea

PatchOps separates four different responsibilities that should stay distinct:

- **generic PatchOps docs** teach how the wrapper works,
- **project packets** teach how one specific target project should be developed with PatchOps,
- **manifests** tell PatchOps what to do in one concrete run,
- **reports and handoff files** prove what happened and tell the next operator or LLM how to continue.

That separation is now part of the supported architecture.
Project packets are an additive onboarding layer, not a replacement for profiles, manifests, reports, or handoff bundles.

---

## What PatchOps owns

PatchOps owns the **how** of controlled change:

- profile-based target assumptions,
- manifest-driven patch execution,
- validation and rerun discipline,
- one canonical report per run,
- failure classification,
- narrow repair paths,
- and handoff surfaces for continuation.

PatchOps does **not** own the domain logic of the target repo.
Target-specific code, rules, and product behavior must remain in the target repository, target manifests, target profiles, and target-facing documentation surfaces.

---

## Supported documentation surfaces

PatchOps now has two documentation layers for LLM-oriented usage.

### 1. Generic PatchOps packet

This is the stable orientation layer that teaches the wrapper itself.
A future LLM onboarding a new target project should begin by reading the maintained generic docs, including:

- `README.md`
- `docs/overview.md`
- `docs/llm_usage.md`
- `docs/manifest_schema.md`
- `docs/profile_system.md`
- `docs/compatibility_notes.md`
- `docs/failure_repair_guide.md`
- `docs/examples.md`
- `docs/project_status.md`
- `docs/operator_quickstart.md`
- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`

### 2. Project packets

Project packets are the maintained target-facing contract inside PatchOps.
They live under:

- `docs/projects/<project_name>.md`

A project packet is:

- human-readable,
- LLM-readable,
- tied to a target root and profile,
- maintained across the life of the target project,
- separate from generic PatchOps docs,
- and separate from handoff run-state files.

Project packets should explain the target project in PatchOps terms without turning the wrapper core into a target-specific product.

---

## What remains true

The project-packet direction does **not** change the core architectural rules:

- PatchOps remains project-agnostic.
- Profiles remain the **executable target abstraction**.
- Project packets remain the **human-readable target contract**.
- PowerShell stays thin.
- Python owns reusable wrapper logic.
- One canonical report per run remains mandatory.
- Handoff remains the continuation surface for already-running work.

---

## New target-project onboarding

When starting a brand-new target project, the intended workflow is now:

1. read the generic PatchOps packet,
2. restate the target boundary and likely profile,
3. create or maintain `docs/projects/<project_name>.md`,
4. choose the closest bundled example,
5. create the first manifest,
6. run:
   - `check`
   - `inspect`
   - `plan`
   - then `apply` or `verify`,
7. inspect the canonical report,
8. update the project packet,
9. continue patch by patch.

This is the supported two-step onboarding model.

---

## Continuation of already-running work

Continuation remains separate from onboarding.

When taking over an already-running PatchOps effort, the first resume surface is still the maintained handoff bundle:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

The next operator or LLM should:

1. read the handoff files first,
2. restate the current state briefly,
3. perform the exact next recommended action,
4. read the relevant `docs/projects/<project_name>.md` only when the task is target-specific.

This keeps **onboarding** and **continuation** clearly separated.

---

## Practical usage flow

For normal operator use, the safe flow remains:

1. inspect available profiles,
2. run environment checks,
3. choose the closest example manifest,
4. create or adapt a manifest,
5. run `check`,
6. run `inspect`,
7. run `plan`,
8. run `apply` or `verify`,
9. inspect the canonical report,
10. classify the result,
11. continue with the next patch or narrow repair.

The project-packet layer is meant to make startup faster and less interpretive.
It is not meant to replace manifests, reports, or the existing command flow.

---

## Repo direction

PatchOps already supports:

- profile-based patching,
- manifest validation and planning,
- canonical reporting,
- verify-only reruns,
- wrapper-only retry handling,
- handoff-first continuation.

The current additive direction is to make **new target-project onboarding** as disciplined as continuation already is.
That is why project packets now exist as an explicit architectural concept.

---

## Bottom line

PatchOps should be understood like this:

- **generic docs** teach PatchOps,
- **project packets** teach one target project,
- **manifests** drive one run,
- **reports** prove what happened,
- **handoff files** tell the next operator or LLM how to continue.

That is the cleanest way to keep the wrapper reusable while making target-project startup faster and more mechanical.

<!-- PATCHOPS_PATCH87_README:START -->
## Current handoff operator reality

The handoff bundle is a shipped continuation surface, not just a future idea.

When resuming already-running PatchOps work, start with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

The default operator continuation flow is:

1. run `export-handoff`
2. upload the generated handoff bundle
3. paste `handoff/next_prompt.txt`

Project packets remain the target-facing contract for brand-new target-project onboarding.
They do not replace handoff for current PatchOps continuation.
<!-- PATCHOPS_PATCH87_README:END -->

<!-- PATCHOPS_PATCH88B_README:START -->
## Legacy-tested handoff wording that remains current

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

For already-running PatchOps continuation, run handoff export first and then paste `handoff/next_prompt.txt`.

Generic Python + PowerShell profile examples remain part of the maintained orientation story, including the `generic_python_powershell` profile.
<!-- PATCHOPS_PATCH88B_README:END -->

## Consolidation status

See also:

- `docs/project_status.md`
- `docs/patch_ledger.md`

PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture.
The initial buildout circle is complete enough that the repo should be treated as a maintained utility rather than an open-ended experiment.

<!-- PATCHOPS_PATCH126_README:START -->
## Final maintenance posture

PatchOps should now be treated as a maintained utility rather than an open-ended architecture buildout.

The core wrapper, handoff-first continuation, and two-step onboarding / project-packet layers are all shipped in meaningful form.
The remaining work is finalization and maintenance:

- protect shipped truth with validation,
- prove the continuation path,
- prove the onboarding path,
- run the final release / maintenance gate,
- compress the final reading set,
- export the final freeze bundle.

### Start here

For already-running PatchOps work, start with handoff artifacts when they exist:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

For a brand-new target project, start with:

- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`
- `docs/finalization_master_plan.md`
- `docs/patch_ledger.md`

This repo should now be read as a maintenance-mode wrapper, not as a greenfield architecture project.
<!-- PATCHOPS_PATCH126_README:END -->

<!-- PATCHOPS_F7_FINAL_DOC_STOP_README:START -->
## Final maintained reading order

PatchOps is now in maintenance mode after the final release / maintenance gate passed in Patch 130.

### Start here for already-running PatchOps work

1. read `handoff/current_handoff.md`
2. read `handoff/current_handoff.json`
3. read `handoff/latest_report_copy.txt`
4. then read `docs/project_status.md`
5. then read `docs/llm_usage.md`

### Start here for a brand-new target project

1. read `README.md`
2. read `docs/llm_usage.md`
3. read `docs/operator_quickstart.md`
4. read `docs/project_packet_contract.md`
5. read `docs/project_packet_workflow.md`
6. then read or create the relevant file under `docs/projects/`

### History-compression reminder

Treat the following as the final maintained reading set rather than reconstructing state from old chat history:

- `README.md`
- `docs/project_status.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `docs/examples.md`
- `docs/handoff_surface.md`
- `docs/project_packet_workflow.md`
- `docs/project_packet_contract.md`
- `docs/patch_ledger.md`
- `docs/finalization_master_plan.md`

### Scope reminder

- historical anchors explain how the repo got here,
- shipped behavior is the truth to operate from now,
- optional future work is additive only,
- target-specific extension work belongs in target packets, profiles, manifests, and target repos rather than inside generic PatchOps core logic.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_README:END -->

<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity maintenance repair

The summary-integrity repair stream established and now documents three distinct facts:

- Patch 133 was a wrapper / patch-authoring failure caused by a duplicated `content_path` resolution.
- Patch 133A was the confirmed product-bug repro: required command evidence showed failure while the rendered inner summary still showed `ExitCode : 0` and `Result   : PASS`.
- Patch 134 was a patch-authoring failure caused by malformed JSON, not evidence that the underlying engine repair was wrong.

The repair sequence through Patches 134C-134E keeps the architecture narrow:

- derive rendered summary truth from required command evidence,
- keep explicitly tolerated non-zero exits allowed through `allowed_exit_codes`,
- harden workflow-facing surfaces so CLI and handoff fail closed when stale success state contradicts required command evidence,
- treat the stream as a maintenance repair rather than a redesign.

When sources disagree during this stream, trust current repo files and current tests over historical chat reconstruction.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->

## Suspicious-run support in maintenance mode

PatchOps now includes a small suspicious-run support layer that helps operators notice when wrapper evidence and repo truth may disagree. This is a wrapper health aid, not target-project business logic. The detector and artifact helpers stay conservative, and artifact emission starts opt-in rather than default-on so the canonical one-report flow remains stable.
