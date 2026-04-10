param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [string]$WrapperRepoRoot = "C:\dev\patchops",

    [string]$PythonExe = "py",

    [switch]$PassThruRawOutput
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Convert-ToWindowsArgumentString {
    param([Parameter(Mandatory = $true)][string[]]$Args)

    $escaped = foreach ($arg in $Args) {
        if ($null -eq $arg -or $arg -eq '') {
            '""'
        }
        elseif ($arg -notmatch '[\s"]') {
            $arg
        }
        else {
            '"' + (($arg -replace '(\\*)"', '$1$1\\"') -replace '(\\+)$', '$1$1') + '"'
        }
    }

    $escaped -join ' '
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $psi.Arguments = Convert-ToWindowsArgumentString -Args $Arguments

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    [pscustomobject]@{
        ExitCode = $process.ExitCode
        StdOut   = $stdout
        StdErr   = $stderr
    }
}

function Get-ReportField {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Name
    )

    $pattern = '(?m)^{0}\s*:\s*(.+)$' -f [regex]::Escape($Name)
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }

    return $null
}

if (-not (Test-Path -LiteralPath $PackagePath)) {
    throw ("Package path does not exist: {0}" -f $PackagePath)
}
if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
    throw ("Wrapper repo root does not exist: {0}" -f $WrapperRepoRoot)
}

$resolvedPackage = (Resolve-Path -LiteralPath $PackagePath).Path
$resolvedWrapper = (Resolve-Path -LiteralPath $WrapperRepoRoot).Path

$cmdArgs = @(
    '-m',
    'patchops.cli',
    'run-package',
    $resolvedPackage,
    '--wrapper-root',
    $resolvedWrapper
)

$result = Invoke-NativeCapture -FilePath $PythonExe -Arguments $cmdArgs -WorkingDirectory $resolvedWrapper

$reportPath = Get-ReportField -Text $result.StdOut -Name 'Canonical Report Path'
if ([string]::IsNullOrWhiteSpace($reportPath)) {
    $reportPath = Get-ReportField -Text $result.StdOut -Name 'Report Path'
}

$summaryText = $result.StdOut
if (-not [string]::IsNullOrWhiteSpace($reportPath) -and (Test-Path -LiteralPath $reportPath)) {
    $summaryText = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8
}

$patchName = Get-ReportField -Text $summaryText -Name 'Patch Name'
if ([string]::IsNullOrWhiteSpace($patchName)) {
    $patchName = [IO.Path]::GetFileNameWithoutExtension($resolvedPackage)
}
$runResult = Get-ReportField -Text $summaryText -Name 'Result'
if ([string]::IsNullOrWhiteSpace($runResult)) {
    $runResult = $(if ($result.ExitCode -eq 0) { 'PASS' } else { 'FAIL' })
}
$exitCodeText = Get-ReportField -Text $summaryText -Name 'ExitCode'
if ([string]::IsNullOrWhiteSpace($exitCodeText)) {
    $exitCodeText = [string]$result.ExitCode
}
$failureCategory = Get-ReportField -Text $summaryText -Name 'Failure Category'
if ([string]::IsNullOrWhiteSpace($failureCategory)) {
    $failureCategory = '(none)'
}

if ($PassThruRawOutput) {
    if (-not [string]::IsNullOrWhiteSpace($result.StdOut)) { Write-Host $result.StdOut }
    if (-not [string]::IsNullOrWhiteSpace($result.StdErr)) { Write-Host $result.StdErr }
}

Write-Host 'PATCHOPS RUN-PACKAGE'
Write-Host '--------------------'
Write-Host ('Patch      : {0}' -f $patchName)
Write-Host ('Result     : {0}' -f $runResult)
Write-Host ('ExitCode   : {0}' -f $exitCodeText)
Write-Host ('Failure    : {0}' -f $failureCategory)
Write-Host ('ReportPath : {0}' -f $(if ([string]::IsNullOrWhiteSpace($reportPath)) { '(not found)' } else { $reportPath }))

exit $result.ExitCode
