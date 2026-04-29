# LLM Browser Final Post-push Verification

This document describes the final post-push verification workflow for the PatchOps LLM browser dry-mode closeout.

Use it only after the final closeout validation passed and the operator manually ran the GitHub upload commands.

## Precondition

Before post-push verification, the operator must have manually run:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```

These commands are not run automatically by PatchOps helper scripts.

## Primary post-push verification command sequence

Run:

```powershell
cd C:\dev\patchops
git status --short --branch
git log -1 --oneline
git fetch origin main
git rev-parse HEAD
git rev-parse origin/main
```

Expected result:

- local branch is `main`;
- local branch is not behind `origin/main`;
- `git status --short --branch` is clean or only shows intentional local files;
- latest commit message is visible in `git log -1 --oneline`;
- `git rev-parse HEAD` matches `git rev-parse origin/main`.

## Optional final validation after push

After pushing, the operator may rerun the passive release checks:

```powershell
cd C:\dev\patchops
py -m patchops.cli llm-browser release-gate --repo-root C:\dev\patchops --json
py -m patchops.cli llm-browser checkpoint --repo-root C:\dev\patchops --json
```

Expected result:

- release-gate returns `PASS`;
- checkpoint returns `PASS`;
- checkpoint may report a clean git status after the push.

## Report pointers to preserve

The final evidence should remain accessible from Desktop:

```text
%USERPROFILE%\Desktop\patchops_reports\
%USERPROFILE%\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

Open the final closeout pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt"
```

Open the broad-validation pointer:

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt"
```

## Copy final closeout evidence to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Final repository state interpretation

After successful post-push verification:

- D0 dry-mode browser-runner closeout is uploaded to GitHub;
- latest local commit matches `origin/main`;
- final closeout evidence is preserved under `Desktop\patchops_reports`;
- future live-adapter work remains a separate stream;
- no live browser automation is implied by this dry-mode closeout.

## Failure handling

If post-push verification fails:

1. Do not create another commit until the failure is understood.
2. Capture `git status --short --branch`.
3. Capture `git log -1 --oneline`.
4. Capture `git rev-parse HEAD`.
5. Capture `git rev-parse origin/main`.
6. Check whether the push failed, the remote changed, or the local branch is not on `main`.
7. Fix the git state intentionally.
8. Rerun post-push verification.

## Safety contract

The post-push verification docs do not:

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

The operator performs post-push verification manually.
