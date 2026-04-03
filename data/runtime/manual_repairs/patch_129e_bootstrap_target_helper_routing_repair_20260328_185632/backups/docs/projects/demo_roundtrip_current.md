# Project packet â€” Demo Roundtrip Current

## 1. Target identity
- **Project name:** Demo Roundtrip Current
- **Packet path:** `docs/projects/demo_roundtrip_current.md`
- **Target project root:** `C:\dev\patchops\data\runtime\manual_repairs\patch_129_new_target_onboarding_flow_proof_20260328_183629\demo_roundtrip_current_target`
- **Wrapper project root:** `C:\dev\patchops`

## 2. Target roots and runtime
- **Target root:** `C:\dev\patchops\data\runtime\manual_repairs\patch_129_new_target_onboarding_flow_proof_20260328_183629\demo_roundtrip_current_target`
- **Wrapper root:** `C:\dev\patchops`
- **Expected runtime:** `(use profile default unless a target-specific override is required)`

## 3. Selected PatchOps profile
- **Profile:** `generic_python`
- **Profile rule:** start with the smallest correct profile and widen only when the target really needs it.

## 4. What PatchOps owns
- manifest authoring and execution mechanics,
- deterministic reporting and validation evidence,
- profile-driven wrapper behavior,
- project-packet maintenance and onboarding support.

## 5. What must remain outside PatchOps
- target-repo business logic,
- target-specific production rules,
- target-side operational policy,
- architectural decisions that belong inside the target repo itself.

## 6. Recommended examples and starting surfaces
- Read the generic PatchOps packet first.
- Start from the closest example under `examples/`.
- Use the packet as the target-facing contract, not as a replacement for manifests or reports.
- Before execution, run `check`, `inspect`, and `plan`.

## 7. Phase guidance
- Build the target patch by patch with narrow manifests.
- Keep PowerShell thin and keep reusable logic in Python.
- Refresh this packet after meaningful report-producing runs.

### Initial goals
- Create the current project packet
- Generate the safest starter manifest

## 8. Current development state

### Mutable status
- **Current phase:** Initial onboarding
- **Current objective:** Create the first narrow target-specific manifest.
- **Latest passed patch:** (none yet)
- **Latest attempted patch:** (none yet)
- **Latest known report path:** (none yet)
- **Current recommendation:** Read the generic PatchOps packet, pick the closest example, and stay narrow.
- **Next action:** Run check, inspect, and plan before the first apply or verify execution.

### Current blockers
- No blockers are recorded right now.

### Outstanding risks
- No outstanding risks are recorded right now.
