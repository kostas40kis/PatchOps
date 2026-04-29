# LLM Browser Closeout Validation and Push Checkpoint

This document describes the final operator checkpoint for the PatchOps LLM browser dry-mode stream.

The checkpoint is intentionally operator-controlled. It produces evidence and command guidance. It does not commit or push automatically.

## Command

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops
```

Default outputs:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_closeout_checkpoint_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
```

The checkpoint also reads the broad-validation pointer:

```text
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## What it validates

The checkpoint:

- runs the operator broad-validation script unless `-SkipBroadValidation` is supplied;
- parses the latest broad-validation report with `llm-browser broad-report --json --strict`;
- runs the dry-mode release gate;
- runs the passive checkpoint command;
- captures git status;
- writes one closeout report under `Desktop\patchops_reports`;
- writes a Desktop pointer to the latest closeout report;
- prints commit and push commands for the operator to run manually.

## Plan-only mode

```powershell
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only proves report/pointer creation and shows the intended commands without running validation.

## Shorter local check

```powershell
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops -SkipFullPytest
```

Use `-SkipFullPytest` only when you intentionally want the nested broad-validation script to skip full pytest.

## Manual commit and push commands

The report prints these commands, but does not run them:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```


## Explicit git safety literals

The checkpoint does not run git commit.

The checkpoint does not run git push.

## Safety contract

The closeout checkpoint does not:

- run git commit;
- run git push;
- start a browser;
- start Selenium;
- click or download artifacts;
- run PatchOps packages;
- paste into the ChatGPT composer;
- submit or send a message;
- create a localhost service.

It only collects validation evidence and shows operator commands.
