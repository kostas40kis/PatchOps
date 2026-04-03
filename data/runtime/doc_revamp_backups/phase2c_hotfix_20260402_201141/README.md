# PatchOps

PatchOps is a standalone wrapper, harness, and patch-execution toolkit for Windows-first repository maintenance.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## Consolidation status

PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture.
The initial buildout circle is complete enough that the repo should be treated as a maintained utility rather than an open-ended architecture buildout.

## Final maintenance posture

PatchOps should now be operated as a maintained wrapper utility rather than a greenfield architecture project.

Read these files in this order:

### For already-running PatchOps work

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `handoff/next_prompt.txt`
5. then `docs/project_status.md`
6. then `docs/llm_usage.md`

For already-running PatchOps continuation, run handoff export first and then paste `handoff/next_prompt.txt`.

### For a brand-new target project

1. `README.md`
2. `docs/llm_usage.md`
3. `docs/operator_quickstart.md`
4. `docs/project_packet_contract.md`
5. `docs/project_packet_workflow.md`
6. then the relevant file under `docs/projects/`

## Current posture

- PatchOps is in maintenance mode.
- PowerShell stays thin and operator-facing.
- Reusable logic belongs in Python.
- One canonical report per run remains mandatory.
- Handoff remains the continuation surface for already-running work.
- Project packets remain the onboarding surface for a brand-new target project.

## Profile and example reminders

Generic Python + PowerShell profile examples remain part of the supported reading and example surface.
That includes the `generic_python_powershell` profile and its example manifests.

Use profiles, manifests, examples, and current reports as the maintained truth surfaces rather than reconstructing state from old chat history.

## Suspicious-run support

PatchOps includes suspicious-run support as a conservative wrapper health aid.
It is opt-in support for contradiction detection and optional artifact emission.
It is meant to increase trust in wrapper evidence without becoming a mandatory default behavior.

<!-- PATCHOPS_F7_FINAL_DOC_STOP_README:START -->
## Final maintained reading order

PatchOps is in maintenance mode after the final release / maintenance gate.

### Start here for already-running PatchOps work

1. read `handoff/current_handoff.md`
2. read `handoff/current_handoff.json`
3. read `handoff/latest_report_copy.txt`
4. then read `docs/project_status.md`
5. then read `docs/llm_usage.md`

Run handoff export before continuing if the handoff bundle needs to be refreshed.

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
