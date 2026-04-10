# Project packet - Wrapper Self Hosted

This is the maintained target-facing packet for PatchOps acting as its own current target after the published Patch 29A state.

## 1. Target identity

- **Project name:** Wrapper Self Hosted
- **Packet path:** `docs/projects/wrapper_self_hosted.md`
- **Target project root:** `C:\dev\patchops`
- **Wrapper project root:** `C:\dev\patchops`
- **Selected profile:** `generic_python`

## 2. What this target is

PatchOps is acting as its own current target project.

The target is still the PatchOps repository, not an external business-logic repo.
PatchOps remains in maintenance mode.
The goal is to evolve the wrapper conservatively without reopening architecture.

## 3. What must remain outside PatchOps

The following still remain outside PatchOps even during self-hosted maintenance:

- target-project business logic from other repos
- reusable workflow logic implemented primarily in PowerShell
- redesign pressure that would move target-owned decisions into the generic wrapper

## 4. Current first-read surfaces

Read these first when continuing self-hosted work:

- `README.md`
- `docs/project_status.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `docs/post_publish_snapshot.md`
- `handoff/current_handoff.md`
- `handoff/current_handoff.json`

## 5. Recommended command surfaces

- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`
- `py -m patchops.cli check <manifest>`
- `py -m patchops.cli inspect <manifest>`
- `py -m patchops.cli plan <manifest>`
- `py -m patchops.cli apply <manifest>`
- `py -m patchops.cli verify <manifest>`

## 6. Current mutable status

- **Latest passed patch:** `patch_29a_operator_quickstart_run_package_zip_contract_restore`
- **Current recommendation:** continue with narrow maintenance patches that improve maintained docs, packet guidance, and wrapper trust
- **Next recommended action:** refresh the project-packet documentation surfaces so the self-hosted packet matches the published post-refresh state

## 7. Working rules

- Keep PowerShell thin.
- Keep reusable logic in Python-owned surfaces.
- Preserve one canonical report per run.
- Prefer narrow repair over broad rewrite.
- Treat the packet as a contract, not as a replacement for manifests or reports.
