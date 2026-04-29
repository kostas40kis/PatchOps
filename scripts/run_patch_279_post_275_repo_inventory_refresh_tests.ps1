& {
param(
    [string]$RepoRoot = 'C:\dev\trader',
    [string]$VenvPython = '',
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$patchNumber = '279'
$patchName = 'post_275_repo_inventory_refresh'
$purpose = 'Refresh maintained repo inventory so it reflects the post-275 file layout and evidence posture.'
$safety = 'Review-only repo-inventory refresh. No live behavior widening, no wallet changes, no order submission.'

if ([string]::IsNullOrWhiteSpace($VenvPython)) {
    $VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
}

$desktop = [Environment]::GetFolderPath('Desktop')
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$reportPath = Join-Path $desktop ("patch_{0}_{1}_{2}.txt" -f $patchNumber, $patchName, $timestamp)
$lines = [System.Collections.Generic.List[string]]::new()

function Add-Line {
    param([AllowNull()][string]$Text)
    if ($null -eq $Text) { $Text = '' }
    $script:lines.Add($Text) | Out-Null
}

function Add-Section {
    param([string]$Title)
    Add-Line ''
    Add-Line ('=' * 120)
    Add-Line $Title
    Add-Line ('=' * 120)
}

function Write-Report {
    $content = ($script:lines -join [Environment]::NewLine) + [Environment]::NewLine
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($reportPath, $content, $utf8NoBom)
}

function Run-Native {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    if ($null -ne $psi.ArgumentList) {
        foreach ($arg in $Arguments) { [void]$psi.ArgumentList.Add($arg) }
    } else {
        $psi.Arguments = ($Arguments | ForEach-Object {
            if ($_ -match '\s') { '"' + ($_ -replace '"','\"') + '"' } else { $_ }
        }) -join ' '
    }
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    [void]$p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    return [pscustomobject]@{ ExitCode = [int]$p.ExitCode; Stdout = $stdout; Stderr = $stderr }
}

$exitCode = 1
try {
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line "Purpose    : $purpose"
    Add-Line "Safety     : $safety"
    Add-Line "RepoRoot   : $RepoRoot"
    Add-Line "VenvPython : $VenvPython"
    Add-Line "ReportPath : $reportPath"

    if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "Repo root not found: $RepoRoot" }
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Venv python not found: $VenvPython" }

    Set-Location $RepoRoot

    Add-Section 'COMPILE COMMAND'
    $compileArgs = @('-m','compileall','-q','src','tests')
    Add-Line ("Command : {0} {1}" -f $VenvPython, ($compileArgs -join ' '))
    $compile = Run-Native -FilePath $VenvPython -Arguments $compileArgs -WorkingDirectory $RepoRoot
    Add-Line ("ExitCode : {0}" -f $compile.ExitCode)
    Add-Section 'COMPILE STDOUT'
    Add-Line $compile.Stdout
    Add-Section 'COMPILE STDERR'
    Add-Line $compile.Stderr
    if ($compile.ExitCode -ne 0) { $exitCode = $compile.ExitCode; throw 'compileall failed' }

    Add-Section 'FOCUSED TEST COMMAND'
    $testArgs = @('-m','unittest','tests.test_post_275_repo_inventory_refresh')
    Add-Line ("Command : {0} {1}" -f $VenvPython, ($testArgs -join ' '))
    $test = Run-Native -FilePath $VenvPython -Arguments $testArgs -WorkingDirectory $RepoRoot
    $exitCode = $test.ExitCode
    Add-Line ("ExitCode : {0}" -f $test.ExitCode)
    Add-Section 'STDOUT'
    Add-Line $test.Stdout
    Add-Section 'STDERR'
    Add-Line $test.Stderr

    Add-Section 'SUMMARY'
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line "Safety     : $safety"
    Add-Line "ExitCode   : $exitCode"
    if ($exitCode -eq 0) { Add-Line 'Result     : PASS' } else { Add-Line 'Result     : FAIL' }
    Add-Line "ReportPath : $reportPath"
    Write-Report
    Write-Host $reportPath
    exit $exitCode
}
catch {
    Add-Section 'EXCEPTION'
    Add-Line $_.Exception.Message
    if ($exitCode -eq 0) { $exitCode = 1 }
    Add-Section 'SUMMARY'
    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line "ExitCode   : $exitCode"
    if ($exitCode -eq 0) { Add-Line 'Result     : PASS' } else { Add-Line 'Result     : FAIL' }
    Add-Line "ReportPath : $reportPath"
    Write-Report
    Write-Host $reportPath
    exit $exitCode
}
}
