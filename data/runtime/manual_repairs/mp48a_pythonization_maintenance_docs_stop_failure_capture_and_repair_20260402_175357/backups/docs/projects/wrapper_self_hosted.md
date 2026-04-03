# Project packet - Wrapper Self Hosted

## 1. Target identity
- **Project name:** Wrapper Self Hosted
- **Packet path:** `docs/projects/wrapper_self_hosted.md`
- **Target project root:** `C:\dev\patchops`
- **Wrapper project root:** `C:\dev\patchops`
- **Selected profile:** `generic_python`
- **Expected runtime:** `py` or the project virtual environment when explicitly chosen

## 2. What this target is
PatchOps is acting as its own current target project.
The target is still the PatchOps repository, not an external business-logic repo.
The goal is to use the existing PatchOps model to evolve PatchOps conservatively.

## 3. What must remain outside PatchOps
- target-repo business logic from other projects
- trader-specific or OSM-specific rules in the generic wrapper core
- reusable workflow logic implemented primarily in PowerShell

## 4. Self-hosted operating rules
- Read `handoff/current_handoff.md`, `handoff/current_handoff.json`, and `handoff/latest_report_copy.txt` first when continuing active work.
- Use this packet as the maintained target contract for self-hosted work.
- Keep PowerShell thin.
- Keep reusable logic in Python-owned surfaces.
- Prefer narrow repair over broad rewrite.
- Preserve one canonical report per run.

## 5. Recommended command surfaces
- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`

## 6. Current development state
- **Current phase:** Phase C
- **Current objective:** Make self-hosted packet generation and refresh operator-friendly.
- **Latest passed patch:** patch_78
- **Latest attempted patch:** patch_79
- **Latest known report path:** (pending current run)
- **Current recommendation:** Use the CLI for packet generation and refresh. Use PowerShell only as a thin launcher/report surface.
- **Next action:** Refresh Documentation Stop P-C after this patch passes.

### Current blockers
- (none)

### Outstanding risks
- wrapper-only repair scripts can still drift wider than the architecture wants if they duplicate reusable logic
\n\n<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:START -->
## Maintained self-hosted packet reminder

This wrapper self-hosted packet remains the maintained target-facing packet for PatchOps acting as its own current target.

It should continue to keep these things explicit:

- target root: `C:\dev\patchops`
- wrapper root: `C:\dev\patchops`
- selected profile
- what must remain outside PatchOps
- next recommended action
- handoff first when work is already in progress
<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:END -->\n