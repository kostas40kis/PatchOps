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

<!-- PATCHOPS_PATCH87_PROJECT_STATUS:START -->
## Patch 87 - handoff operator docs stop

### Current state

- Patch 87 refreshes the operator-facing handoff docs after the repaired handoff failure-mode tests are green.
- The docs now describe handoff export and `handoff/next_prompt.txt` as shipped continuation surfaces.
- The docs also keep the distinction explicit:
  - handoff = current run-state and next action,
  - project packets = target-facing contract for new target onboarding.

### Why this matters

- future LLMs and operators no longer need to infer whether handoff export is still future work,
- current continuation flow is documented as current reality,
- the repo stays in maintenance/refinement posture instead of drifting back into stale roadmap language.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- treat the old handoff redesign stream as implemented and now maintained.
<!-- PATCHOPS_PATCH87_PROJECT_STATUS:END -->

<!-- PATCHOPS_PATCH88_STATUS:START -->
## Patch 88 - handoff example usage docs refresh

### Current state

- Patch 88 refreshes `docs/examples.md` for the current handoff-first continuation flow.
- The examples now show how to run `export-handoff`, which files are expected under `handoff/`, and when handoff should be used instead of project-packet onboarding.
- This keeps the handoff redesign sequence moving through small documentation patches after the green validation wave.

### Why this matters

- examples now match the current CLI and handoff surfaces,
- continuation guidance is easier to follow mechanically,
- onboarding and continuation remain clearly separated.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- treat the old handoff-redesign stream as implemented and now maintained.
<!-- PATCHOPS_PATCH88_STATUS:END -->

<!-- PATCHOPS_PATCH88B_PROJECT_STATUS:START -->
## Current state snapshot

PatchOps is in late Stage 1 / pre-Stage 2 and should be treated as a maintained wrapper utility.

This section preserves older snapshot language that is still intentionally tested, while remaining accurate for the current repo state.

### Stable now

The following exists in the repo today:

- verification-only reruns,
- wrapper-only retry classification support,
- `powershell/Invoke-PatchVerify.ps1`,
- `patchops.cli examples`,
- the handoff-first continuation surface completed through Patch 69,
- the later maintenance patches that keep the handoff surface current.

### What remains future work rather than current behavior

This section preserves the distinction between shipped behavior and future work, not yet shipped behavior.

The project should still describe what remains future work rather than current behavior, especially when discussing additive follow-on improvements beyond the current maintained continuation flow.

### Historical anchors that still matter

- Patch 41 remains the profile-surface reference point for `generic_python_powershell`.
- Patch 48 remains the final initial-milestone gate reference point.
- Later handoff work should preserve these anchors rather than flatten the earlier project history.

### Current continuation shorthand

For the already-running handoff-first UX, the operator can now run one export command and paste one generated prompt.
<!-- PATCHOPS_PATCH88B_PROJECT_STATUS:END -->
\n\n<!-- PATCHOPS_PATCH89_STATUS:START -->
## Patch 89 - project-packet workflow boundary validation

### Current state

- Patch 89 adds a doc-contract validation test for the onboarding-versus-continuation boundary.
- The new test reads `docs/project_packet_workflow.md`, `docs/llm_usage.md`, `docs/operator_quickstart.md`, and `docs/project_packet_contract.md`.
- The goal is to keep the current architecture legible:
  - handoff first for already-running PatchOps continuation,
  - generic packet plus project packet for brand-new target onboarding.

### Why this matters

- the most important workflow distinction now has an explicit test,
- continuation and onboarding remain separate in the docs,
- the repo continues through narrow maintenance patches rather than broader redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the architecture is already shipped and the main risk is wording drift.
<!-- PATCHOPS_PATCH89_STATUS:END -->\n

<!-- PATCHOPS_PATCH89B_STATUS:START -->
## Patch 89B - operator quickstart boundary phrase repair

### Current state

- Patch 89B repairs the single missing phrase exposed by Patch 89.
- `docs/operator_quickstart.md` now explicitly says `already-running PatchOps work`.
- The onboarding-versus-continuation boundary remains documentation-driven and test-protected.

### Why this matters

- the boundary test now matches the intended operator wording,
- the repair stays narrow and honest,
- continuation and onboarding remain clearly separated.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer tiny doc-contract repairs when the behavior is already correct.
<!-- PATCHOPS_PATCH89B_STATUS:END -->

<!-- PATCHOPS_PATCH90_STATUS:START -->
## Patch 90 - project-packet update discipline validation

### Current state

- Patch 90 adds a doc-contract test for project-packet update discipline.
- The docs now keep three things explicit and testable:
  - stable sections change rarely,
  - mutable sections refresh with validated progress,
  - packet updates should stay grounded in reports and handoff.

### Why this matters

- the onboarding layer remains usable without encouraging packet rewrites detached from evidence,
- the packet-update story is now protected as a maintained rule,
- the repo keeps moving through narrow maintenance patches after the substantially complete onboarding rollout.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the main risk is wording drift rather than missing architecture.
<!-- PATCHOPS_PATCH90_STATUS:END -->
\n\n<!-- PATCHOPS_PATCH91_STATUS:START -->
## Patch 91 - onboarding helper docs alignment validation

### Current state

- Patch 91 adds a narrow doc-contract test for the helper-first onboarding command surface.
- The maintained docs now keep the helper story explicit:
  - `recommend-profile`,
  - `init-project-doc`,
  - `starter`,
  - onboarding bootstrap artifacts,
  - `refresh-project-doc`.

### Why this matters

- the operator-visible onboarding path stays aligned with the shipped helper layer,
- onboarding remains distinct from handoff-first continuation,
- the repo continues through maintenance validation rather than wider redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer validation patches when the main risk is wording drift across maintained docs.
<!-- PATCHOPS_PATCH91_STATUS:END -->\n\n<!-- PATCHOPS_PATCH92_STATUS:START -->
## Patch 92 - onboarding bootstrap docs alignment validation

### Current state

