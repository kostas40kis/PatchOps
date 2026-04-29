& {
param(
    [string]$RepoRoot = 'C:\dev\trader',
    [string]$VenvPython = '',
    [int]$TimeoutSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PatchNumber = '276'
$PatchName = 'post_275_frontier_truth_sync'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$desktop = [Environment]::GetFolderPath('Desktop')
$ReportPath = Join-Path $desktop ("patch_{0}_{1}_{2}.txt" -f $PatchNumber, $PatchName, $timestamp)
$lines = [System.Collections.Generic.List[string]]::new()

function Add-Line {
    param([AllowNull()][string]$Text)
    if ($null -eq $Text) { $Text = '' }
    [void]$lines.Add($Text)
}

function Write-Utf8NoBomFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )
    $parent = Split-Path -Path $Path -Parent
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Invoke-ProcessWithTimeout {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][int]$TimeoutSeconds
    )

    $stdoutPath = Join-Path ([System.IO.Path]::GetTempPath()) ("patch276_stdout_{0}.txt" -f ([guid]::NewGuid().ToString('N')))
    $stderrPath = Join-Path ([System.IO.Path]::GetTempPath()) ("patch276_stderr_{0}.txt" -f ([guid]::NewGuid().ToString('N')))
    $process = Start-Process -FilePath $FilePath -ArgumentList $Arguments -WorkingDirectory $WorkingDirectory -PassThru -NoNewWindow -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
    $completed = $process.WaitForExit($TimeoutSeconds * 1000)
    if (-not $completed) {
        try { $process.Kill() } catch { }
        $stdout = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { '' }
        $stderr = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { '' }
        return [PSCustomObject]@{
            ExitCode = 124
            TimedOut = $true
            StdOut = $stdout
            StdErr = ($stderr + [Environment]::NewLine + "Process timed out after $TimeoutSeconds seconds.")
            CommandLine = ($FilePath + ' ' + ($Arguments -join ' '))
        }
    }
    $stdoutText = if (Test-Path -LiteralPath $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw } else { '' }
    $stderrText = if (Test-Path -LiteralPath $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw } else { '' }
    Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    return [PSCustomObject]@{
        ExitCode = [int]$process.ExitCode
        TimedOut = $false
        StdOut = $stdoutText
        StdErr = $stderrText
        CommandLine = ($FilePath + ' ' + ($Arguments -join ' '))
    }
}

try {
    if (-not (Test-Path -LiteralPath $RepoRoot)) { throw "Repo root not found: $RepoRoot" }
    $RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
    if ([string]::IsNullOrWhiteSpace($VenvPython)) { $VenvPython = Join-Path $RepoRoot '.venv\Scripts\python.exe' }
    if (-not (Test-Path -LiteralPath $VenvPython)) { throw "Venv python not found: $VenvPython" }

    $env:PYTHONPATH = (Join-Path $RepoRoot 'src') + ';' + $RepoRoot

    Add-Line "Patch      : $PatchNumber"
    Add-Line "PatchName  : $PatchName"
    Add-Line "RepoRoot   : $RepoRoot"
    Add-Line "Python     : $VenvPython"
    Add-Line "Safety     : Review-only/no-submit frontier metadata validation. No live behavior widening."
    Add-Line "ReportPath : $ReportPath"
    Add-Line ''

    $args = @('-m', 'unittest', 'tests.test_post_275_frontier_truth_sync')
    $result = Invoke-ProcessWithTimeout -FilePath $VenvPython -Arguments $args -WorkingDirectory $RepoRoot -TimeoutSeconds $TimeoutSeconds
    Add-Line "COMMAND    : $($result.CommandLine)"
    Add-Line "ExitCode   : $($result.ExitCode)"
    Add-Line "TimedOut   : $($result.TimedOut)"
    Add-Line ''
    Add-Line 'STDOUT'
    Add-Line '------'
    Add-Line $result.StdOut
    Add-Line ''
    Add-Line 'STDERR'
    Add-Line '------'
    Add-Line $result.StdErr
    Add-Line ''
    if ($result.ExitCode -eq 0) { Add-Line 'Result     : PASS' } else { Add-Line 'Result     : FAIL' }
    Add-Line "ReportPath : $ReportPath"

    Write-Utf8NoBomFile -Path $ReportPath -Content ($lines -join [Environment]::NewLine)
    Write-Host $ReportPath
    exit ([int]$result.ExitCode)
}
catch {
    Add-Line "ERROR      : $($_.Exception.Message)"
    Add-Line 'Result     : FAIL'
    Add-Line "ReportPath : $ReportPath"
    Write-Utf8NoBomFile -Path $ReportPath -Content ($lines -join [Environment]::NewLine)
    Write-Host $ReportPath
    exit 1
}
}
