# Profile System

Profiles isolate target-repo assumptions from the PatchOps core.

## Stage 1 profiles

- `trader`
- `generic_python`
- `generic_python_powershell`

## A profile can define

- default target root
- runtime path resolution
- backup root convention
- report prefix
- evidence discipline defaults
- profile notes for humans and future LLMs

## Why profiles exist

The wrapper must stay generic.

Target repos differ in:

- expected root location
- virtual environment layout
- report naming preference
- backup-root convention
- common runtime assumptions

Those differences belong in profiles rather than being hardcoded into the execution core.

## Profile discovery command

PatchOps now exposes a first-class profile discovery command:

```powershell
py -m patchops.cli profiles
py -m patchops.cli profiles --name trader
```

The output is JSON so it is easy for:

- humans to inspect
- future LLMs to consume
- documentation to quote precisely

The thin PowerShell launcher is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1 -Name trader
```

## Rule

Trader is the first profile, not the identity of the system.
The core must remain project-agnostic.

<!-- PATCHOPS_PATCH41_MIXED_PROFILE:START -->
## Mixed Python/PowerShell profile

Patch 41 hardens the `generic_python_powershell` profile as the conservative mixed-repo option.

Use this profile when a target repo has both:

- Python-driven validation or helper flows,
- and PowerShell scripts that still need to stay outside the wrapper core.

The intent is to broaden reuse without changing the core architecture shape.

The mixed profile should stay explicit about:

- mixed markers (`python`, `powershell`),
- conservative runtime candidates,
- and the rule that shell behavior remains a profile concern rather than a new generic core abstraction.
<!-- PATCHOPS_PATCH41_MIXED_PROFILE:END -->

<!-- PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:START -->
## Project-packet helper relationship to profiles

Profiles remain the executable abstraction.
The onboarding helpers do not replace profile choice; they make it more explicit and faster.

Current helper surfaces:
- `recommend-profile --target-root ...`
- `starter --profile ... --intent ...`

Correct relationship:
- profile = executable target assumptions
- project packet = maintained target-facing contract
- starter helper = conservative first-manifest scaffold tied to patch class

When in doubt, choose the smallest correct profile and the narrowest starter intent.
<!-- PATCHOPS_PATCH84_PROFILE_SYSTEM_HELPERS:END -->