- Patch 92 adds a narrow doc-contract test for the onboarding bootstrap artifact surface.
- The maintained docs now keep the bootstrap outputs explicit:
  - `onboarding/current_target_bootstrap.md`,
  - `onboarding/current_target_bootstrap.json`,
  - `onboarding/next_prompt.txt`,
  - `onboarding/starter_manifest.json`.

### Why this matters

- the faster first-use onboarding surface is now documented as a maintained operator story,
- bootstrap guidance stays distinct from handoff-first continuation,
- the repo continues through maintenance validation instead of bigger redesign work.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the feature already exists and the main risk is wording drift.
<!-- PATCHOPS_PATCH92_STATUS:END -->\n\n<!-- PATCHOPS_PATCH93_STATUS:START -->
## Patch 93 - project-packet examples alignment validation

### Current state

- Patch 93 adds a narrow validation surface for the maintained project-packet examples.
- The trader packet and the wrapper self-hosted packet now both keep the core packet-example reminders explicit:
  - roots,
  - selected profile,
  - target boundary wording,
  - next recommended action,
  - handoff-first continuation when work is already in progress.

### Why this matters

- the maintained packet examples stay aligned with the packet contract and onboarding story,
- the first serious target packet and the self-hosted packet remain usable as operator-facing references,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the packet layer is already shipped and the main risk is wording drift.
<!-- PATCHOPS_PATCH93_STATUS:END -->\n\n<!-- PATCHOPS_PATCH94_STATUS:START -->
## Patch 94 - onboarding bootstrap artifact contract validation

### Current state

- Patch 94 adds a direct contract test for the actual onboarding bootstrap outputs.
- The new test proves the current artifact set remains stable:
  - `current_target_bootstrap.md`,
  - `current_target_bootstrap.json`,
  - `next_prompt.txt`,
  - `starter_manifest.json`.

### Why this matters

- the repo now protects the generated onboarding artifacts themselves, not only the docs around them,
- the faster first-use onboarding surface stays grounded in a concrete test,
- the onboarding layer remains in maintenance/refinement posture.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the feature already exists and the main risk is contract drift.
<!-- PATCHOPS_PATCH94_STATUS:END -->\n

<!-- PATCHOPS_PATCH94B_STATUS:START -->
## Patch 94B - onboarding bootstrap path contract repair

### Current state

- Patch 94B repairs the single failing assertion introduced by Patch 94.
- The bootstrap artifact test now matches the current starter-manifest path-format contract.
- The repair stays on the validation surface and does not widen the bootstrap implementation.

### Why this matters

- the onboarding bootstrap validation wave stays green without redesigning an already-shipped surface,
- the path expectation now matches the actual generated artifact,
- maintenance continues through small honest repairs.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer test-contract repairs when a new test drifted from the current implementation contract.
<!-- PATCHOPS_PATCH94B_STATUS:END -->

<!-- PATCHOPS_PATCH94C_STATUS:START -->
## Patch 94C - onboarding bootstrap payload contract repair

### Current state

- Patch 94C repairs the remaining failing assertion from the Patch 94 validation wave.
- The bootstrap artifact test now matches the current direct payload contract:
  - `written`,
  - returned artifact paths,
  - generated markdown and JSON surfaces for profile identity.

### Why this matters

- the onboarding bootstrap validation wave can finish without widening the shipped implementation,
- the direct payload expectations now match the already-proven bootstrap contract,
- maintenance continues through small honest repairs.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer test-contract repairs when a new test drifts from the current implementation contract.
<!-- PATCHOPS_PATCH94C_STATUS:END -->

<!-- PATCHOPS_PATCH95_STATUS:START -->
## Patch 95 - refresh-project-doc CLI contract validation

### Current state

- Patch 95 adds a direct CLI-contract test for `refresh-project-doc`.
- The new test protects the operator-facing refresh shape:
  - packet path,
  - handoff JSON path,
  - report path,
  - mutable-state override flags,
  - blocker input.

### Why this matters

- packet refresh remains explicitly grounded in handoff and report artifacts,
- operator usage stays visible and test-protected,
- the repo continues through narrow maintenance validation instead of broader redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped surfaces.
<!-- PATCHOPS_PATCH95_STATUS:END -->

<!-- PATCHOPS_PATCH95B_STATUS:START -->
## Patch 95B - refresh-project-doc help contract repair

### Current state

- Patch 95B repairs the failing help-text assertion introduced by Patch 95.
- The test now matches the live `refresh-project-doc --help` surface instead of expecting a newer description string.
- The repair also aligns the new test with the current `--risk` flag name shown by the live CLI help.

### Why this matters

- the refresh CLI validation stays useful without forcing a CLI wording change,
- the test now follows the shipped surface,
- maintenance continues through small honest repairs.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer test-contract repairs when a new test drifted from live operator output.
<!-- PATCHOPS_PATCH95B_STATUS:END -->

<!-- PATCHOPS_PATCH96_STATUS:START -->
## Patch 96 - helper CLI help contract validation

### Current state

- Patch 96 adds a direct CLI-help contract test for the remaining small helper-first commands.
- The new test protects:
  - `recommend-profile`,
  - `starter`.

### Why this matters

- the helper-first onboarding surface is now protected at both behavior and live help levels,
- operator-facing usage stays visible and test-backed,
- the repo continues through narrow maintenance validation instead of broader redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped helper surfaces.
<!-- PATCHOPS_PATCH96_STATUS:END -->

<!-- PATCHOPS_PATCH97_STATUS:START -->
## Patch 97 - init-project-doc help contract validation

### Current state

- Patch 97 adds a direct CLI-help contract test for `init-project-doc`.
- The new test protects the live scaffold-help shape used by the helper-first onboarding flow.

### Why this matters

- the remaining first-use packet scaffold command is now covered at the operator-help level,
- helper-first onboarding stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped helper surfaces.
<!-- PATCHOPS_PATCH97_STATUS:END -->

