# Project packet - Wrapper Self Hosted

This document is the maintained target-facing packet for PatchOps acting as its own current target.

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
This packet should be read as a maintenance-only, wrapper-on-wrapper contract rather than as a greenfield architecture brief.

## 3. What must remain outside PatchOps
The following still belong outside PatchOps even when PatchOps patches itself:

- target-repo business logic from other projects
- trader-specific or OSM-specific rules in the generic wrapper core
- reusable workflow logic implemented primarily in PowerShell
- any redesign that would move target-owned decisions into the generic wrapper

Simple rule:
- PatchOps owns wrapper behavior,
- target repos own target behavior.

## 4. Why `generic_python` is the selected profile
Selected profile remains `generic_python`.

Why this is the right profile for self-hosted maintenance:

- the repo under change is still a normal Python repository from the wrapper's point of view,
- self-hosted maintenance should exercise the generic wrapper surface rather than invent a PatchOps-only profile without proof,
- the selected profile keeps self-hosted work close to the project-agnostic core,
- profile choice remains executable configuration, while this packet remains the human-readable and LLM-readable contract.

## 5. Self-hosted operating rules
- Read `handoff/current_handoff.md`, `handoff/current_handoff.json`, and `handoff/latest_report_copy.txt` first when continuing active work.
- Use this packet as the maintained target contract for self-hosted work.
- Keep PowerShell thin.
- Keep reusable logic in Python-owned surfaces.
- Prefer narrow repair over broad rewrite.
- Preserve one canonical report per run.
- Handoff first when work is already in progress.
- Treat suspicious-run helpers as conservative trust-improvement surfaces rather than as permission to widen scope.

## 6. Recommended command surfaces
- `py -m patchops.cli init-project-doc`
- `py -m patchops.cli refresh-project-doc`
- `py -m patchops.cli export-handoff`
- `py -m patchops.cli check <manifest>`
- `py -m patchops.cli inspect <manifest>`
- `py -m patchops.cli plan <manifest>`
- `py -m patchops.cli apply <manifest>`

## 7. Current maintenance posture
PatchOps should be treated here as a finished initial product in maintenance mode.

Current recommended patch classes:
- doc-contract repair
- documentation refresh
- wrapper-only repair
- proof patch
- narrow helper alignment
- additive maintenance validation

Next recommended action:
- continue with narrow maintenance patches that improve maintained docs, packet guidance, and wrapper trust without reopening architecture.

## 8. Current development state
- **Current phase:** Phase C
- **Current objective:** Make self-hosted packet generation and refresh operator-friendly while preserving the maintenance-mode wrapper boundary.
- **Latest passed patch:** patch_78
- **Latest attempted patch:** patch_79
- **Latest known report path:** (pending current run)
- **Current recommendation:** Use the CLI for packet generation and refresh. Use PowerShell only as a thin launcher/report surface.
- **Next action:** Refresh Documentation Stop P-C after this patch passes.

### Current blockers
- (none)

### Outstanding risks
- wrapper-only repair scripts can still drift wider than the architecture wants if they duplicate reusable logic
- large documentation rewrites can still break exact doc-contract tests if they replace instead of preserve known phrases
- suspicious-run support is intentionally conservative and should stay that way

<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:START -->
## Maintained self-hosted packet reminder

This wrapper self-hosted packet remains the maintained target-facing packet for PatchOps acting as its own current target.

It should continue to keep these things explicit:

- target root: `C:\dev\patchops`
- wrapper root: `C:\dev\patchops`
- selected profile
- what must remain outside PatchOps
- next recommended action
- handoff first when work is already in progress
<!-- PATCHOPS_PATCH93_WRAPPER_PACKET:END -->

## Suspicious-run maintenance note

The self-hosted maintenance stream now includes suspicious-run helpers for contradiction detection, compact optional artifact emission, and a short report mention when emission occurs. These surfaces exist to improve wrapper trust during maintenance work and remain intentionally conservative.
