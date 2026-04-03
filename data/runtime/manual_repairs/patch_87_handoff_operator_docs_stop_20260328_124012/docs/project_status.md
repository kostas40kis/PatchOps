# PatchOps project status

## 1. Purpose of this document

This document records the current interpreted status of PatchOps.

Its job is to answer four questions clearly:

1. what PatchOps already supports,
2. what should be treated as stable now,
3. what is still being added,
4. what a future LLM or operator should treat as the next active development direction.

This file should help prevent two common mistakes:

- treating older design ideas as if they were still the current plan,
- treating newly proposed onboarding features as if they were already fully implemented.

---

## 2. Current high-level interpretation

PatchOps should now be understood as a wrapper project that owns:

- patch application,
- validation,
- evidence/report generation,
- rerun and repair guidance,
- handoff support,
- and now the beginning of a stronger target-project onboarding layer.

The architectural boundary remains:

- **PatchOps** = how change is applied, validated, evidenced, retried, and handed off,
- **target repo** = what the actual project change is.

That boundary remains one of the most important rules in the repo and should not be weakened by future work. fileciteturn11file13

---

## 3. What should be treated as stable now

The following should be treated as the stable core operating model of PatchOps.

### 3.1 Profile-driven, manifest-driven execution

Profiles remain the executable abstraction for target-specific assumptions.
Manifests remain the explicit instruction surface for what PatchOps should do right now. Project packets are being added as a maintained guidance surface, but they are not a replacement for profiles or manifests. fileciteturn11file9turn11file1

### 3.2 Thin PowerShell, reusable Python

PowerShell remains a thin operator-facing surface.
Reusable workflow logic should continue to live in Python-owned surfaces rather than being duplicated in launcher scripts. This remains a hard architectural rule for the project. fileciteturn11file9turn11file14

### 3.3 One canonical report per run

PatchOps should continue producing one canonical evidence artifact per run.
The report contract should stay explicit and should not be weakened for documentation-only work, maintenance work, or future onboarding-related features. fileciteturn11file9turn11file14

### 3.4 Handoff-first continuation for already-running work

For takeover of an already-running PatchOps effort, the expected start point remains the handoff bundle:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

If the task is target-specific, the relevant project packet should then be read as an additional surface rather than as a replacement for handoff. fileciteturn11file5

### 3.5 Practical operator workflow

The shortest safe working flow still starts with:

- profiles,
- doctor,
- examples,
- template,
- check,
- inspect,
- plan,
- then apply or verify.

That practical flow remains a core usage story for the wrapper. fileciteturn11file7

---

## 4. What is established but should not be confused with the new work

PatchOps already has an explicit handoff-oriented direction.
That handoff direction was introduced so a future LLM can resume from concrete repo-generated state instead of rebuilding context from scattered documents. The current project-packet work does not replace that. It extends the onboarding story for brand-new target projects. fileciteturn11file15

Simple rule:

- use **handoff files** to resume active work,
- use **project packets** to understand a specific target project,
- use **manifests** to tell PatchOps what to do now,
- use the **report** to prove what happened.

That separation should remain explicit in all future docs and code. fileciteturn11file1turn11file5

---

## 5. Active development direction now

The active additive direction is the **two-step onboarding / project-packet buildout**.

This direction introduces a new first-class concept:

- the **project packet**

A project packet is intended to live under:

- `docs/projects/<project_name>.md`

and acts as the maintained target-facing contract that sits between:

- the generic PatchOps docs,
- and the target project being developed with PatchOps. fileciteturn11file9

The project-packet direction is meant to make new target-project startup faster without redesigning PatchOps into a different kind of product. The plan explicitly says this should be an additive feature, not a rewrite. fileciteturn11file5turn11file9

---

## 6. What the new project-packet layer is supposed to do

The project-packet layer is intended to make future onboarding more mechanical.

For a brand-new target project, the desired future flow is:

1. read the generic PatchOps packet,
2. restate what PatchOps owns,
3. restate what must remain outside PatchOps,
4. choose the most appropriate profile,
5. create `docs/projects/<project_name>.md`,
6. generate the first manifest from the closest example or starter helper,
7. run check / inspect / plan / apply or verify,
8. inspect the canonical report,
9. update the project packet,
10. continue patch by patch. fileciteturn11file3turn11file12

This means the project-packet layer is meant to reduce blank-page startup work while preserving the existing profile, manifest, report, and handoff model. fileciteturn11file5

---

## 7. What is already added in the new direction

The current project-packet rollout begins with documentation-first surfaces.
The intended safest first implementation order is:

1. `docs/project_packet_contract.md`
2. `docs/project_packet_workflow.md`
3. refresh `docs/llm_usage.md`
4. add `docs/projects/`
5. create `docs/projects/trader.md`
6. add tests for the new docs and packet structure
7. only then add generator/refresh CLI support. fileciteturn11file5

