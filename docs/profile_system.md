# Profile system

## Purpose

Profiles let PatchOps adapt execution behavior to a target repository without moving target-side logic into the wrapper.

PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:START
Helper relationship
- recommend-profile --target-root <path> is the narrow helper for profile recommendation during brand-new target onboarding.
- It reduces guesswork but does not replace manifests, reports, or handoff.
PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:END
- Profiles remain executable-assumption surfaces rather than target business-logic surfaces.
- Use `recommend-profile` first for brand-new targets, then confirm with a narrow starter example.
- `generic_python` remains the safest baseline profile when no target-specific evidence is available.
- Start with the smallest correct profile.
- Profile guidance should keep the wrapper project-agnostic.
Profiles remain the executable abstraction.
Keep the wrapper project-agnostic.
