# LLM Usage Guide

This document is the core usage manual for future coding LLMs working inside PatchOps.

The main goal is simple:

help a future model become useful quickly **without rediscovering the architecture, mixing target-repo logic into PatchOps, or widening safe rerun paths into blind retries**.

---

## 1. Read this project in the right order

Do not start by guessing from file names alone.

Read the project in this order:

1. `README.md`
2. `docs/project_status.md`
3. `docs/overview.md`
4. `docs/manifest_schema.md`
5. `docs/profile_system.md`
6. `docs/examples.md`
7. `docs/failure_repair_guide.md`
8. `docs/trader_profile.md` when the target repo is `C:\dev\trader`

If the work is specifically trader-first, also read:

- `docs/trader_readiness_index.md`

This order matters because PatchOps is profile-driven and manifest-driven.
A model that skips directly into patch files can misunderstand which behavior belongs to the wrapper and which belongs to the target repo.

---

## 2. How to understand the project quickly

PatchOps is a **standalone wrapper / harness project**.

PatchOps owns:

- manifest loading and validation,
- profile resolution,
- path and backup handling,
- file-writing helpers,
- process execution,
- reporting,
- failure classification,
- apply / verify / cleanup / archive workflow surfaces,
- thin PowerShell launchers.

Target repos own:

- business logic,
- domain rules,
- tests,
- repo-specific architecture,
- repo-specific safety policy,
- patch semantics.

Never move target-repo business logic into PatchOps just because PatchOps is touching that repo.

---

## 3. How to pick a profile

Always pick a profile before assuming path defaults, runtimes, or report expectations.

The active profile determines things such as:

- default target project root,
- expected runtime path pattern,
- backup conventions,
- report preferences,
- and sometimes safe operational defaults.

Use the CLI to inspect profile availability when needed:

- `py -m patchops.cli profiles`
- `py -m patchops.cli doctor --profile trader`

Current important profiles include:

- `generic_python`
- `generic_python_powershell`
- `trader`

Do not hardcode trader assumptions into the core just because trader is the first real target profile.

---

## 4. How to build a manifest

Start from the smallest example manifest that matches the job.

Good starting points are in `examples/`.

Typical pattern:

1. choose the closest example,
2. keep the active profile explicit,
3. keep file targets explicit,
4. keep validation commands narrow and reportable,
5. keep notes and tags useful for handoff.

Before inventing a new structure, read:

- `docs/manifest_schema.md`
- `docs/examples.md`

For trader-first work, especially verify-first usage, start from:

- `examples/trader_first_verify_patch.json`
- `examples/trader_first_doc_patch.json`

Prefer adaptation over invention.

---

## 5. How to decide between apply and verify-only

Do not default to a full apply pass.

Choose **apply** when:

- files need to be created or changed,
- the point of the run is to perform a patch,
- a write pass is actually part of the task.

Choose **verify-only** when:

- the files are already on disk,
- the real goal is re-validation,
- the correct next step is a narrow evidence rerun,
- another write pass would add avoidable risk or noise.

The verify-only surface should remain narrow and explicit.

For PowerShell-first operator flows, the thin launcher exists for that path:

- `powershell/Invoke-PatchVerify.ps1`

Use preview behavior when appropriate so the verify-only plan is visible before running it.

---

## 6. How to classify failure

Do not collapse all failures into “rerun it.”

Use `docs/failure_repair_guide.md` and distinguish between:

- **content failure**,
- **wrapper failure**,
- **verification-only rerun case**,
- **wrapper-only repair case**.

A good model should ask:

1. did target-repo content fail,
2. or did wrapper mechanics fail,
3. are the files already on disk,
4. and what is the narrowest trustworthy recovery path?

This matters because wrapper-only retry and verify-only reruns are meant to stay narrow and auditable.

---

## 7. How to avoid moving target-repo logic into PatchOps

This is one of the most important rules.

Wrong direction:

- adding trader business rules into PatchOps core modules,
- embedding target-repo patch semantics inside launcher logic,
- making examples or docs imply that trader behavior is the identity of PatchOps.

Correct direction:

- keep target specifics in manifests,
- keep repo defaults in profiles,
- keep domain behavior in the target repo,
- keep PatchOps focused on safe workflow execution and evidence.

Trader is the first serious profile, not the identity of the wrapper.

---

## 8. How to work safely in this repo as an LLM

Prefer these habits:

- read current docs before reshaping code,
- check the development plan before skipping ahead,
- make patches additive and explicit,
- keep PowerShell thin and conservative,
- let Python own reusable workflow logic once,
- produce one strong report artifact per patch run,
- keep tests close to the claimed contract.

Avoid these habits:

- broad redesigns during doc/test patches,
- hidden shell assumptions,
- hand-wavy rerun logic,
- moving examples faster than tests and docs,
- unreviewed widening from verify-only into apply.

---

## 9. Practical first steps for a future LLM

When you arrive fresh in this project:

1. read `README.md`,
2. read `docs/project_status.md`,
3. read this file,
4. read the relevant profile doc,
5. inspect the examples that match the task,
6. choose whether the task is apply, verify-only, or wrapper-only repair,
7. write the smallest patch that proves the next contract surface,
8. validate it with a single strong report.

That sequence is the intended handoff behavior.

---

## 10. Bottom line

PatchOps becomes valuable when future models can use it **without tribal memory**.

The right mindset is:

- understand the wrapper/target boundary,
- choose a profile deliberately,
- start from a manifest example,
- decide between apply and verify-only carefully,
- classify failures honestly,
- and keep the recovery path as narrow and trustworthy as possible.

If you follow that discipline, a future LLM can begin useful work from this project quickly.
