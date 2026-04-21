# Canonical run-package operator runner

## Purpose

`Invoke-QuietRunPackage.ps1` is the single canonical operator-facing wrapper for run-package when less live console noise is preferred.

Keep PowerShell thin.
Keep reusable mechanics in Python.
Keep one canonical Desktop txt report.

## Usage

Set-Location C:\dev\patchops
.\powershell\Invoke-QuietRunPackage.ps1 -PackagePath <zip> -WrapperRepoRoot C:\dev\patchops -VerboseConsole

The report path is the source of truth.