That means the correct interpretation is:

- the project-packet concept should now be treated as an explicit supported direction,
- but the full onboarding packet system should not yet be described as fully shipped until the later packet, test, and helper patches are completed.

---

## 8. What is not yet complete

The following should still be treated as incomplete or future-facing until their patches are finished.

### 8.1 First maintained packet examples

The planned first serious packet example is:

- `docs/projects/trader.md`

with explicit target root, wrapper root, runtime, selected profile, boundary rules, recommended manifests, phased guidance, and current status. fileciteturn11file0

### 8.2 Packet contract tests

The planned documentation and packet tests include:

- `tests/test_project_packet_contract_doc.py`
- `tests/test_project_packet_examples.py`

These are meant to prevent the new workflow from drifting into vague documentation. fileciteturn11file0turn11file12

### 8.3 Packet generation and refresh support

The intended reusable support layer is expected in Python-owned surfaces such as:

- `patchops/project_packets.py`
- `patchops/cli.py`

This support is intended to scaffold starter packets and refresh mutable sections conservatively from known state such as handoff files and report metadata. fileciteturn11file0turn11file12

### 8.4 Faster first-use onboarding helpers

The later onboarding layer is expected to add:

- onboarding bootstrap artifacts,
- profile recommendation help,
- starter-manifest helpers by intent.

That work belongs to the later phase of the plan and should not be described as present before those patches exist. fileciteturn11file3turn11file12

---

## 9. Stable interpretation rules for future LLMs

A future LLM should preserve the following interpretation rules.

1. Do not move target-project business logic into PatchOps. fileciteturn11file13
2. Do not let project packets replace profiles, manifests, reports, or handoff files. fileciteturn11file1turn11file9
3. Do not let PowerShell become the home of reusable wrapper logic. fileciteturn11file9turn11file14
4. Do not weaken the one-report evidence model just because the work is documentation-heavy. fileciteturn11file9turn11file14
5. Prefer additive change over broad redesign. fileciteturn11file9turn11file15

---

## 10. Recommended current reading order

For a future LLM onboarding to PatchOps generally, the intended generic packet includes:

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
12. `docs/project_packet_workflow.md` fileciteturn11file9turn11file13

For takeover of an already-running PatchOps effort, read the handoff bundle first, then read the relevant project packet if the task is target-specific. fileciteturn11file5

---

## 11. Recommended next development direction

The next correct additive direction is:

1. finish making project-packet architecture explicit in the main docs,
2. add `docs/projects/` as a first-class surface,
3. create the first maintained project packet,
4. add tests for packet docs and packet examples,
5. only then add reusable generator and refresh support.

That sequence keeps the rollout controlled and aligned with the plan’s recommended first implementation order. fileciteturn11file5

---

## 12. Bottom line

PatchOps should currently be understood as:

- a stable manifest-driven wrapper,
- with explicit profile, report, validation, rerun, and handoff behavior,
- and with a new project-packet onboarding layer being added in a conservative, additive way.

The project is not trying to replace its existing handoff system.
It is trying to make new target-project startup as teachable and mechanical as continuation already is.

That is the correct status interpretation to preserve until the later project-packet phases are actually implemented. fileciteturn11file5turn11file9

<!-- PATCHOPS_PATCH76_PROJECT_PACKET_ROLLOUT_STATUS:START -->
## Project packet rollout status

Project packets are now an explicit supported direction for PatchOps.

### Shipped now

- `docs/project_packet_contract.md` defines the packet contract,
- `docs/project_packet_workflow.md` defines the two-step onboarding workflow,
- `docs/projects/` is the official home for maintained target packets,
- `docs/projects/trader.md` exists as the first serious maintained packet example,
- packet wording tests exist and are passing.

### What this means operationally

Project packets are now part of the practical usage story.
They help future LLMs and operators understand a target project faster without moving target business logic into the PatchOps core.

### Not shipped yet

The generation and refresh support proposed for later work is still future work.
That means project-packet scaffold helpers, packet refresh helpers, and any related CLI support should still be treated as the next additive phase rather than already-complete behavior.
<!-- PATCHOPS_PATCH76_PROJECT_PACKET_ROLLOUT_STATUS:END -->

<!-- PATCH_79_SELF_HOSTED_STATUS_START -->
## Patch 79 - self-hosted operator guidance status

### Current state

- Patch 79 adds self-hosted operator guidance instead of widening the PowerShell layer.
- Project-packet scaffold and refresh commands now have a documented operator flow.
- `docs/projects/wrapper_self_hosted.md` becomes the maintained packet for PatchOps acting as its own current target.

