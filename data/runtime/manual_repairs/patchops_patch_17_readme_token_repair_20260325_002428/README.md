# PatchOps

PatchOps is a project-agnostic patch execution harness for Windows-first patch workflows.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## Current Stage 1 command surface

- `patchops apply <manifest>`
- `patchops verify <manifest>`
- `patchops inspect <manifest>`
- `patchops plan <manifest> [--mode apply|verify]`
- `patchops profiles`
- `patchops template --profile ... --mode ... [--patch-name ...] [--output-path ...]`
- `patchops check <manifest>`
- `patchops doctor [--profile ...] [--target-root ...]`
- `patchops examples [--profile ...]`
- `patchops schema`

Thin PowerShell launchers under `powershell/` mirror the main authoring and discovery commands.

## Recommended safe first-use flow

1. `patchops profiles`
2. `patchops doctor --profile ...`
3. `patchops examples`
4. `patchops schema`
5. `patchops template ...`
6. `patchops check ...`
7. `patchops inspect ...`
8. `patchops plan ...`
9. `patchops apply ...` or `patchops verify ...`

## Example coverage

PatchOps ships example manifests for:

- generic apply
- backup proof
- verify-only
- trader examples
- Generic Python + PowerShell profile examples
- report preference examples
- command-group examples
- content-path examples

The content-path example is useful when a manifest should write a file from an external text artifact instead of embedding the full content inline.