<!-- PATCHOPS_PATCH98_STATUS:START -->
## Patch 98 - export-handoff help contract validation

### Current state

- Patch 98 adds a direct CLI-help contract test for `export-handoff`.
- The new test protects the live handoff-export help shape used by the handoff-first continuation flow.

### Why this matters

- the resume-surface export command is now covered at the operator-help level,
- handoff-first continuation stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH98_STATUS:END -->

<!-- PATCHOPS_PATCH99_STATUS:START -->
## Patch 99 - bootstrap-target help contract validation

### Current state

- Patch 99 adds a direct CLI-help contract test for `bootstrap-target`.
- The new test protects the live bootstrap-target help shape used by the onboarding bootstrap flow.

### Why this matters

- the bootstrap-target operator surface is now covered at the help-contract level,
- onboarding bootstrap remains visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH99_STATUS:END -->

<!-- PATCHOPS_PATCH100_STATUS:START -->
## Patch 100 - template help contract validation

### Current state

- Patch 100 adds a direct CLI-help contract test for `template`.
- The new test protects the live starter-template help shape used by the operator-facing manifest bootstrap flow.

### Why this matters

- the template command is now covered at the help-contract level,
- starter-manifest generation stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH100_STATUS:END -->

<!-- PATCHOPS_PATCH101_STATUS:START -->
## Patch 101 - doctor help contract validation

### Current state

- Patch 101 adds a direct CLI-help contract test for `doctor`.
- The new test protects the live doctor help shape used by the operator-facing readiness-inspection flow.

### Why this matters

- the doctor command is now covered at the help-contract level,
- readiness inspection stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH101_STATUS:END -->

<!-- PATCHOPS_PATCH102_STATUS:START -->
## Patch 102 - examples help contract validation

### Current state

- Patch 102 adds a direct CLI-help contract test for `examples`.
- The new test protects the live examples help shape used by the operator-facing example-discovery flow.

### Why this matters

- the examples command is now covered at the help-contract level,
- example discovery stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH102_STATUS:END -->

<!-- PATCHOPS_PATCH103_STATUS:START -->
## Patch 103 - schema help contract validation

### Current state

- Patch 103 adds a direct CLI-help contract test for `schema`.
- The new test protects the live manifest-reference help surface used by operators and future LLMs.

### Why this matters

- the schema command is now covered at the help-contract level,
- manifest-reference discovery stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH103_STATUS:END -->

<!-- PATCHOPS_PATCH104_STATUS:START -->
## Patch 104 - release-readiness help contract validation

### Current state

- Patch 104 adds a direct CLI-help contract test for `release-readiness`.
- The new test protects the live readiness help shape used by the operator-facing freeze/release-readiness flow.

### Why this matters

- the release-readiness command is now covered at the help-contract level,
- readiness reporting stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH104_STATUS:END -->

<!-- PATCHOPS_PATCH105_STATUS:START -->
## Patch 105 - release-readiness report artifact contract validation

### Current state

- Patch 105 adds a direct contract test for the `release-readiness` evidence artifact.
- The new test protects the current `--report-path` surface:
  - resolved report path in JSON,
  - deterministic readiness heading,
  - focused profile line,
  - status line,
  - core-tests line,
  - notes footer.

### Why this matters

- the readiness evidence file is now protected as a current operator-facing surface,
- release/freeze reporting stays deterministic and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH105_STATUS:END -->

<!-- PATCHOPS_PATCH106_STATUS:START -->
## Patch 106 - profiles help contract validation

### Current state

- Patch 106 adds a direct CLI-help contract test for `profiles`.
- The new test protects the live profile-summary help shape used by operators and future LLMs.

### Why this matters

- the profiles command is now covered at the help-contract level,
- profile discovery stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH106_STATUS:END -->

<!-- PATCHOPS_PATCH107_STATUS:START -->
## Patch 107 - check help contract validation

### Current state

- Patch 107 adds a direct CLI-help contract test for `check`.
- The new test protects the live manifest-validation help surface used before apply or verify.

### Why this matters

- the `check` command is now covered at the help-contract level,
- starter-placeholder validation stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH107_STATUS:END -->

<!-- PATCHOPS_PATCH108_STATUS:START -->
## Patch 108 - inspect help contract validation

### Current state

- Patch 108 adds a direct CLI-help contract test for `inspect`.
- The new test protects the existence and stable help surface of the inspect step in the current operator flow.

### Why this matters

- the `check -> inspect -> plan` sequence is now more fully protected,
- the inspect command stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is operator-surface drift.
<!-- PATCHOPS_PATCH108_STATUS:END -->

<!-- PATCHOPS_PATCH109_STATUS:START -->
## Patch 109 - plan help contract validation

### Current state

- Patch 109 adds a direct CLI-help contract test for `plan`.
- The new test protects the live planning help shape used after `check` and `inspect` and before apply or verify flows.

### Why this matters

- the `plan` command is now covered at the help-contract level,
- preview planning stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH109_STATUS:END -->

<!-- PATCHOPS_PATCH110_STATUS:START -->
## Patch 110 - apply help contract validation

### Current state

- Patch 110 adds a direct CLI-help contract test for `apply`.
- The new test protects the live execution-entry help surface used after planning is complete.

### Why this matters

- the `apply` command is now covered at the help-contract level,
- core execution entry stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH110_STATUS:END -->

<!-- PATCHOPS_PATCH111_STATUS:START -->
## Patch 111 - verify help contract validation

### Current state

- Patch 111 adds a direct CLI-help contract test for `verify`.
- The new test protects the live verify-only entry surface used for rerun-safe validation flows.

### Why this matters

- the `verify` command is now covered at the help-contract level,
- the verify-only operator entry stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH111_STATUS:END -->

<!-- PATCHOPS_PATCH112_STATUS:START -->
## Patch 112 - wrapper-retry help contract validation

### Current state

- Patch 112 adds a direct CLI-help contract test for `wrapper-retry`.
- The new test protects the live wrapper-only retry entry surface used for narrow self-hosted recovery flows.

