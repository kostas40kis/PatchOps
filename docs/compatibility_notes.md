# Compatibility notes

## Windows PowerShell 5.1

PatchOps must remain compatible with Windows PowerShell 5.1 where possible.

## Self-hosted manifest-authoring compatibility note

Use compatibility-safe authoring when generating manifests from self-hosted scripts.
- Windows PowerShell 5.1 may not expose `ProcessStartInfo.ArgumentList`; use the `Arguments` fallback when needed.
- Self-hosted manifest-authoring compatibility remains additive and should not widen PowerShell into a second workflow engine.
- Use `ProcessStartInfo.Arguments` when `ProcessStartInfo.ArgumentList` is unavailable.
- Launcher helpers must preserve parser-safe shape when falling back for older Windows PowerShell environments.
- Root launchers should keep the parser-safe top-level `param(` script-file form when emitted or repaired.
- There must be no stray leading character before `param(...)` in emitted or repaired root launchers.
- When repairing compatibility issues, repair the first failing layer only before widening.

## Self-hosted manifest-authoring compatibility note
PowerShell ISE
avoid relying on `ProcessStartInfo.ArgumentList`
compact JSON
no trailing newline
immediate `json.load(...)` validation
ProcessStartInfo.Arguments
ArgumentList
