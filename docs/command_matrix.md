# PatchOps command matrix

| Goal | Python CLI | PowerShell launcher | Notes |
|---|---|---|---|
| Show available profiles | `patchops profiles` | `Invoke-PatchProfiles.ps1` | Start here if you do not know which profile to use |
| Preflight environment | `patchops doctor --profile trader` | `Invoke-PatchDoctor.ps1 -Profile trader` | Checks profile visibility, workspace guess, desktop, Python, and PowerShell |
| Discover bundled examples | `patchops examples` | `Invoke-PatchExamples.ps1` | Helps future LLMs pick the closest example before generating a new manifest |
| Generate starter manifest | `patchops template --profile trader --mode apply --patch-name my_patch` | `Invoke-PatchTemplate.ps1` | Can also write directly to disk with `--output-path` |
| Check starter manifest quality | `patchops check .\examples\generic_backup_patch.json` | `Invoke-PatchCheck.ps1` | Flags starter placeholders before apply or verify |
| Inspect normalized manifest | `patchops inspect .\examples\generic_python_patch.json` | n/a | Shows the normalized JSON contract |
| Preview execution plan | `patchops plan .\examples\generic_python_patch.json` | n/a | Shows resolved profile, report path pattern, backup path pattern, files, and commands |
| Apply a manifest | `patchops apply <manifest>` | `Invoke-PatchManifest.ps1` | Real patch execution |
| Run verify-only flow | `patchops verify <manifest>` | `Invoke-PatchVerify.ps1` | Narrow rerun and validation-only path |

## Recommended command order

`profiles` -> `doctor` -> `examples` -> `template` -> `check` -> `inspect` -> `plan` -> `apply` or `verify`