### Why this matters

- the `wrapper-retry` command is now covered at the help-contract level,
- wrapper-only retry stays visible and test-backed,
- the repo continues through narrow maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH112_STATUS:END -->

<!-- PATCHOPS_PATCH113_STATUS:START -->
## Patch 113 - core execution help-contract inventory validation

### Current state

- Patch 113 adds a narrow inventory test for the core execution-entry help-contract wave.
- The new test keeps two things explicit:
  - the shipped parser still exposes `apply`, `verify`, and `wrapper-retry`,
  - the matching help-contract tests remain present.

### Why this matters

- the core execution-entry trilogy is now protected as a maintained group instead of only as isolated tests,
- future command-surface changes are more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small validation patches when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH113_STATUS:END -->

<!-- PATCHOPS_PATCH114_STATUS:START -->
## Patch 114 - root help contract validation

### Current state

- Patch 114 adds a direct CLI-help contract test for the root `patchops --help` entry.
- The new test protects the maintained operator-visible command map as a whole.

### Why this matters

- the root command index is now covered at the help-contract level,
- future drift in the top-level operator surface is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small contract tests when the main risk is CLI/help drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH114_STATUS:END -->

<!-- PATCHOPS_PATCH115_STATUS:START -->
## Patch 115 - PowerShell launcher inventory validation

### Current state

- Patch 115 adds a narrow inventory test for the maintained PowerShell launcher surface.
- The new test protects the main thin launcher set used across:
  - apply / verify,
  - wrapper-only retry,
  - release readiness,
  - discovery and authoring flows.

### Why this matters

- the documented launcher layer stays explicit and test-backed,
- future launcher drift is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small inventory or contract tests when the main risk is operator-surface drift across already-shipped tooling.
<!-- PATCHOPS_PATCH115_STATUS:END -->

<!-- PATCHOPS_PATCH116_STATUS:START -->
## Patch 116 - secondary PowerShell launcher inventory validation

### Current state

- Patch 116 adds a narrow inventory test for the remaining thin PowerShell launcher surfaces.
- The new test protects the maintained launcher set for:
  - handoff export,
  - manifest/schema discovery,
  - manifest inspection.

### Why this matters

- the secondary launcher layer stays explicit and test-backed,
- future drift in these already-shipped operator surfaces is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small inventory or contract tests when the main risk is operator-surface drift across already-shipped tooling.
<!-- PATCHOPS_PATCH116_STATUS:END -->

<!-- PATCHOPS_PATCH117_STATUS:START -->
## Patch 117 - operator subcommand inventory validation

### Current state

- Patch 117 adds a narrow parser-inventory test for the maintained operator subcommand surface.
- The new test protects the shipped subcommand map independently of help-text wording.

### Why this matters

- the maintained operator surface now has a parser-level inventory check,
- future command-map drift is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small inventory or contract tests when the main risk is operator-surface drift across already-shipped tooling.
<!-- PATCHOPS_PATCH117_STATUS:END -->

<!-- PATCHOPS_PATCH118_STATUS:START -->
## Patch 118 - CLI and PowerShell surface alignment validation

### Current state

- Patch 118 adds a narrow alignment test for the launcher-backed operator surface.
- The new test protects the maintained mapping between:
  - shipped CLI commands,
  - thin PowerShell launchers.

### Why this matters

- launcher-backed operator entry points now stay aligned as one maintained surface,
- future drift between CLI and launcher layers is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small alignment or contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH118_STATUS:END -->

<!-- PATCHOPS_PATCH119_STATUS:START -->
## Patch 119 - Python-only helper surface boundary validation

### Current state

- Patch 119 adds a narrow boundary test for the helper-first Python-only command layer.
- The new test keeps two things explicit:
  - the shipped helper commands still exist,
  - the helper-first layer remains Python-owned rather than gaining new thin PowerShell wrappers.

### Why this matters

- the onboarding helper boundary now stays explicit and test-backed,
- future drift toward unnecessary PowerShell expansion is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small boundary or contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH119_STATUS:END -->

<!-- PATCHOPS_PATCH120_STATUS:START -->
## Patch 120 - operator surface partition validation

### Current state

- Patch 120 adds a narrow partition test for the maintained operator command map.
- The new test keeps three things explicit:
  - launcher-backed commands remain one maintained group,
  - Python-only helper commands remain a separate maintained group,
  - together they still cover the current operator-facing surface.

### Why this matters

- the operator map is now protected as an explicit partition instead of only as separate inventories,
- future drift across launcher-backed versus Python-only boundaries is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small partition, inventory, or contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH120_STATUS:END -->

<!-- PATCHOPS_PATCH121_STATUS:START -->
## Patch 121 - exact PowerShell launcher set validation

### Current state

- Patch 121 adds a narrow exact-set test for the maintained thin PowerShell launcher layer.
- The new test keeps explicit that the launcher surface is not only present but also bounded.

### Why this matters

- the shipped launcher layer now fails on both missing and unexpected launcher drift,
- future PowerShell expansion is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small exact-set, boundary, or contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH121_STATUS:END -->

<!-- PATCHOPS_PATCH122_STATUS:START -->
## Patch 122 - operator surface status doc validation

### Current state

- Patch 122 adds a narrow documentation-validation test for the recent operator-surface hardening wave.
- The new test protects the maintained status surfaces that describe:
  - launcher-backed alignment,
  - Python-only helper boundaries,
  - operator-surface partitioning,
  - exact thin PowerShell launcher bounds.

### Why this matters

- the recent maintenance wave now stays explicit in both code-facing and doc-facing surfaces,
- future doc drift is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small boundary, inventory, or doc-contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH122_STATUS:END -->

<!-- PATCHOPS_PATCH123_STATUS:START -->
## Patch 123 - exact CLI subcommand set validation

### Current state

- Patch 123 adds a narrow exact-set test for the shipped CLI subcommand surface.
- The new test keeps explicit that the maintained operator-facing command map is not only partitioned and inventoried, but also bounded.

