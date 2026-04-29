# LLM Browser Broad Validation One-command Runner

This document is the operator-facing one-command path for validating the PatchOps LLM browser dry-mode stream.

It is intentionally boring:

- one command creates the report;
- reports go to one Desktop folder;
- one Desktop pointer file tells you where the latest report is;
- one parser command can summarize the report;
- one clipboard command can copy the actual latest report content.

## Main command

Run from the PatchOps repo:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops
```

Default outputs:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_broad_validation_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## Open the latest pointer

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt"
```

The pointer file contains the latest report path and a Notepad command.

## Open the reports folder

```powershell
explorer "$env:USERPROFILE\Desktop\patchops_reports"
```

## Copy the actual latest report content to clipboard

This copies the real broad-validation report, not just the pointer file:

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Parse the latest report as JSON

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict
```

## Plan-only smoke

Use this when you want to prove report and pointer creation without running full pytest:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only still writes:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_broad_validation_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## Skip full pytest intentionally

Use this only when you are deliberately doing a shorter local check:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_broad_validation.ps1 -RepoRoot C:\dev\patchops -SkipFullPytest
```

Normal acceptance should not use `-SkipFullPytest`.

## Expected PASS interpretation

A PASS broad-validation report means:

- compileall passed;
- the dry-mode release gate passed;
- the checkpoint command passed;
- the dependency doctor for `--browser none` passed;
- missing audit-log readback behaved safely;
- full pytest passed unless `-SkipFullPytest` was intentionally supplied;
- the report parser can summarize the result.

## Failure interpretation

If the report says FAIL:

1. Open the pointer file.
2. Open the report path shown inside it.
3. Look at the `SUMMARY` section.
4. Look at the first command section whose `ExitCode` is nonzero or whose `TimedOut` field is `True`.
5. Use `llm-browser broad-report --path <report> --json` for a compact machine-readable summary.
6. Do not commit or push until the failing command is repaired.

## Safety contract

The broad-validation one-command runner is an operator validation helper.

It does not:

- start a browser;
- start Selenium;
- click or download artifacts;
- run PatchOps packages;
- paste into the ChatGPT composer;
- submit or send a message;
- run git commit;
- run git push;
- create a localhost service.

It only validates the current dry-mode surfaces and writes local report artifacts.
