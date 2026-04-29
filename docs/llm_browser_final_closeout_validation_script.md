# LLM Browser Final Closeout Validation Script

This document is the final operator guide for closing the PatchOps LLM browser dry-mode stream.

It assumes the dry-mode stream has already shipped:

- broad-validation script;
- broad-validation parser;
- Desktop report folder;
- Desktop broad-validation pointer;
- closeout validation and push checkpoint script;
- Desktop closeout checkpoint pointer;
- future live-adapter plan.

The final validation path is intentionally operator-controlled. It does not commit or push automatically.

## Final command

Run this from the PatchOps repo:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops
```

This command can run the broad validation script, parse the latest broad-validation report, run release-gate/checkpoint smokes, capture git status, and print the manual commit/push commands.

## Expected closeout report outputs

The closeout script writes:

```text
%USERPROFILE%\Desktop\patchops_reports\patchops_llm_browser_closeout_checkpoint_YYYYMMDD_HHMMSS.txt
%USERPROFILE%\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt
```

It also reads the broad-validation pointer:

```text
%USERPROFILE%\Desktop\patchops_latest_llm_browser_broad_validation_report.txt
```

## Open the latest closeout pointer

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt"
```

## Open the latest broad-validation pointer

```powershell
notepad "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt"
```

## Copy the latest closeout report to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_closeout_checkpoint.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Copy the latest broad-validation report to clipboard

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
Get-Content $reportPath -Raw | Set-Clipboard
```

## Parse the latest broad-validation report

```powershell
$pointer = Get-Content "$env:USERPROFILE\Desktop\patchops_latest_llm_browser_broad_validation_report.txt" -Raw
$reportPath = [regex]::Match($pointer, 'ReportPath\s*:\s*(.+)').Groups[1].Value.Trim()
py -m patchops.cli llm-browser broad-report --path $reportPath --json --strict
```

## PASS requirements

A final closeout report is acceptable only when:

- `Result : PASS`;
- `ExitCode : 0`;
- the broad-validation report parser passes with `--strict`;
- the release gate reports `PASS`;
- the passive checkpoint reports `PASS`;
- git status is captured;
- manual commit/push commands are printed;
- the report and pointer paths are easy to find from Desktop.

## FAIL handling

If the final closeout report says `FAIL`:

1. Open the closeout pointer.
2. Open the closeout report path.
3. Find the `SUMMARY` section.
4. Inspect the first command with nonzero `ExitCode` or `TimedOut : True`.
5. Open the broad-validation pointer if the failure involves broad validation.
6. Do not commit or push.
7. Repair the failing layer and rerun the final command.

## Manual commit and push commands

The closeout report prints these commands. The operator runs them manually only after a PASS report has been reviewed:

```powershell
cd C:\dev\patchops
git status --short --branch
git add -A
git commit -m "Close out llm-browser dry-mode validation stream"
git push origin main
```

## Plan-only mode

Use plan-only mode only to prove report/pointer creation and inspect the intended command sequence:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops -PlanOnly
```

Plan-only is not final acceptance.

## Shorter local check

Use `-SkipFullPytest` only when intentionally doing a shorter local check through the nested broad-validation script:

```powershell
cd C:\dev\patchops
.\scripts\llm_browser_closeout_validation_push_checkpoint.ps1 -RepoRoot C:\dev\patchops -SkipFullPytest
```

A final closeout should not use `-SkipFullPytest`.

## Safety contract

The final closeout validation script does not:

- run git commit;
- run git push;
- start a browser;
- start Selenium;
- click or download artifacts;
- run PatchOps packages;
- paste into the ChatGPT composer;
- submit or send a message;
- create a localhost service.

It only runs validation commands, parses report evidence, captures git status, writes local reports, writes Desktop pointer files, and prints manual operator commands.

## Closeout interpretation

When the final closeout report is PASS and the operator has reviewed the report:

- the dry-mode stream is validated;
- the future live-adapter work remains a separate planned stream;
- the repository can be committed and pushed by the operator;
- no live browser automation has been shipped by this dry-mode closeout.