### Why this matters

- the shipped CLI now fails on both missing and unexpected subcommand drift,
- future operator-surface expansion is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small exact-set, boundary, inventory, or contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH123_STATUS:END -->

<!-- PATCHOPS_PATCH124_STATUS:START -->
## Patch 124 - exact operator surface doc validation

### Current state

- Patch 124 adds a narrow documentation-validation test for the recent exact-boundary operator-surface wave.
- The new test protects the maintained status surfaces that describe:
  - exact thin PowerShell launcher bounds,
  - exact CLI subcommand bounds,
  - the latest operator-surface maintenance posture.

### Why this matters

- the exact-boundary maintenance wave now stays explicit in both code-facing and doc-facing surfaces,
- future doc drift is more likely to trigger a narrow honest repair,
- the repo continues through maintenance validation rather than redesign.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small exact-set, boundary, inventory, or doc-contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH124_STATUS:END -->

<!-- PATCHOPS_PATCH125A_STATUS:START -->
## Patch 125A - truth-reset doc contract repair

### Current state

- Patch 125A repairs the narrow documentation regressions exposed by the truth-reset audit.
- The maintained status surface is again explicit about the exact thin PowerShell launcher set.
- The maintained status surface again uses the exact-set test for the shipped CLI subcommand surface wording.
- The maintained status surface again keeps explicit that the operator-facing command map is not only partitioned and inventoried, but also bounded.

### Why this matters

- the repo remains in late Stage 1 / pre-Stage 2 maintenance posture,
- the recent maintenance wave continues through maintenance validation rather than redesign,
- future doc drift is more likely to trigger a narrow honest repair.

### Remaining posture

- continue with narrow maintenance, refinement, or target-specific expansion,
- prefer small exact-set, boundary, inventory, or doc-contract tests when the main risk is drift across already-shipped operator surfaces.
<!-- PATCHOPS_PATCH125A_STATUS:END -->

<!-- PATCHOPS_PATCH126_STATUS:START -->
## Patch 126 - final self-contained master documentation

This patch refreshes the self-contained operator/LLM documentation set after the truth-reset repair wave.

### Current interpreted posture

- latest confirmed green head: Patch 129
- the truth-reset blocker found by Patch 125 was repaired by Patch 125A and Patch 125B
- PatchOps is in a maintenance / refinement posture
- the core wrapper, handoff-first continuation, and two-step onboarding / project-packet layers are already shipped in meaningful form
- the remaining finalization sequence is F6 through F8, not a redesign wave

### What is done

- the core manifest/profile/reporting wrapper is done enough for real use
- handoff-first continuation is done enough for real use
- two-step onboarding / project packets are done enough for real use

### What remains

- final contract-lock validation sweep
- continuation proof
- onboarding proof
- final release / maintenance gate
- final documentation stop
- final source-bundle freeze export

### Maintenance rule

Prefer narrow maintenance, validation, and truth-refresh work over broad rewrites.
<!-- PATCHOPS_PATCH126_STATUS:END -->

<!-- PATCHOPS_PATCH127_STATUS:START -->
## Patch 127 - final contract-lock validation sweep

### Current state

- Patch 127 adds narrow maintenance-mode contract tests for the final docs introduced by Patch 126.
- The final posture is now enforced by tests rather than memory.
- The repo remains in a maintenance / refinement posture.

### What is now explicitly protected

- `README.md` final maintenance posture wording,
- `docs/llm_usage.md` final maintenance-mode reading order,
- `docs/operator_quickstart.md` final maintenance-mode quickstart split,
- `docs/project_status.md` maintenance posture wording,
- `docs/finalization_master_plan.md` freeze/finalization posture wording.

### Remaining posture

- continue with F4 through F8,
- prefer validation-first proof and narrow repair over broader rewrite,
- keep the repo in maintenance validation rather than redesign.
<!-- PATCHOPS_PATCH127_STATUS:END -->

<!-- PATCHOPS_PATCH128_STATUS:START -->
## Patch 128 - active-work continuation flow proof

### Current state

- Patch 128 re-exports the maintained handoff bundle from a real current PASS report.
- Patch 128 adds one current-state continuation proof test layer.
- The active-work continuation path is now proven both by function/CLI tests and by current generated artifacts.

