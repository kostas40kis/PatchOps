& {
param(
    [string]$RepoRoot = 'C:\dev\trader',
    [string]$VenvPython = '',
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$patchNumber = '278'
$patchName = 'post_275_test_matrix_refresh'
$desktop = [Environment]::GetFolderPath('Desktop')
if ([string]::IsNullOrWhiteSpace($desktop)) { $desktop = $HOME }
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$reportPath = Join-Path $desktop "patch_${patchNumber}_${patchName}_tests_$timestamp.txt"
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
    $parent = Split-Path -Parent $reportPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($reportPath, ($lines -join [Environment]::NewLine) + [Environment]::NewLine, $utf8NoBom)
}

try {
    if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "Repo root not found: $RepoRoot" }
    if ([string]::IsNullOrWhiteSpace($VenvPython)) {
        $VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe'
    }
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Venv python not found: $VenvPython" }

    Add-Line "Patch      : $patchNumber"
    Add-Line "PatchName  : $patchName"
    Add-Line 'Purpose    : Run focused Patch 278 validation.'
    Add-Line 'Safety     : Review-only test-matrix refresh. No live behavior widening.'
    Add-Line "RepoRoot   : $RepoRoot"
    Add-Line "Python     : $VenvPython"
    Add-Line "ReportPath : $reportPath"

    Add-Section 'FILE EXISTENCE CHECK'
    $targets = @(
        'src\trader\execution\post_275_test_matrix_refresh.py',
        'docs\architecture\post_275_test_matrix_refresh.md',
        'tests\test_post_275_test_matrix_refresh.py',
        'scripts\run_patch_278_post_275_test_matrix_refresh_tests.ps1',
        'trader_test_matrix.md'
    )
    foreach ($target in $targets) {
        $path = Join-Path $RepoRoot $target
        if (Test-Path -LiteralPath $path) { Add-Line "EXISTS : $path" } else { Add-Line "MISSING : $path"; throw "Missing target: $target" }
    }

    Add-Section 'COMPILE COMMAND'
    $compileArgs = @('-m','compileall','-q','src','tests')
    Add-Line "Command : $VenvPython $($compileArgs -join ' ')"
    $compile = & $VenvPython @compileArgs 2>&1
    $compileCode = $LASTEXITCODE
    Add-Line "ExitCode : $compileCode"
    Add-Line ($compile | Out-String)
    if ($compileCode -ne 0) { throw "compileall failed with exit code $compileCode" }

    Add-Section 'FOCUSED TEST COMMAND'
    $testArgs = @('-m','unittest','tests.test_post_275_test_matrix_refresh')
    Add-Line "Command : $VenvPython $($testArgs -join ' ')"
    $output = & $VenvPython @testArgs 2>&1
    $testCode = $LASTEXITCODE
    Add-Line "ExitCode : $testCode"
    Add-Line ($output | Out-String)

    Add-Section 'SUMMARY'
    Add-Line "ExitCode   : $testCode"
    if ($testCode -eq 0) { Add-Line 'Result     : PASS' } else { Add-Line 'Result     : FAIL' }
    Add-Line "ReportPath : $reportPath"
    Write-Report
    Write-Host $reportPath
    exit ([int]$testCode)
}
catch {
    Add-Section 'EXCEPTION'
    Add-Line $_.Exception.Message
    Add-Section 'SUMMARY'
    Add-Line 'ExitCode   : 1'
    Add-Line 'Result     : FAIL'
    Add-Line "ReportPath : $reportPath"
    Write-Report
    Write-Host $reportPath
    exit 1
}
}
