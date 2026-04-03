# PatchOps operator quickstart

This guide is the shortest safe path for using PatchOps in a real workspace.

## Recommended Stage 1 flow

1. Run `patchops profiles` or `Invoke-PatchProfiles.ps1` to see available profiles.
2. Run `patchops doctor --profile <name>` or `Invoke-PatchDoctor.ps1` to confirm the environment is ready.
3. Run `patchops examples` or `Invoke-PatchExamples.ps1` to find the closest bundled example.
4. Run `patchops template` or `Invoke-PatchTemplate.ps1` to generate a starter manifest.
5. Replace placeholder paths, content, and commands in the manifest.
6. Run `patchops check <manifest>` to catch starter placeholders before real execution.
7. Run `patchops inspect <manifest>` to see normalized JSON.
8. Run `patchops plan <manifest>` to preview target root, runtime, report path, backup path, and command groups.
9. Run `patchops apply <manifest>` for real patch execution, or `patchops verify <manifest>` for narrow validation-only reruns.

## Safer first proving order

Use a throwaway generic target before touching trader.

- Start with `examples/generic_python_patch.json`
- Then prove backups with `examples/generic_backup_patch.json`
- Then practice narrow reruns with `examples/generic_verify_patch.json`
- Only after that should you move to trader-oriented examples

## When to use verify-only reruns

Use verify-only reruns when patch content is already correct and you only need a narrower validation pass or cleaner evidence.

## When to stop and repair the wrapper

If the target repo commands already pass but the report, launcher, quoting, or wrapper plumbing fails, treat it as a wrapper-only repair instead of reworking the target patch.