### Why this matters

- operator usage remains simple,
- reusable logic stays in Python,
- self-hosted work now follows the same project-packet model as other targets.

### Next planned step

- Patch 80 should refresh `docs/project_packet_workflow.md`, `docs/operator_quickstart.md`, and `docs/project_status.md` as the formal Documentation Stop P-C once this patch passes.
<!-- PATCH_79_SELF_HOSTED_STATUS_END -->

<!-- PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:START -->
## Project-packet rollout status

### Shipped now

- project-packet contract and workflow docs,
- `docs/projects/` as the official packet home,
- `docs/projects/trader.md` as the first maintained target packet,
- `docs/projects/wrapper_self_hosted.md` as the self-hosted packet,
- packet contract tests,
- `init-project-doc` scaffold support,
- `refresh-project-doc` mutable-state refresh support,
- operator guidance for self-hosted project-packet use.

### Still planned

- onboarding bootstrap artifacts,
- profile recommendation helper,
- starter helper by intent,
- final onboarding documentation stop.

### Current interpretation

The project-packet layer is now real and operator-usable.
The remaining work is about making startup even more mechanical, not about redesigning the architecture.
<!-- PATCHOPS_PATCH80_PROJECT_PACKET_STATUS:END -->

<!-- PATCHOPS_PATCH84_STATUS_FINALIZATION:START -->
## Project-packet rollout status after Documentation Stop P-D

### Shipped now

- project-packet contract and workflow docs,
- maintained project-packet examples under `docs/projects/`,
- scaffold and refresh helpers,
- onboarding bootstrap artifacts,
- profile recommendation helper,
- starter helper by intent,
- operator-facing documentation connecting onboarding and continuation,
- tests protecting the packet, workflow, helper, and command surfaces.

### Practical interpretation

The onboarding layer is now substantially complete:
- generic docs teach PatchOps,
- project packets teach one target,
- helper commands reduce ambiguity during first use,
- handoff remains the resume surface for already-running work.

### Remaining posture

Further changes after this point should be maintenance, refinement, or target-specific expansion rather than architectural redesign.
<!-- PATCHOPS_PATCH84_STATUS_FINALIZATION:END -->

<!-- PATCHOPS_PATCH85_STATUS:START -->
## Patch 85 - onboarding helper roundtrip validation

### Current state

- Patch 85 adds one combined validation test for the helper-first onboarding flow.
- The new test exercises `recommend-profile`, `init-project-doc`, `starter`, and `refresh-project-doc` in one conservative roundtrip.
- The goal is to protect helper alignment as a maintained operator-visible flow without widening the architecture.

### Why this matters

- the onboarding layer is now protected as one practical flow, not only as isolated helper surfaces,
- the patch stays maintenance-sized and validation-first,
- handoff remains the resume surface for already-running work.

### Remaining posture

- continue with maintenance, refinement, or target-specific expansion,
- prefer narrow validation or repair patches before any new architecture work.
<!-- PATCHOPS_PATCH85_STATUS:END -->

<!-- PATCHOPS_PATCH86_STATUS:START -->
## Patch 86 - handoff failure-mode validation

### Current state

- Patch 86 adds targeted handoff failure-mode tests.
- The new validation covers:
  - missing report path -> fail closed,
  - missing bundled prompt -> recreated on re-export,
  - missing top-level index -> recreated on re-export,
  - stale prompt after state change -> refreshed on re-export.
- The patch stays within maintenance/refinement posture after the Patch 84 onboarding stop and the Patch 85 onboarding helper roundtrip validation.

### Why this matters

- continuation becomes more trustworthy in realistic self-hosted rerun conditions,
- export-handoff behavior is protected against stale or partially missing artifacts,
- the repo keeps improving through narrow validation patches instead of broad redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer the smallest test or repair patch that closes a real workflow gap.
<!-- PATCHOPS_PATCH86_STATUS:END -->

<!-- PATCHOPS_PATCH86C_STATUS:START -->
## Patch 86C - function-level handoff test repair

### Current state

- Patch 86C repairs the failed Patch 86B repair attempt.
- The new patcher replaces the failing handoff test by function name instead of relying on one exact text block.
- The repaired assertion path now matches the shipped handoff contract:
  - direct export payload -> prompt path and continuation fields,
  - latest report copy path -> indexed handoff surface.

### Why this matters

- the repair becomes resilient to local formatting drift,
- the handoff failure-mode coverage remains useful,
- the repo continues through narrow contract repair instead of wider code changes.

### Remaining posture

- continue with narrow maintenance and refinement patches,
- prefer robust patchers when fixing test-only drift in already-shipped surfaces.
<!-- PATCHOPS_PATCH86C_STATUS:END -->
