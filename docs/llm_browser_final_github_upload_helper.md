# LLM Browser Final GitHub Upload Helper

This document is the final GitHub upload helper for the PatchOps LLM browser dry-mode closeout.

It is intentionally manual and operator-controlled. It does not run git commit and it does not run git push.

## Required pre-upload validation

Before uploading to GitHub, run the final closeout helper:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\dev\patchops
```

The final closeout report must show:

- `Result : PASS`;
- `ExitCode : 0`;
- final operator checkpoint evidence exists;
- closeout checkpoint evidence exists;
- broad-validation report evidence exists;
- broad-validation parser returns PASS under `--strict`;
- release-gate returns PASS;
- passive checkpoint returns PASS;
- git status is captured;
- manual commit and push commands are printed.

Do not upload to GitHub if the final closeout report is FAIL.

## Report pointers to review

Open the final closeout pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt"
```

Open the final operator checkpoint pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt"
```

Open the closeout checkpoint pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt"
```

Open the broad-validation pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt"
```

All report files should be findable through:

```text
%USERPROFILE%\Desktop\patchops_reports\
```

## Copy the final closeout report to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Parse the latest broad-validation report

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict
```

## Manual GitHub upload commands

Run these manually only after reviewing a PASS final closeout report:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```

## Post-upload verification

After pushing, verify the local branch and the latest commit:

```powershell
cd C:\dev\patchops
git status --short --branch
git log -1 --oneline
```

Expected local result:

- branch is on `main`;
- local branch is not behind `origin/main`;
- `git status --short --branch` is clean or only shows intentional local files;
- latest commit message is visible from `git log -1 --oneline`.

## Optional remote verification

Use this only if you want a remote ref check:

```powershell
cd C:\dev\patchops
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
```

The two hashes should match after a successful push.

## Safety contract

The GitHub upload helper docs do not:

- run git commit;
- run git push;
- stage files automatically;
- create a commit automatically;
- start a browser;
- start Selenium;
- click or download artifacts;
- run PatchOps packages;
- paste into the ChatGPT composer;
- submit or send a message;
- create a localhost service.

The operator runs the GitHub commands manually after reviewing validation evidence.

## Failure handling

If any validation command fails:

1. Do not run `git add -A`.
2. Do not run `git commit`.
3. Do not run `git push`.
4. Open the final closeout report.
5. Repair the first failing command section.
6. Rerun the final closeout helper.
7. Upload only after the final closeout report is PASS.

## Handoff note

After a successful manual push, the dry-mode browser-runner stream can be treated as uploaded to GitHub. Future live-adapter work remains a separate stream and must not silently expand this dry-mode closeout into live browser automation.
