# GitHub publish helper

## Purpose
`powershell/Push-PatchOpsToGitHub.ps1` is the maintained manual helper for publishing the reviewed PatchOps repository to GitHub after a patch stream is already green.

It exists to preserve the already-used local upload flow in repo truth rather than leaving it only in chat history.

## Guardrails
- This helper is **manual** and **operator-reviewed**.
- It is **not** the default next step after every patch.
- It is **not a second apply engine**.
- PatchOps still uses manifests, bundles, and canonical reports to prove repo truth before any push happens.

## Current maintained target
Default values are:

- repo path: `C:\dev\patchops`
- remote URL: `https://github.com/kostas40kis/PatchOps.git`
- branch: `main`

## Compatibility
The helper keeps Windows PowerShell 5.1 compatibility by using:

- `Convert-ToWindowsArgumentString`
- `ProcessStartInfo.Arguments`

It intentionally does **not** depend on `ProcessStartInfo.ArgumentList`.

## Safety features
The helper:
- checks that `git` is available,
- verifies `user.name` and `user.email`,
- handles a stale `.git\index.lock`,
- updates `.gitignore` with local/generated exclusions including `data/runtime/`,
- stages maintained PatchOps source surfaces,
- prints staged status before commit,
- commits only when changes exist,
- pushes with explicit branch handling.

## Example
```powershell
& {
    Set-Location "C:\dev\patchops"
    powershell -NoProfile -ExecutionPolicy Bypass -File ".\powershell\Push-PatchOpsToGitHub.ps1" -CommitMessage "Update PatchOps after maintenance closeout"
}
```

## When to use it
Use this helper only after:
1. the canonical report says PASS,
2. validation is green,
3. you have reviewed the repo changes you intend to publish.
