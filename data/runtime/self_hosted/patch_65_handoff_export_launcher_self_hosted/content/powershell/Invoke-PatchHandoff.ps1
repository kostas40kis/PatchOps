[CmdletBinding()]
param(
    [string]$ProjectRoot = 'C:\dev\patchops',
    [string]$PythonExe = '',
    [string]$SourceReportPath = '',
    [string]$CurrentStage = 'Stage 2 in progress',
    [string]$BundleName = 'current'
)

$ErrorActionPreference = 'Stop'

function New-Utf8NoBomWriter {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $parent = Split-Path -Parent $Path
    if (-not [string]::IsNullOrWhiteSpace($parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    return New-Object System.IO.StreamWriter($Path, $false, $utf8NoBom)
}

function Quote-ProcessArgument {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Value
    )

    if ($Value.Length -eq 0) {
        return '""'
    }

    if ($Value -notmatch '[\s"]') {
        return $Value
    }

    $escaped = $Value -replace '(\\*)"', '$1$1\"'
    $escaped = $escaped -replace '(\\+)$', '$1$1'
    return '"' + $escaped + '"'
}

function Join-ProcessArguments {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList
    )

    $quoted = foreach ($arg in $ArgumentList) {
        Quote-ProcessArgument -Value $arg
    }

    return [string]::Join(' ', $quoted)
}

function Resolve-PatchOpsPython {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($PythonExe) -and (Test-Path -LiteralPath $PythonExe)) {
        return $PythonExe
    }

    $venvCandidates = @(
        (Join-Path $RepoRoot '.venv\Scripts\python.exe'),
        (Join-Path $RepoRoot 'venv\Scripts\python.exe')
    )

    foreach ($candidate in $venvCandidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCommand -and $pyCommand.Source) {
        return $pyCommand.Source
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $pythonCommand -and $pythonCommand.Source) {
        return $pythonCommand.Source
    }

    throw 'Could not resolve a Python runtime for PatchOps.'
}

function Invoke-ProcessCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.Arguments = Join-ProcessArguments -ArgumentList $ArgumentList
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi

    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    return [pscustomobject]@{
        FilePath         = $FilePath
        Arguments        = $ArgumentList
        ArgumentsDisplay = $psi.Arguments
        WorkingDirectory = $WorkingDirectory
        ExitCode         = $process.ExitCode
        StdOut           = $stdout
        StdErr           = $stderr
    }
}

$desktop = [Environment]::GetFolderPath('Desktop')
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$launcherReportPath = Join-Path $desktop ('patch_handoff_export_' + $timestamp + '.txt')

$pythonPath = Resolve-PatchOpsPython -RepoRoot $ProjectRoot
$argumentList = @(
    '-m',
    'patchops.cli',
    'export-handoff',
    '--wrapper-root',
    $ProjectRoot,
    '--current-stage',
    $CurrentStage,
    '--bundle-name',
    $BundleName
)

if (-not [string]::IsNullOrWhiteSpace($SourceReportPath)) {
    $argumentList += @('--report-path', $SourceReportPath)
}

$run = Invoke-ProcessCapture -FilePath $pythonPath -ArgumentList $argumentList -WorkingDirectory $ProjectRoot

$payload = $null
$payloadParseError = $null

if ($run.ExitCode -eq 0) {
    try {
        $payload = $run.StdOut | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        $payloadParseError = $_.Exception.Message
        $run = [pscustomobject]@{
            FilePath         = $run.FilePath
            Arguments        = $run.Arguments
            ArgumentsDisplay = $run.ArgumentsDisplay
            WorkingDirectory = $run.WorkingDirectory
            ExitCode         = 1
            StdOut           = $run.StdOut
            StdErr           = (($run.StdErr.TrimEnd() + [Environment]::NewLine + 'Failed to parse export-handoff JSON output: ' + $payloadParseError).Trim())
        }
    }
}

$resultLabel = if ($run.ExitCode -eq 0) { 'PASS' } else { 'FAIL' }

