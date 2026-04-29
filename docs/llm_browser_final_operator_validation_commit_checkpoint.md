# LLM Browser Final Operator Validation and Commit Checkpoint

This document describes the final operator checkpoint before manually committing and pushing the LLM browser dry-mode closeout.

The checkpoint collects evidence and prints commands. It does not commit or push automatically.

## Command

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_final_operator_validation_commit_checkpoint.ps1 -RepoRoot C:\dev\patchops
```

Default outputs:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_final_operator_commit_checkpoint_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt
```

The checkpoint reads these pointers:

```text
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## What it validates

The final operator checkpoint:

- runs the closeout validation and push checkpoint unless `-SkipCloseoutValidation` is supplied;
- reads the closeout checkpoint pointer;
- reads the broad-validation pointer;
- parses the latest broad-validation report using `llm-browser broad-report --path ... --json --strict`;
- runs the dry-mode release gate;
- runs the passive checkpoint command;
- captures git status;
- writes one final operator checkpoint report under `Desktop\patchops_reports`;
- writes a Desktop pointer to the latest final operator checkpoint report;
- prints manual commit and push commands.

## Plan-only mode

```powershell
.\scripts\llm_browser_final_operator_validation_commit_checkpoint.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only proves report/pointer creation and shows intended commands. Plan-only is not final acceptance.

## Shorter local check

```powershell
.\scripts\llm_browser_final_operator_validation_commit_checkpoint.ps1 -RepoRoot C:\dev\patchops -SkipFullPytest
```

Use `-SkipFullPytest` only when intentionally doing a shorter local check through the nested closeout/broad-validation path.

A final operator closeout should not use `-SkipFullPytest`.

## Manual commit and push commands

The final operator checkpoint prints these commands, but does not run them:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```

## Open the latest final checkpoint pointer

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt"
```

## Copy the latest final checkpoint report to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_final_operator_commit_checkpoint.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## PASS requirements

The final checkpoint is acceptable only when:

- `Result : PASS`;
- `ExitCode : 0`;
- closeout checkpoint evidence exists;
- broad-validation report evidence exists;
- broad-validation parser returns PASS under `--strict`;
- release-gate returns PASS;
- passive checkpoint returns PASS;
- git status is captured;
- manual commit and push commands are printed.


## Explicit git safety literals

The final operator checkpoint does not run git commit.

The final operator checkpoint does not run git push.

## Safety contract

The final operator checkpoint does not:

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
