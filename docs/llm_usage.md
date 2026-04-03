# LLM Usage Guide

This file is the orientation page for future coding LLMs.

It is not the main state-reconstruction surface anymore.

PatchOps is a **standalone wrapper / harness project**.

PatchOps owns how change is applied, validated, evidenced, retried, and handed off. Target repos own:

- business logic
- target-specific application behavior
- project-specific workflows that do not belong in the generic wrapper core

Never move target-repo business logic into PatchOps.

do not move target-repo business logic into PatchOps

Trader is the first serious profile, not the identity of the wrapper.

This doc should help a future LLM understand:

- how to read the project
- how to pick a profile
- how to build a manifest
- how to decide between apply and verify-only
- how to classify failure
- how to avoid moving target-repo logic into patchops

The most important supporting surfaces for that are:

- `docs/failure_repair_guide.md`
- `docs/project_status.md`
- `docs/operator_quickstart.md`
- `docs/examples.md`
- `examples/trader_first_verify_patch.json`
- `powershell/Invoke-PatchVerify.ps1`

## Path A — active-work continuation

If PatchOps work is already in progress, start with the handoff bundle first.

This path is for continuing an already-running PatchOps effort.

Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Then read:

4. `docs/project_status.md`
5. `docs/operator_quickstart.md`
6. `docs/examples.md`

After reading the handoff, briefly restate:

- current state
- latest attempted patch
- failure class
- next action

Then produce only the next repair patch or next planned patch.

In other words: verify reality, repair narrowly, prefer narrow repair over broad rewrite, and preserve the smallest trustworthy next step.

### operator flow for continuation

The intended operator path is:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

That is the default takeover flow for in-progress PatchOps work.

## Path B — onboarding a brand-new target project

When the task is not “continue the current PatchOps run,” but instead “use PatchOps to start work on a brand-new target project,” begin with the generic onboarding packet.

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

Then read or create the relevant file under `docs/projects/`.

Use `docs/projects/<project_name>.md` as the maintained target packet path.

<!-- PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START -->
## Project-packet onboarding now includes helpers

When starting a brand-new target project with PatchOps, the onboarding flow is now:

1. read the generic PatchOps packet,
2. determine the smallest correct profile with `recommend-profile`,
3. create or refresh `docs/projects/<project_name>.md`,
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


## how to pick a profile

Use the smallest correct profile.

Examples include:

- `trader`
- `generic_python`
- `generic_python_powershell`

Profiles remain the executable target abstraction.

## how to build a manifest

Use an existing example when possible, then adjust the manifest narrowly for the current run.

The usual safe authoring sequence remains:

`profiles` -> `doctor` -> `examples` -> `template` -> `check` -> `inspect` -> `plan` -> `apply` or `verify`

## how to decide between apply and verify-only

Use `apply` when content really needs to change.

Use `verify` when the code or docs already on disk are expected to be correct and you need a narrow rerun where writes are skipped and expected files are re-checked.

## how to classify failure

Use `docs/failure_repair_guide.md` to distinguish:

- content failure
- wrapper failure
- verification-only rerun cases
- wrapper-only repair cases
- suspicious-run cases

## Do not do this

- do not start from stale historical plans
- do not redesign broad architecture on narrow failures
- do not confuse wrapper failure with target failure
- do not replace project packets with handoff
- do not replace handoff with project packets

## Final maintenance-mode reading order

The final maintenance-mode reading order is:

1. handoff bundle first for already-running work
2. generic packet plus project packet for brand-new target onboarding under `docs/projects/<project_name>.md`
3. project status, operator quickstart, examples, patch ledger, and the finalization anchor as the durable repo-level orientation set

`docs/finalization_master_plan.md` is the maintained finalization anchor when prior chat history is gone.

<!-- PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START -->
## Final start-here guide after history compression

Use the smallest correct reading path.

### If PatchOps work is already in progress

Start with the handoff bundle:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Then read:

4. `docs/project_status.md`
5. `docs/operator_quickstart.md`
6. `docs/examples.md`

### If you are starting a brand-new target project

Start with the generic onboarding packet:

1. `README.md`
2. `docs/llm_usage.md`
3. `docs/operator_quickstart.md`
4. `docs/project_packet_contract.md`
5. `docs/project_packet_workflow.md`

Then read or create the relevant file under `docs/projects/`.

Use `docs/projects/<project_name>.md` as the maintained target packet path.
Use `docs/projects/<project_name>.md` as the maintained target packet path for brand-new onboarding.


### Boundary rules

- use handoff for already-running PatchOps work,
- use the generic packet plus a project packet for brand-new target work,
- use manifests to tell PatchOps what to do now,
- use reports to prove what happened,
- do not treat old chat history as the primary state source once these maintained docs exist.
<!-- PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:END -->

<!-- PATCHOPS_F8_FREEZE_EXPORT_LLM_USAGE:START -->
## Final freeze-export note

When a future LLM needs one durable upload artifact rather than several repo files, prefer:

`handoff/final_future_llm_source_bundle.txt`

Continue to use the handoff bundle for the most recent run-state, but use the final source bundle when you need one larger, durable, history-compressed source artifact.
<!-- PATCHOPS_F8_FREEZE_EXPORT_LLM_USAGE:END -->

## Self-hosted patch authoring notes for Windows PowerShell / ISE

When generating self-hosted PatchOps repair scripts that write a temporary patch manifest and then call PatchOps from Windows PowerShell 5.1 or PowerShell ISE, use this pattern:

- write the patch manifest as compact JSON
- do not add a trailing newline to the patch manifest
- validate the manifest immediately with `json.load(...)` before calling PatchOps
- if the PatchOps run fails early, print the manifest content for debugging
- prefer `System.Diagnostics.ProcessStartInfo.Arguments` over `ArgumentList` in Windows PowerShell 5.1 / ISE compatibility mode

These notes are not architecture changes.
They are operator-authoring hardening notes that reduce avoidable script failures in self-hosted repair flows.