$writer = New-Utf8NoBomWriter -Path $launcherReportPath
try {
    $writer.WriteLine('PATCHOPS HANDOFF EXPORT')
    $writer.WriteLine('=======================')
    $writer.WriteLine('')
    $writer.WriteLine(('Timestamp           : {0}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')))
    $writer.WriteLine(('Wrapper Project Root: {0}' -f $ProjectRoot))
    $writer.WriteLine(('Runtime             : {0}' -f $pythonPath))
    if ([string]::IsNullOrWhiteSpace($SourceReportPath)) {
        $writer.WriteLine('Source Report Path  : (use export-handoff fallback logic)')
    }
    else {
        $writer.WriteLine(('Source Report Path  : {0}' -f $SourceReportPath))
    }
    $writer.WriteLine(('Current Stage       : {0}' -f $CurrentStage))
    $writer.WriteLine(('Bundle Name         : {0}' -f $BundleName))
    $writer.WriteLine(('Launcher Report Path: {0}' -f $launcherReportPath))
    $writer.WriteLine('')

    $writer.WriteLine('HANDOFF EXPORT COMMAND')
    $writer.WriteLine('----------------------')
    $writer.WriteLine(($run.FilePath + ' ' + $run.ArgumentsDisplay))
    $writer.WriteLine(('WorkingDirectory : {0}' -f $run.WorkingDirectory))
    $writer.WriteLine('')

    $writer.WriteLine('[stdout]')
    if ([string]::IsNullOrEmpty($run.StdOut)) {
        $writer.WriteLine('(empty)')
    }
    else {
        $writer.Write($run.StdOut)
        if (-not $run.StdOut.EndsWith("`n")) {
            $writer.WriteLine('')
        }
    }

    $writer.WriteLine('')
    $writer.WriteLine('[stderr]')
    if ([string]::IsNullOrEmpty($run.StdErr)) {
        $writer.WriteLine('(empty)')
    }
    else {
        $writer.Write($run.StdErr)
        if (-not $run.StdErr.EndsWith("`n")) {
            $writer.WriteLine('')
        }
    }

    $writer.WriteLine('')

    $writer.WriteLine('HANDOFF EXPORT RESULT')
    $writer.WriteLine('---------------------')
    if ($null -eq $payload) {
        $writer.WriteLine('(none)')
    }
    else {
        $writer.WriteLine(('Current Status       : {0}' -f $payload.current_status))
        $writer.WriteLine(('Failure Class        : {0}' -f $payload.failure_class))
        $writer.WriteLine(('Latest Attempted Patch: {0}' -f $payload.latest_attempted_patch))
        $writer.WriteLine(('Latest Passed Patch  : {0}' -f $payload.latest_passed_patch))
        $writer.WriteLine(('Next Recommended Mode: {0}' -f $payload.next_recommended_mode))
        $writer.WriteLine(('Next Action          : {0}' -f $payload.next_action))
        $writer.WriteLine(('Report Path          : {0}' -f $payload.report_path))
        $writer.WriteLine(('Handoff Root         : {0}' -f $payload.handoff_root))
        $writer.WriteLine(('Bundle Root          : {0}' -f $payload.bundle_root))
        $writer.WriteLine('')

        $writer.WriteLine('WRITTEN FILES')
        $writer.WriteLine('-------------')
        foreach ($item in $payload.written_files) {
            $writer.WriteLine(('WROTE : {0}' -f $item))
        }
        $writer.WriteLine('')

        $writer.WriteLine('BUNDLE FILES')
        $writer.WriteLine('------------')
        foreach ($item in $payload.bundle_files) {
            $writer.WriteLine(('BUNDLED : {0}' -f $item))
        }
    }

    $writer.WriteLine('')
    $writer.WriteLine('SUMMARY')
    $writer.WriteLine('-------')
    $writer.WriteLine(('ExitCode : {0}' -f $run.ExitCode))
    $writer.WriteLine(('Result   : {0}' -f $resultLabel))
}
finally {
    $writer.Dispose()
}

Invoke-Item -LiteralPath $launcherReportPath

if ($run.ExitCode -ne 0) {
    throw ('Invoke-PatchHandoff failed. See report: {0}' -f $launcherReportPath)
}