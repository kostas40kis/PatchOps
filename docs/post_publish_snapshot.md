# Post-publish snapshot

## Purpose
This packet records the first published maintenance state after the Patch 21 through Patch 25A stream landed and the repository was pushed to GitHub on the `main` branch.

It exists so a future maintainer or LLM can start from the published state instead of reconstructing recent work from scattered Desktop reports.

## Published state captured here
The repo is published after **Patch 25A** with the recent maintenance stream green and pushed.

The maintained surfaces now include:
- `run-package`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `maintenance-gate`
- `emit-operator-script`
- `bootstrap-repair`
- `Push-PatchOpsToGitHub.ps1`

The working operator assumption remains:
- start from the published repo on `main`
- preserve one canonical Desktop txt report per PatchOps-driven run
- keep PowerShell thin and operator-facing
- keep reusable mechanics in Python

## What a maintainer should do first
1. Clone or pull the published repo state.
2. Run the maintained validation loop.
3. Use `maintenance-gate` to get one current health answer.
4. Use `emit-operator-script` only for thin generated helper scripts.
5. Use `bootstrap-repair` only when the normal CLI import chain is too broken to use the standard flow.
6. Use `Push-PatchOpsToGitHub.ps1` only after review, commit, and deliberate operator intent.

## Baseline validation loop
```powershell
& {
    Set-Location "C:\dev\patchops"
    py -m pytest -q
    py -m patchops.cli maintenance-gate
}
```

## Notes
This packet is additive. It does not replace the earlier freeze/closeout docs.
It gives a simple published-state handoff after the first GitHub push from the repo-owned publish helper era.
