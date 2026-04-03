# Trader project packet

## 1. Purpose of the target project

The trader project is the first serious target-project example for PatchOps.

Its purpose in this packet is not to restate every trader architectural detail from the target repository.
Its purpose is to give a future LLM or operator one maintained target-facing contract inside PatchOps so trader-facing work can begin without rebuilding assumptions from scattered docs, reports, and old chat context.

This packet should be read as the standing PatchOps view of the trader target.
It should help answer:

- what the trader target is,
- which PatchOps profile should be used,
- which roots and runtime are expected,
- which kinds of first patches are safe,
- which existing docs and examples are the right starting surfaces,
- what must remain inside the trader repo rather than drifting into PatchOps,
- what the current trader-facing usage posture is.

---

## 2. Target root

Primary target root:

`C:\dev\trader`

Wrapper root:

`C:\dev\patchops`

The target root and wrapper root must stay distinct.
PatchOps is the wrapper that applies, validates, evidences, and hands off change.
The trader repo is the place where trader architecture, domain logic, execution behavior, and safety decisions live.

---

## 3. Expected runtime

Expected trader runtime:

`C:\dev\trader\.venv\Scripts\python.exe`

Expected wrapper runtime posture:

- PatchOps commands are launched from the PatchOps repo,
- the selected profile resolves the target assumptions,
- validation commands should normally use the profile runtime when trader-side Python validation is required.

The runtime expectation should be treated as part of the trader profile contract, not as an ad hoc per-run guess.

---

## 4. Selected PatchOps profile

Expected profile:

`trader`

Why this is the right profile:

- the target root convention is trader-specific,
- the expected runtime is trader-specific,
- the first-usage docs, readiness surface, and starter examples already assume the trader profile,
- the initial target-facing usage flow is deliberately documented around trader-first rehearsal and low-risk first manifests.

This packet does not replace the profile.
The profile remains the executable abstraction.
This packet is the maintained human-readable and LLM-readable contract for using that profile against the trader target.

---

## 5. What must remain outside PatchOps

The following must remain owned by the trader repo rather than migrating into PatchOps:

- trading domain logic,
- execution logic,
- strategy logic,
- market behavior decisions,
- trader-side safety policy,
- repo-specific architecture,
- target-owned tests beyond wrapper orchestration.

PatchOps may execute manifests that touch trader files, validate trader code, and produce deterministic reports.
It must not become the long-term home of trader business logic.

Simple rule:

- PatchOps owns wrapper behavior,
- trader owns trader behavior.

---

## 6. Recommended example manifests

The lowest-friction starting surfaces for trader-facing work are the low-risk starter examples already connected to the trader-first readiness flow.

Recommended first examples:

- `examples/trader_first_verify_patch.json`
- `examples/trader_first_doc_patch.json`

Also relevant, depending on scope:

- `examples/trader_verify_patch.json`
- `examples/trader_doc_patch.json`
- `examples/trader_code_patch.json`

Use the first two when the goal is the safest first trader-facing usage or rehearsal.
Use the broader trader examples only when the work clearly exceeds the initial starter posture.

When blank-page authoring would be wasteful, also use the template command with the trader profile and then narrow it deliberately.

---

## 7. Patch classes expected for this target

The trader target should be approached conservatively.
The expected patch classes include:

- documentation-only trader patches,
- verification-only or report-only trader patches,
- tiny repo-safe writes,
- validation/test-surface patches,
- profile-aligned starter manifests,
- later, larger trader-facing patches only after the readiness surface is respected.

The earliest preferred classes remain:

- documentation-only,
- verification-only,
- small explicit file writes with deterministic validation,
- rehearsal-first flows.

Avoid using this packet to justify jumping straight into broad high-risk trader changes.

---

## 8. Development phases for this target

The trader target should be interpreted in phases from the PatchOps point of view.

### Phase 1 — trader-first preparation and rehearsal

Goal:
Use PatchOps as the normal wrapper around a real trader-facing manifest flow without moving trader business logic into PatchOps.

Typical characteristics:

- read the trader readiness docs,
- choose a low-risk starter manifest,
- run the normal wrapper flow,
- classify outcomes cleanly as wrapper-only or trader-side,
- prove the reporting and execution discipline on small safe work.

### Phase 2 — controlled first real trader-facing usage

Goal:
Move from rehearsal to real but still conservative trader-target work.

Typical characteristics:

- explicit backups,
- explicit validation commands,
- clear report expectations,
- still narrow manifest scope,
- still no migration of trader logic into PatchOps.

### Phase 3 — broader trader-target usage once readiness gates are satisfied

