# PowerShell Runner Guardrails

This note exists to keep launcher-side work boring and reliable.

## Core rule

PowerShell is the operator-facing boundary, not the durable workflow engine.

## Use PowerShell for

- path resolution,
- runtime resolution,
- calling the PatchOps CLI,
- capturing outer stdout and stderr when needed,
- writing one Desktop report,
- opening the report.

## Do not use PowerShell for

- large reusable workflow logic,
- brittle JSON handoff unless unavoidable,
- deep state reconstruction,
- giant inline Python source emission,
- complex report-buffer choreography,
- logic that belongs in tested Python helpers.

## Guardrails

### 1. Keep the failure path simpler than the success path
If the catch path depends on the same helpers that already failed, the report becomes less trustworthy.

### 2. Treat null and empty report buffers as hostile input
Never assume the report buffer is still a valid list in a failure path.

### 3. Prefer staged file writes over inline source acrobatics
If PowerShell writes Python, assume backslashes, quotes, and indentation are dangerous.

### 4. Avoid exact-body surgery when files may have drifted
Use top-level anchors, append-if-missing logic, or direct staged rewrites.

### 5. Preserve the real failing command output
If the report does not contain exact command, exit code, stdout, and stderr, fix that first.

### 6. Switch to direct repair when self-hosted authoring becomes the blocker
PatchOps should prove itself, but not at the cost of endless runner archaeology.

## Bottom line

Thin launcher only.
Capture first.
Report clearly.
Move reusable logic back into Python.
