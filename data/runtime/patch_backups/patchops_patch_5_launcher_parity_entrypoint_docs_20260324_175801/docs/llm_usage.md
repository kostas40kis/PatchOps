# LLM Usage

A future LLM should be able to use PatchOps with this sequence:

1. Read `README.md`, `docs/overview.md`, and `docs/manifest_schema.md`.
2. Pick a profile from `docs/profile_system.md`.
3. Generate target file contents.
4. Generate a JSON manifest.
5. Run `patchops inspect <manifest>`.
6. Run `patchops plan <manifest>`.
7. Run `patchops apply <manifest>` or `patchops verify <manifest>`.
8. Inspect the single report path printed by the CLI.

## Why the new `plan` command matters

`inspect` proves the manifest shape.

`plan` proves how the wrapper resolves that manifest into:

- the active profile
- target root
- runtime path
- report path pattern
- backup path pattern
- target file set
- command groups

That makes PatchOps safer to use before touching a real repo such as `C:\dev\trader`.

## Ground rules

- Do not move target-repo business logic into PatchOps.
- Put repo-specific assumptions in the active profile.
- Keep PowerShell launchers thin.
- Use `inspect` and `plan` before real apply runs when validating a new manifest.
- Use verify-only reruns when patch content already exists and only evidence must be regenerated.