### What is now explicitly protected

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`
- `handoff/bundle/current/`

### Remaining posture

- continue with F5 through F8,
- keep onboarding separate from continuation,
- prefer narrow proof and repair over broader rewrite.
<!-- PATCHOPS_PATCH128_STATUS:END -->

<!-- PATCHOPS_PATCH128A_STATUS:START -->
## Patch 128A - post-F4 maintenance-doc test repair

Patch 128A repairs the stale Patch 127 expectations inside the maintenance-doc validation layer after Patch 128 advanced the current green head.

This is a narrow test-alignment repair.
It does not change handoff behavior, onboarding behavior, or finalization posture.
<!-- PATCHOPS_PATCH128A_STATUS:END -->

<!-- PATCHOPS_PATCH129_STATUS:START -->
## Patch 129 - new-target onboarding flow proof

### Current state

- Patch 129 proves the helper-first onboarding path against a current generic demo target.
- The repo now has a current proof packet at `docs/projects/demo_roundtrip_current.md`.
- The repo now has current onboarding bootstrap artifacts under `onboarding/`.

### What is now explicitly protected

- `recommend-profile` current generic-target suggestion behavior,
- `init-project-doc` current packet scaffolding path,
- `starter` current documentation-patch manifest suggestion for a generic target,
- current onboarding bootstrap artifacts:
  - `onboarding/current_target_bootstrap.md`
  - `onboarding/current_target_bootstrap.json`
  - `onboarding/next_prompt.txt`
  - `onboarding/starter_manifest.json`

### Remaining posture

- continue with F6 through F8,
- keep onboarding separate from continuation,
- prefer narrow proof and repair over broader rewrite.
<!-- PATCHOPS_PATCH129_STATUS:END -->

<!-- PATCHOPS_PATCH129A_STATUS:START -->
## Patch 129A - onboarding bootstrap CLI repair

Patch 129A is a narrow repair patch for the onboarding proof wave.

It does not redesign onboarding.
It only replaces the failed ad hoc bootstrap helper with the maintained `bootstrap-target` command surface so the expected onboarding artifacts are generated under `onboarding/`.
<!-- PATCHOPS_PATCH129A_STATUS:END -->

<!-- PATCHOPS_PATCH129B_STATUS:START -->
## Patch 129B - bootstrap-target argv repair

Patch 129B is a narrow CLI repair for the onboarding proof path.

It does not redesign onboarding.
It only fixes the `bootstrap-target` module-entry branch so the current onboarding artifacts can be generated through the maintained CLI surface.
<!-- PATCHOPS_PATCH129B_STATUS:END -->

<!-- PATCHOPS_PATCH129C_STATUS:START -->
## Patch 129C - bootstrap-target subcommand slice repair

Patch 129C is the second narrow CLI repair for the onboarding proof path.

It preserves the Patch 129 / 129A / 129B onboarding design and only fixes the final argument-slicing detail needed for successful `python -m patchops.cli bootstrap-target ...` execution.
<!-- PATCHOPS_PATCH129C_STATUS:END -->

<!-- PATCHOPS_PATCH129D_STATUS:START -->
## Patch 129D - bootstrap-target payload contract repair

Patch 129D is a narrow payload-contract repair for the onboarding proof path.

It keeps the CLI flow and onboarding artifacts intact and only aligns the emitted bootstrap JSON with the maintained helper contract already expected by the repo tests.
<!-- PATCHOPS_PATCH129D_STATUS:END -->

<!-- PATCHOPS_PATCH129E_STATUS:START -->
## Patch 129E - bootstrap-target helper routing repair

Patch 129E routes the `bootstrap-target` CLI branch through the maintained onboarding helper so the emitted payload and generated onboarding artifacts match the already-shipped onboarding bootstrap contract.
<!-- PATCHOPS_PATCH129E_STATUS:END -->

<!-- PATCHOPS_PATCH129F_STATUS:START -->
## Patch 129F - bootstrap-target duplicate branch collapse

Patch 129F is the final narrow onboarding-proof repair attempt.

It removes the duplicated `bootstrap-target` command branches and leaves one canonical helper-backed path.
This is still a CLI-surface repair, not an onboarding redesign.
<!-- PATCHOPS_PATCH129F_STATUS:END -->

<!-- PATCHOPS_PATCH129H_STATUS:START -->
## Patch 129H - onboarding proof test contract alignment

Patch 129H aligns the added onboarding proof tests with the current shipped bootstrap-target payload contract.

The onboarding flow remains proven by:
- successful helper-first commands,
- generated onboarding artifacts,
- packet creation,
- starter manifest generation,
- current bootstrap artifact paths.

This patch changes only the proof-test expectations, not the onboarding behavior itself.
<!-- PATCHOPS_PATCH129H_STATUS:END -->

<!-- PATCHOPS_PATCH129I_STATUS:START -->
## Patch 129I - bootstrap-target helper contract restore

Patch 129I restores the intended helper-backed onboarding bootstrap contract for the `bootstrap-target` CLI branch.

This is still a narrow onboarding-proof repair patch.
It does not redesign onboarding; it makes the CLI branch honor the maintained helper contract already documented in the repo.
<!-- PATCHOPS_PATCH129I_STATUS:END -->

<!-- PATCHOPS_PATCH129J_STATUS:START -->
## Patch 129J - onboarding artifact refresh after helper restore

Patch 129J is a narrow refresh patch for the F5 onboarding proof stream.

It does not change the bootstrap contract.
It regenerates the onboarding artifacts from the current `bootstrap-target` implementation so the repo state matches the now-maintained onboarding proof expectations.
<!-- PATCHOPS_PATCH129J_STATUS:END -->

<!-- PATCHOPS_F6_GATE_STATUS:START -->
## Patch 130 - final release / maintenance gate

### Verified input state before this gate

- F1 truth-reset completed.
- F2 final self-contained master documentation completed.
- F3 final contract-lock validation sweep completed.
- F4 active-work continuation flow proof completed.
- F5 new-target onboarding flow proof completed.
- latest successful patch before this gate: Patch 129K â€” `patch_129k_new_target_onboarding_current_contract_repair`
- latest trusted report before this gate: `C:\Users\kostas\Desktop\patch_129k_new_target_onboarding_current_contract_repair_20260328_195939.txt`

### Gate intent

Patch 130 is the final release / maintenance gate patch.
Its job is to confirm, through the shipped readiness and full-suite validation surfaces, that PatchOps can now be described honestly as:

- complete as an initial product,
- in maintenance mode,
- open only to additive or target-specific future work.

### Boundary reminder

Do not redesign the architecture during this gate.
Use the current readiness, handoff, onboarding, example, and profile surfaces as shipped, and repair only what validation proves is still drifting.
<!-- PATCHOPS_F6_GATE_STATUS:END -->

<!-- PATCHOPS_F7_FINAL_DOC_STOP_STATUS:START -->
## Patch 131 - final documentation stop and history compression

Patch 131 is the final documentation stop after Patch 130 passed the release / maintenance gate.

Latest trusted gate report:
`C:\Users\kostas\Desktop\patch_130_final_release_maintenance_gate_patch_130_final_release_maintenance_gate_20260328_202245.txt`

### Shipped behavior

PatchOps should now be treated as:

- finished as an initial product,
- in maintenance mode,
- mechanically usable for active-work continuation,
- mechanically usable for brand-new target onboarding,
- protected by maintained operator, handoff, onboarding, and validation surfaces.

### Historical anchors

Historical plans, older freeze-point prompts, and earlier patch narratives remain useful as anchors.
They do not override current repo files, current tests, current handoff artifacts, or the latest successful validation reports.

### Optional future work

Optional future work is additive only.
It may extend target coverage, helpers, or export ergonomics without reopening the core architecture.

### Target-specific extension work

Target-specific extension work belongs in:

- target repos,
- target project packets under `docs/projects/`,
- target-aligned manifests,
- target profiles where executable assumptions are needed.

It does not belong in the generic PatchOps core unless the behavior is truly reusable.

### Reading-order rule after chat-history loss

If earlier chat history disappears, the minimum durable reading order is:

1. `handoff/current_handoff.md` for already-running work, or the generic docs for brand-new target onboarding,
2. `docs/project_status.md`,
3. `docs/llm_usage.md`,
4. `docs/operator_quickstart.md`,
5. `docs/examples.md`,
6. `docs/patch_ledger.md`,
7. `docs/finalization_master_plan.md`.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_STATUS:END -->

<!-- PATCHOPS_F8_FREEZE_EXPORT_STATUS:START -->
## Patch 132 - final source bundle freeze export

Patch 132 produces the durable final future-LLM source bundle and should be treated as the preferred history-compression artifact after the F6 gate and F7 documentation stop.

Latest trusted pre-export report:
`C:\Users\kostas\Desktop\patch_131_final_documentation_stop_history_compression_patch_131_final_documentation_stop_history_compression_20260328_202727.txt`

### Preferred history-compression artifact

Use `handoff/final_future_llm_source_bundle.txt` as the preferred upload artifact when chat history is unavailable or when a future LLM needs one durable repo snapshot.

### What this bundle includes

The final bundle is intended to preserve at minimum:

- current project status,
- current handoff bundle,
- latest report copy,
- patch ledger,
- master finalization plan,
- key operator docs,
- key onboarding docs,
- current project-packet examples.

### Final freeze stance

PatchOps should now be treated as:

- finished as an initial product,
- in maintenance mode,
- exportable through one durable final source bundle,
- ready for additive-only future work.
<!-- PATCHOPS_F8_FREEZE_EXPORT_STATUS:END -->

<!-- PATCHOPS_PATCH134A_STATUS:START -->
## Patch 134A - summary-integrity repair stream truth reset

### Current state

- A new narrow repair stream has begun for summary-integrity truthfulness.
- The repo should still be treated as a maintenance / refinement wrapper rather than a redesign candidate.
- Patch 133 failed as a wrapper/content-path authoring problem before the real bug was exercised.
- Patch 133A repaired the manifest-local content-path issue and confirmed the real product bug: a required validation failure can still render a summary that ends with `ExitCode : 0` and `Result   : PASS`.
- The attempted Patch 134 run then failed earlier as a malformed-manifest authoring problem rather than a reporting-engine result.

### Why this matters

- the confirmed product bug is now isolated from the surrounding authoring noise,
- future LLMs should not have to reconstruct the 133 -> 133A -> 134 chain from chat history,
- the next step is a narrow authoring unblocker so the real engine fix can run cleanly.

### Failure classification for this stream

- Patch 133 = `wrapper_failure`
- Patch 133A = `target_project_failure` that confirms the real summary-integrity contradiction
- attempted Patch 134 = patch-authoring / malformed-manifest failure

### Next action

Proceed to the second patch in the six-patch repair circle:
- repair the current self-hosted authoring path narrowly,
- keep `content_path` manifest-local and stable,
- repair the malformed JSON generation issue,
- then rerun the real summary-integrity repair path.

### Boundary reminder

Do not redesign PatchOps here.
Keep PowerShell thin, keep reusable logic in Python, and prefer the smallest truthful repair.
<!-- PATCHOPS_PATCH134A_STATUS:END -->

<!-- PATCHOPS_PATCH134B_STATUS:START -->
## Patch 134B â€” summary-integrity authoring unblocker

Patch 134B is the narrow authoring unblocker for the summary-integrity repair stream.

It keeps the scope conservative and does not redesign the manifest system.
Instead it locks two current authoring rules for self-hosted manual-repair patches:

- emit the manifest as valid JSON from structured data rather than hand-assembled text,
- keep `content_path` manifest-local and relative to the manifest file.

A current regression test now drives `check`, `inspect`, `plan`, and `apply` against a temporary self-hosted manual-repair patch root so the stream can prove its authoring contract before the real summary derivation repair continues.
<!-- PATCHOPS_PATCH134B_STATUS:END -->

<!-- PATCHOPS_PATCH134C_STATUS:START -->
## Patch 134C â€” summary-integrity derivation repair

Patch 134C repairs the confirmed summary-integrity bug proven by Patch 133A.

The renderer no longer trusts stale `WorkflowResult.exit_code` / `WorkflowResult.result_label` values blindly when the required command evidence says otherwise.
Instead it derives the rendered summary from current required command evidence before calling `render_summary(...)`.

Current guaranteed behavior:
- required validation failure outside `allowed_exit_codes` forces rendered summary `FAIL`,
- required smoke failure outside `allowed_exit_codes` forces rendered summary `FAIL`,
- the first required failure remains sticky even if later required commands succeed,
- explicitly tolerated non-zero exits still remain `PASS` when they are listed in `allowed_exit_codes`.

This remains a narrow reporting-layer repair.
Workflow-state hardening beyond the renderer stays in the next patch class.
<!-- PATCHOPS_PATCH134C_STATUS:END -->

<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Summary-integrity repair stream status

The summary-integrity stream is now in late maintenance / proof posture.

Current maintained interpretation:
- Patch 133 was a wrapper / patch-authoring failure caused by duplicated `content_path` resolution.
- Patch 133A confirmed the real product bug by proving that required command evidence could still coexist with a rendered `PASS` summary.
- Patch 134 was a malformed-manifest authoring failure and did not invalidate the confirmed product bug.
- Patch 134B repaired the self-hosted authoring unblocker for this stream.
- Patch 134C repaired rendered summary derivation for required validation / smoke failures while preserving explicitly tolerated non-zero exits.
- Patch 134D / 134E hardened workflow-facing surfaces so CLI and handoff now fail closed when stale success state conflicts with required command evidence.

The next steps after this doc refresh are proof / freeze work, not architecture redesign.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->

<!-- PATCHOPS_PATCH134G_STATUS:START -->
## Patch 134G - summary-integrity proof and handoff refresh

Patch 134G closes the six-patch summary-integrity repair circle with a proof-and-refresh run.

It proves the repaired state by running the maintained summary-integrity validation layer:
- `tests/test_summary_integrity_current.py`
- `tests/test_summary_integrity_workflow_current.py`
- `tests/test_reporting.py`
- `tests/test_failure_classifier.py`
- `tests/test_handoff_failure_modes.py`
- `tests/test_export_handoff_cli_contract.py`

It also refreshes the maintained handoff bundle from a green current report so future continuation can rely on:
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/latest_report_index.json`
- `handoff/next_prompt.txt`

