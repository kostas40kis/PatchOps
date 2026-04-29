& {
param(
    [string]$RepoRoot = 'C:\dev\trader',
    [string]$VenvPython = '',
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$patchNumber = '277'
$patchName = 'post_275_patch_ledger_refresh'
$desktop = [Environment]::GetFolderPath('Desktop')
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$reportPath = Join-Path $desktop ("patch_{0}_{1}_tests_{2}.txt" -f $patchNumber, $patchName, $timestamp)
$lines = [System.Collections.Generic.List[string]]::new()

function Add-Line {
    param([AllowNull()][string]$Text)
    if ($null -eq $Text) { $Text = '' }
    $lines.Add($Text) | Out-Null
}

function Add-Section {
    param([string]$Title)
    Add-Line ''
    Add-Line ('=' * 120)
    Add-Line $Title
    Add-Line ('=' * 120)
}

function Write-Report {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($reportPath, (($lines -join [Environment]::NewLine) + [Environment]::NewLine), $utf8NoBom)
}

function Invoke-NativeCaptured {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [int]$TimeoutSeconds
    )
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    foreach ($arg in $Arguments) { [void]$psi.ArgumentList.Add($arg) }
    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi
    [void]$proc.Start()
    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()
    if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
        try { $proc.Kill() } catch { }
        return [pscustomobject]@{ ExitCode = 124; Stdout = $stdoutTask.Result; Stderr = ($stderrTask.Result + "`nProcess timed out after $TimeoutSeconds seconds."); TimedOut = $true }
    }
    return [pscustomobject]@{ ExitCode = [int]$proc.ExitCode; Stdout = $stdoutTask.Result; Stderr = $stderrTask.Result; TimedOut = $false }
}

$exitCode = 1
try {
    if ([string]::IsNullOrWhiteSpace($VenvPython)) {
        $VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
    }
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line 'Purpose    : Focused Patch 277 post-275 patch ledger refresh tests.'
    Add-Line 'Safety     : Review-only ledger validation. No live behavior widening.'
    Add-Line "RepoRoot   : $RepoRoot"
    Add-Line "VenvPython : $VenvPython"
    Add-Line "ReportPath : $reportPath"

    Add-Section 'PRECHECKS'
    if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "Repo root not found: $RepoRoot" }
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Venv python not found: $VenvPython" }
    Add-Line 'Repo root exists.'
    Add-Line 'Venv python exists.'

    Add-Section 'TARGET FILE DOUBLE-CHECK'
    $targets = @(
        'src\trader\execution\post_275_patch_ledger_refresh.py',
        'docs\architecture\post_275_patch_ledger_refresh.md',
        'tests\test_post_275_patch_ledger_refresh.py',
        'scripts\run_patch_277_post_275_patch_ledger_refresh_tests.ps1',
        'trader_patch_ledger.md'
    )
    foreach ($target in $targets) {
        $path = Join-Path $RepoRoot $target
        if (Test-Path -LiteralPath $path) { Add-Line "EXISTS : $path" } else { Add-Line "MISSING : $path"; throw "Missing target: $target" }
    }

    Add-Section 'TEST COMMAND'
    $args = @('-m', 'unittest', 'tests.test_post_275_patch_ledger_refresh')
    Add-Line ("WorkingDirectory : {0}" -f $RepoRoot)
    Add-Line ("Command          : {0} {1}" -f $VenvPython, ($args -join ' '))
    $env:PYTHONPATH = ((Join-Path $RepoRoot 'src') + ';' + $RepoRoot)
    $result = Invoke-NativeCaptured -FilePath $VenvPython -Arguments $args -WorkingDirectory $RepoRoot -TimeoutSeconds $TimeoutSeconds
    $exitCode = [int]$result.ExitCode
    Add-Line ("ExitCode         : {0}" -f $exitCode)
    Add-Line ("TimedOut         : {0}" -f $result.TimedOut)
    Add-Section 'STDOUT'
    Add-Line $result.Stdout
    Add-Section 'STDERR'
    Add-Line $result.Stderr

    Add-Section 'SUMMARY'
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line "ExitCode   : $exitCode"
    if ($exitCode -eq 0) { Add-Line 'Result     : PASS' } else { Add-Line 'Result     : FAIL' }
    Add-Line "ReportPath : $reportPath"
} catch {
    Add-Section 'EXCEPTION'
    Add-Line $_.Exception.Message
    Add-Section 'SUMMARY'
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line 'ExitCode   : 1'
    Add-Line 'Result     : FAIL'
    Add-Line "ReportPath : $reportPath"
    $exitCode = 1
} finally {
    Write-Report
    Write-Host $reportPath
}
exit $exitCode
}
