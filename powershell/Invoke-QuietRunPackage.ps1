param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [string]$WrapperRepoRoot = "C:\dev\patchops",

    [string]$PythonExe = "py",

    [switch]$PassThruRawOutput,

    [switch]$VerboseConsole
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Resolve-ReportField {
    param(
        [string]$Text,
        [string]$Name
    )

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $null
    }

    $pattern = '(?m)^\s*' + [regex]::Escape($Name) + '\s*:\s*(.+?)\s*$'
    $match = [regex]::Match($Text, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value.Trim()
    }

    return $null
}

function Invoke-NativeCapture {
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
    $psi.CreateNoWindow = $true

    $escaped = foreach ($argument in $Arguments) {
        if ($argument -match '[\s"]') {
            '"' + ($argument -replace '"', '\"') + '"'
        }
        else {
            $argument
        }
    }
    $psi.Arguments = [string]::Join(' ', $escaped)

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    [pscustomobject]@{
        ExitCode = [int]$process.ExitCode
        StdOut   = $stdout
        StdErr   = $stderr
    }
}

$resolvedWrapperRoot = [System.IO.Path]::GetFullPath($WrapperRepoRoot)
$resolvedPackage = if ([System.IO.Path]::IsPathRooted($PackagePath)) {
    [System.IO.Path]::GetFullPath($PackagePath)
}
else {
    [System.IO.Path]::GetFullPath((Join-Path $PWD $PackagePath))
}

if (-not (Test-Path -LiteralPath $resolvedPackage)) {
    throw ("Package path not found: {0}" -f $resolvedPackage)
}

$arguments = @('-m', 'patchops.cli', 'run-package', $resolvedPackage, '--wrapper-root', $resolvedWrapperRoot)

$result = Invoke-NativeCapture -FilePath $PythonExe -Arguments $arguments -WorkingDirectory $resolvedWrapperRoot

$canonicalReportPath = Resolve-ReportField -Text $result.StdOut -Name 'Canonical Report Path'
if ([string]::IsNullOrWhiteSpace($canonicalReportPath)) {
    $canonicalReportPath = Resolve-ReportField -Text $result.StdOut -Name 'Report Path'
}

$summaryText = $result.StdOut
if (-not [string]::IsNullOrWhiteSpace($canonicalReportPath) -and (Test-Path -LiteralPath $canonicalReportPath)) {
    $summaryText = Get-Content -LiteralPath $canonicalReportPath -Raw -Encoding UTF8
}

$patchName = Resolve-ReportField -Text $summaryText -Name 'Patch Name'
if ([string]::IsNullOrWhiteSpace($patchName)) {
    $patchName = [IO.Path]::GetFileNameWithoutExtension($resolvedPackage)
}

$runResult = Resolve-ReportField -Text $summaryText -Name 'Result'
if ([string]::IsNullOrWhiteSpace($runResult)) {
    $runResult = $(if ($result.ExitCode -eq 0) { 'PASS' } else { 'FAIL' })
}

$exitCodeText = Resolve-ReportField -Text $summaryText -Name 'ExitCode'
if ([string]::IsNullOrWhiteSpace($exitCodeText)) {
    $exitCodeText = [string]$result.ExitCode
}

$failureCategory = Resolve-ReportField -Text $summaryText -Name 'Failure Category'
if ([string]::IsNullOrWhiteSpace($failureCategory)) {
    $failureCategory = '(none)'
}

if ($PassThruRawOutput -or $VerboseConsole) {
    if (-not [string]::IsNullOrWhiteSpace($result.StdOut)) { Write-Host $result.StdOut }
    if (-not [string]::IsNullOrWhiteSpace($result.StdErr)) { Write-Host $result.StdErr }
}

Write-Host 'PATCHOPS QUIET RUN SUMMARY'
Write-Host '-------------------------'
Write-Host ('Patch        : {0}' -f $patchName)
Write-Host ('Result       : {0}' -f $runResult)
Write-Host ('ExitCode     : {0}' -f $exitCodeText)
Write-Host ('Failure      : {0}' -f $failureCategory)
Write-Host ('ReportPath   : {0}' -f $(if ([string]::IsNullOrWhiteSpace($canonicalReportPath)) { '(not found)' } else { $canonicalReportPath }))

exit $result.ExitCode