Current summary-integrity repair posture:
- Patch 134A recorded the truth reset and separated the confirmed product bug from the authoring failures.
- Patch 134B repaired the narrow self-hosted authoring unblocker.
- Patch 134C repaired rendered summary derivation so required validation/smoke failures can no longer render `PASS`.
- Patch 134E completed the workflow hardening repair so CLI and handoff also fail closed when required command evidence contradicts stale success state.
- Patch 134G now treats this stream as complete unless later evidence proves another contradiction.
<!-- PATCHOPS_PATCH134G_STATUS:END -->

<!-- PATCHOPS_PATCH134H_REPORT_DIR_REPAIR:START -->
## Patch 134H â€” apply-flow report-directory creation repair

Patch 134G exposed a narrow apply-flow bug: `patchops.workflows.apply_patch.apply_manifest(...)` could respect a custom `report_dir` in planning output yet still fail at report-write time when that directory did not already exist.

The repair is intentionally narrow:
- create the parent directory for the resolved report path before writing the canonical report,
- keep the existing `report_preferences.report_dir` contract,
- add a regression test that proves a missing custom report directory is created automatically.

This is a wrapper/content repair, not a summary-integrity redesign.
<!-- PATCHOPS_PATCH134H_REPORT_DIR_REPAIR:END -->

