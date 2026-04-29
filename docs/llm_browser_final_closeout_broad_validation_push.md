# LLM Browser Final Closeout Broad Validation and Push

This document describes the final operator-run helper before manual commit and push.

The helper validates the dry-mode closeout evidence and prints the final manual git commands. It does not run git commit and it does not run git push.

## Command

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\dev\patchops
```

Default outputs:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_final_closeout_broad_validation_push_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt
```

The helper reads these existing pointer files:

```text
%USERPROFILE%\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## What it validates

The helper:

- runs the final operator validation and commit checkpoint unless `-SkipFinalOperatorCheckpoint` is supplied;
- reads the final operator checkpoint pointer;
- reads the closeout checkpoint pointer;
- reads the broad-validation pointer;
- parses the latest broad-validation report with `llm-browser broad-report --path ... --json --strict`;
- runs the dry-mode release gate;
- runs the passive checkpoint command;
- captures git status;
- writes one final closeout report under `Desktop\patchops_reports`;
- writes a Desktop pointer to the latest final closeout report;
- prints manual commit and push commands.

## Plan-only mode

```powershell
.\scripts\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only proves report/pointer creation and shows intended commands. Plan-only is not final acceptance.

## Shorter local check

```powershell
.\scripts\llm_browser_final_closeout_broad_validation_push.ps1 -RepoRoot C:\dev\patchops -SkipFullPytest
```

Use `-SkipFullPytest` only when intentionally doing a shorter local check through the nested validation path.

A final closeout should not use `-SkipFullPytest`.

## Manual commit and push commands

The final closeout helper prints these commands, but does not run them:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```

## Open the latest final closeout pointer

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt"
```

## Copy the latest final closeout report to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_closeout_broad_validation_push.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## PASS requirements

The final closeout helper is acceptable only when:

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

## Safety contract

The final closeout helper does not:

- run git commit;
- run git push;
- start a browser by itself;
- start Selenium by itself;
- click or download artifacts by itself;
- run PatchOps packages by itself;
- paste into the ChatGPT composer;
- submit or send a message;
- create a localhost service.

It only runs validation commands, parses report evidence, captures git status, writes local reports, writes Desktop pointer files, and prints manual operator commands.
