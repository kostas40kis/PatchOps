# LLM Usage

A future LLM should be able to use PatchOps with this sequence:

1. Read `README.md`, `docs/overview.md`, and `docs/manifest_schema.md`.
2. Pick a profile from `docs/profile_system.md`.
3. Generate target file contents.
4. Generate a JSON manifest.
5. Run `patchops apply <manifest>` or `patchops verify <manifest>`.
6. Inspect the single report path printed by the CLI.

## Ground rules

- Do not move target-repo business logic into PatchOps.
- Put repo-specific assumptions in the active profile.
- Keep PowerShell launchers thin.
- Use verify-only reruns when patch content already exists and only evidence must be regenerated.