<!-- PATCHOPS_PATCH134I_REPORT_DIR_PROOF:START -->
## Patch 134I â€” report-dir proof repair

Patch 134H most likely repaired the apply-flow bug itself, because `patchops apply` progressed far enough to emit a normal run summary instead of crashing on report creation.

The remaining failure looked like proof-layer drift, not a second report-path crash.
This repair therefore keeps the code fix, narrows the proof surface, and hardens report-preference tests to use an explicit Python runtime instead of relying on the bare `python` command.

This remains a narrow wrapper/content repair.
<!-- PATCHOPS_PATCH134I_REPORT_DIR_PROOF:END -->

<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:START -->
## Patch 134J â€” report-dir proof pytest repair

Patch 134H most likely fixed the underlying apply-flow bug by creating the report directory before writing the canonical report.
The remaining failures were inside the proof layer itself.

This patch keeps the apply-flow repair, updates the maintained report-preference proof test to use an explicit Python runtime, and proves the repair with focused pytest coverage only.
<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:END -->

<!-- PATCHOPS_PATCH134K_STATUS:START -->
## Patch 134K - report-dir proof layer repair

### Current state

- Patch 134K repairs the remaining report-dir proof-layer drift left after Patch 134H through Patch 134J.
- The maintained report-preference apply-flow proof is now a valid current test surface again.
- The maintained interpretation remains:
  - Patch 134H fixed the apply-flow report-directory creation bug itself,
  - and the remaining work after Patch 134K is the final proof / handoff refresh step only.

### Remaining posture

- rerun the maintained summary-integrity proof layer,
- refresh the handoff bundle from the current green report,
- record closure conservatively without widening the stream into redesign.
<!-- PATCHOPS_PATCH134K_STATUS:END -->

<!-- PATCHOPS_PATCH134L_STATUS:START -->
## Patch 134L - summary-integrity final proof and handoff refresh

### Current state

- Patch 134L reruns the maintained summary-integrity proof layer after Patch 134K returned the report-dir proof surface to green.
- Patch 134L refreshes the maintained handoff bundle from the current green report.
- The summary-integrity repair stream can now be treated as complete unless later repo evidence shows a new contradiction between required command evidence and final reported status.

### Remaining posture

- return to the broader maintenance / finalization posture,
- prefer narrow validation, proof, and freeze work over redesign.
<!-- PATCHOPS_PATCH134L_STATUS:END -->

<!-- PATCHOPS_PATCH134O_STATUS:START -->
## Patch 134O - exact-current repair manifest authoring fix

### Current state

- Patch 134O carries the exact-current apply report-write hardening payload through a valid self-hosted manifest shape.
- The patch lands the apply-flow report write hardening in live code and adds the current self-hosted docs-shape regression test.
- The summary-integrity stream should now retry the final proof / handoff refresh step instead of widening the repair scope again.

### Remaining posture

- rerun the maintained summary-integrity proof layer,
- export a refreshed handoff bundle from a current green report,
- record conservative stream closure in maintained docs.
<!-- PATCHOPS_PATCH134O_STATUS:END -->

<!-- PATCHOPS_PATCH134P_STATUS:START -->
## Patch 134P - summary-integrity final proof and handoff refresh retry

### Current state

- Patch 134P reruns the maintained summary-integrity proof layer after Patch 134O landed the exact-current apply report-write hardening.
- Patch 134P refreshes the handoff bundle from a current green report.
- The summary-integrity repair stream can now be treated as complete unless later repo evidence shows a new contradiction between required command evidence and final reported status.

### Remaining posture

- return to the broader maintenance / finalization posture,
- prefer narrow validation, proof, and freeze work over redesign.
<!-- PATCHOPS_PATCH134P_STATUS:END -->
