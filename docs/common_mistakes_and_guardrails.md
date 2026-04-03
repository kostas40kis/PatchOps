# Common Mistakes and Hard-Won Guardrails

This file is the condensed maintained lessons note for self-hosted PatchOps work.

## Biggest recurring mistake class

The most expensive failures were usually not deep architecture failures.

They were usually one of these:

1. wrapper or prep logic failed before real validation started,
2. the report hid the actual failing step,
3. generated source or tests were malformed,
4. a test asserted a path-dependent or environment-dependent detail instead of the intended contract,
5. a shared helper assumed a newer full object shape than older callers actually provided.

## Guardrails by mistake class

### Fragile JSON handoff between embedded Python and PowerShell
Avoid it unless truly necessary.
Prefer simpler handoff shapes or Python-owned orchestration.

### Wrapper logic became the failure point after authoring already succeeded
Keep the wrapper thin.
Every extra parse, conversion, or helper hop creates another failure surface.

### Emitting Python source incorrectly from PowerShell
Treat PS1-written Python as high-risk.
Validate generated files immediately with a targeted collection run.

### Nested quoting and backslashes handled too loosely
Prefer staged content files over shell string acrobatics.

### Weak or brittle truth probes
Do not use over-interpretive prep logic when a direct staged rewrite would be safer.

### Shared helpers extended without preserving lightweight caller shapes
Use defensive reads for optional fields.
Add compatibility tests when helper surfaces change.

### Null or empty-string report buffers in failure paths
Never assume the report buffer still has the expected shape.
Build a fresh fallback report buffer directly in the catch path.

### PowerShell collection-shape drift caused by enumeration
Keep one list object and mutate it in place.
Do not bounce buffers through multiple helper-return pathways.

### Failure reports that hide the actual failing command output
If the runner cannot preserve exact command, exit code, stdout, and stderr, repair the runner first.

### Path-dependent or environment-dependent test assertions
Assert the intended contract, not incidental path text or temp-directory spelling.

## Bottom line

Do not let the script that is supposed to prove repo truth become more fragile than the repo work itself.