Goal:
Expand PatchOps usage against the trader repo after the initial readiness wave is well understood.

Typical characteristics:

- larger or more varied patch classes,
- more confidence in operator sequence,
- continued use of reports, profiles, manifests, and handoff,
- the same architectural boundary remains intact.

---

## 9. Validation strategy

Validation for trader-facing PatchOps work should remain conservative and explicit.

Recommended validation posture:

1. confirm PatchOps baseline health first,
2. use `doctor --profile trader`,
3. inspect examples before inventing a manifest from scratch,
4. review every manifest with:
   - `check`
   - `inspect`
   - `plan`
5. prefer verify-only or documentation-first starts when risk is unclear,
6. keep the earliest real trader-facing patches intentionally small,
7. ensure failure can be classified as wrapper-only or trader-side.

The trader readiness docs should stay part of the validation surface for this target.
They exist specifically to keep early trader-facing work disciplined.

---

## 10. Report expectations

Every trader-facing PatchOps run should still produce one canonical report.

That report should make the following easy to understand:

- what manifest ran,
- which target root was used,
- which profile was active,
- which runtime was used,
- which commands were executed,
- what stdout and stderr were produced,
- whether the run passed or failed,
- whether a failure is wrapper-only or trader-side when that distinction can be made.

A project packet does not replace run evidence.
It summarizes standing target understanding and current status.
The canonical report remains the evidence artifact for what actually happened in a specific run.

---

## 11. Recommended reading order for this target

When a future LLM is using PatchOps against trader for the first time, the shortest good orientation path is:

1. generic PatchOps onboarding docs,
2. this project packet,
3. `docs/trader_readiness_index.md`,
4. `docs/trader_first_usage.md`,
5. `docs/trader_manifest_authoring_checklist.md`,
6. `docs/trader_safe_first_patch_types.md`,
7. `docs/trader_execution_sequence.md`,
8. `docs/trader_rehearsal_runbook.md`,
9. `docs/first_real_trader_run_checklist.md`,
10. `docs/stage2_entry_criteria.md`.

If the work is already in progress and current handoff artifacts exist, start with handoff first and then read this packet as the target-facing contract.

---

## 12. Current state

Current interpretation of the trader target inside PatchOps:

- trader is the first serious maintained target-project example for the new project-packet layer,
- the repo already has a trader-first readiness surface,
- starter manifests and trader-specific guidance already exist,
- the current packet is meant to gather those assumptions into one maintained target-facing contract,
- the packet should be treated as additive guidance, not as a replacement for the existing readiness docs.

The trader target should therefore be considered:

- already supported by a real profile,
- already supported by starter examples and rehearsal docs,
- now being upgraded with a maintained project packet so future onboarding is less interpretive.

---

## 13. Latest passed patch

For the project-packet rollout itself, the latest already-completed work is the documentation-first phase that introduced:

- `docs/project_packet_contract.md`,
- `docs/project_packet_workflow.md`,
- refreshed `docs/llm_usage.md`,
- refreshed top-level status and README surfaces.

This trader packet should be treated as the first major maintained target-packet example that follows that formalized contract.

---

## 14. Latest attempted patch

Current patch target:

- create `docs/projects/trader.md`

This file is the first serious example packet in the new project-packet system.

---

## 15. Current blockers

Current blockers are mostly architectural and documentary rather than code-level.

They include:

- the trader assumptions still live across multiple docs and starter surfaces,
- the packet system does not yet have its contract tests,
- scaffold and refresh helpers do not yet exist,
- the onboarding story is not yet as mechanical as the handoff story.

These blockers do not prevent use of PatchOps against trader.
They are the reason this maintained packet is worth creating now.

---

## 16. Next recommended action

After this packet is added, the next safest steps are:

1. add the packet contract tests,
2. prove the trader packet contains the required roots, boundaries, and workflow references,
3. refresh practical usage docs so project packets become part of everyday operator guidance,
4. only then add project-packet scaffold and refresh helpers.

This preserves the intended sequence:

- docs first,
- first real maintained packet,
- tests,
- practical doc refresh,
- then automation support.

---

## 17. Stable interpretation rules for future LLMs

A future LLM using this packet should preserve the following rules.

1. Do not move trader business logic into PatchOps.
2. Do not treat this packet as a replacement for the trader profile.
3. Do not treat this packet as a replacement for manifests.
4. Do not treat this packet as a replacement for handoff files.
5. Start from trader starter examples when risk is low and speed matters.
6. Prefer deliberate small trader-facing patches before broad ones.
7. Keep one canonical report per run.
8. Use this packet to reduce guesswork, not to bypass the normal PatchOps execution flow.
