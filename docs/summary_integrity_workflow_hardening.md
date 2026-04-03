# Summary-integrity workflow hardening

This note records the Patch 134E follow-on hardening after the Patch 134C derivation repair.

## Purpose

Patch 134C repaired the rendered inner report summary so required validation and smoke failures could not render `PASS`.

Patch 134E hardens the workflow-facing surfaces that still depended on raw `WorkflowResult.exit_code` and `WorkflowResult.result_label` values.

## Narrow rule added in Patch 134E

When required validation or smoke command evidence fails outside `allowed_exit_codes`, PatchOps should fail closed across workflow-facing summary surfaces even if a stale `WorkflowResult` still says success.

That hardening now covers:

- console run summary output from `patchops.cli`
- console process exit code returned by `patchops.cli`
- handoff current-status and latest-passed labels
- handoff next-action recommendation classification
- the rendered report summary through the shared integrity helper

## Scope boundary

This patch does not redesign command execution or manifest behavior.

It only makes summary truth derived consistently from required command evidence before user-facing summary surfaces present PASS/FAIL state.
