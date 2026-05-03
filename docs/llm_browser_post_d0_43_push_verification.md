# LLM Browser Post-D0.43 Push Verification

This document describes the post-D0.43 push verification helper.

D0.43 recorded the final validation/GitHub upload evidence. D0.44 adds the helper that verifies D0.43 itself was later manually committed and pushed.

## Precondition

Before running the verification helper without `-PlanOnly`, manually run:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "D0.43 record final validation and GitHub upload evidence"
git push origin main
```

The helper does not run git add, does not run git commit, and does not run git push.

## Primary command

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_post_d0_43_push_verification.ps1 -RepoRoot C:\dev\patchops
```

Default outputs:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_post_d0_43_push_verification_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_post_d0_43_push_verification.txt
```

## Plan-only command

```powershell
.\scripts\llm_browser_post_d0_43_push_verification.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only proves report and pointer creation, but does not verify GitHub state.

## What the helper checks

The helper runs:

```powershell
git status --short --branch
git fetch origin main
git log -1 --oneline
git rev-parse HEAD
git rev-parse origin/main
git status --short --branch
```

It passes only when:

- `HEAD` matches `origin/main`;
- `git status --short --branch` shows `## main...origin/main`;
- the working tree has no modified, staged, conflicted, or untracked files;
- the latest commit message contains `D0.43 record final validation and GitHub upload evidence`.

## Clipboard command

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_post_d0_43_push_verification.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Safety contract

The helper does not:

- run git add;
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

## Interpretation

When the helper returns PASS after D0.43 has been manually committed and pushed, the D0 dry-mode browser-runner stream is ready for the final acceptance marker.

The next patch after this helper should be the final D-phase acceptance marker, unless post-push verification evidence fails and requires repair.
