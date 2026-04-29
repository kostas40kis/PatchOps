param(
    [string]$RepoRoot = 'C:\dev\patchops',
    [string]$ReportPath = '',
    [string]$ReportFolder = '',
    [string]$PointerPath = '',
    [switch]$PlanOnly,
    [switch]$SkipFullPytest,
    [int]$TimeoutShortSeconds = 120,
    [int]$TimeoutMediumSeconds = 300,
    [int]$TimeoutFullPytestSeconds = 1800
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Lines = [System.Collections.Generic.List[string]]::new()
$script:Failures = [System.Collections.Generic.List[string]]::new()
$script:CommandResults = [System.Collections.Generic.List[object]]::new()

function Add-Line {
    param([AllowNull()][object]$Text = '')
    if ($null -eq $Text) {
        $Text = ''
    }
    [void]$script:Lines.Add([string]$Text)
}

function Add-Section {
    param([string]$Title)
    Add-Line ''
    Add-Line ('=' * 120)
    Add-Line $Title
    Add-Line ('=' * 120)
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [AllowNull()][object]$Content = ''
    )
    if ($null -eq $Content) {
        $Content = ''
    }
    $text = [string]$Content
    $directory = Split-Path -Path $Path -Parent
    if (-not [string]::IsNullOrWhiteSpace($directory) -and -not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $text, $utf8NoBom)
}

function Resolve-DesktopPath {
    try {
        $desktop = [Environment]::GetFolderPath('Desktop')
        if (-not [string]::IsNullOrWhiteSpace($desktop)) {
            return $desktop
        }
    } catch {}
    return (Join-Path $env:USERPROFILE 'Desktop')
}

function Join-NativeArguments {
    param([string[]]$Arguments)
    $rendered = New-Object System.Collections.Generic.List[string]
    foreach ($arg in @($Arguments)) {
        if ($null -eq $arg) {
            $arg = ''
        }
        $s = [string]$arg
        if ($s -eq '') {
            [void]$rendered.Add('""')
        } elseif ($s -notmatch '[\s"]') {
            [void]$rendered.Add($s)
        } else {
            [void]$rendered.Add('"' + ($s.Replace('"', '\"')) + '"')
        }
    }
    return ([string]::Join(' ', [string[]]$rendered.ToArray()))
}

function Resolve-PythonCommand {
    param([string]$Root)
    $venv = Join-Path $Root '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venv) {
        return @{
            FilePath = $venv
            PrefixArgs = @()
            Display = $venv
        }
    }
    return @{
        FilePath = 'py'
        PrefixArgs = @('-3')
        Display = 'py -3'
    }
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [int]$TimeoutSeconds = 120
    )

    Add-Section ("COMMAND: {0}" -f $Label)
    Add-Line ("CWD       : {0}" -f $WorkingDirectory)
    Add-Line ("Command   : {0} {1}" -f $FilePath, (Join-NativeArguments -Arguments $Arguments))
    Add-Line ("Timeout   : {0}s" -f $TimeoutSeconds)

    $stdout = ''
    $stderr = ''
    $exitCode = $null
    $timedOut = $false
    $exceptionText = ''

    try {
        $psi = [System.Diagnostics.ProcessStartInfo]::new()
        $psi.FileName = $FilePath
        $psi.Arguments = Join-NativeArguments -Arguments $Arguments
        $psi.WorkingDirectory = $WorkingDirectory
        $psi.UseShellExecute = $false
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.CreateNoWindow = $true

        $process = [System.Diagnostics.Process]::new()
        $process.StartInfo = $psi

        [void]$process.Start()
        $completed = $process.WaitForExit([Math]::Max(1, $TimeoutSeconds) * 1000)

        if (-not $completed) {
            $timedOut = $true
            try { $process.Kill() } catch {}
            try { $process.WaitForExit(5000) | Out-Null } catch {}
        }

        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()

        if (-not $timedOut) {
            $exitCode = $process.ExitCode
        } else {
            $exitCode = 124
        }

        $process.Dispose()
    } catch {
        $exitCode = 125
        $exceptionText = $_.Exception.ToString()
    }

    Add-Line ("TimedOut  : {0}" -f $timedOut)
    Add-Line ("ExitCode  : {0}" -f $exitCode)
    Add-Line '--- STDOUT ---'
    Add-Line $stdout
    Add-Line '--- STDERR ---'
    Add-Line $stderr
    if (-not [string]::IsNullOrWhiteSpace($exceptionText)) {
        Add-Line '--- EXCEPTION ---'
        Add-Line $exceptionText
    }

    $result = [pscustomobject]@{
        Label = $Label
        FilePath = $FilePath
        Arguments = @($Arguments)
        WorkingDirectory = $WorkingDirectory
        TimeoutSeconds = $TimeoutSeconds
        TimedOut = [bool]$timedOut
        ExitCode = [int]$exitCode
        Stdout = $stdout
        Stderr = $stderr
        Exception = $exceptionText
    }
    [void]$script:CommandResults.Add($result)

    if ($timedOut) {
        [void]$script:Failures.Add(("{0}: timed out after {1}s" -f $Label, $TimeoutSeconds))
    } elseif ([int]$exitCode -ne 0) {
        [void]$script:Failures.Add(("{0}: exit code {1}" -f $Label, $exitCode))
    }

    return $result
}

function Add-Plan {
    param(
        [string]$PythonFile,
        [string[]]$PythonPrefixArgs
    )

    Add-Section 'VALIDATION PLAN'
    Add-Line 'This operator script writes one report and captures stdout/stderr for each command.'
    Add-Line 'It is intentionally broad, but every command has a timeout.'
    Add-Line ''
    Add-Line 'Planned commands:'
    Add-Line '1. git status --short --branch'
    Add-Line '2. python -m compileall patchops tests'
    Add-Line '3. python -m patchops.cli llm-browser release-gate --repo-root <RepoRoot> --json'
    Add-Line '4. python -m patchops.cli llm-browser checkpoint --repo-root <RepoRoot> --json'
    Add-Line '5. python -m patchops.cli llm-browser doctor --browser none --json'
    Add-Line '6. python -m patchops.cli llm-browser audit-log --path <temporary missing audit log> --json'
    if (-not $SkipFullPytest) {
        Add-Line '7. python -m pytest -q'
        Add-Line '7 detail: full pytest is enabled by default.'
    } else {
        Add-Line '7. Full pytest skipped because -SkipFullPytest was provided.'
    }
    Add-Line ''
    Add-Line ("Resolved python: {0} {1}" -f $PythonFile, (Join-NativeArguments -Arguments $PythonPrefixArgs))
}

try {
    $resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
} catch {
    throw "RepoRoot does not exist: $RepoRoot"
}

$desktop = Resolve-DesktopPath
if (-not (Test-Path -LiteralPath $desktop)) {
    New-Item -ItemType Directory -Path $desktop -Force | Out-Null
}

if ([string]::IsNullOrWhiteSpace($ReportFolder)) {
    $ReportFolder = Join-Path $desktop 'patchops_reports'
}
if (-not (Test-Path -LiteralPath $ReportFolder)) {
    New-Item -ItemType Directory -Path $ReportFolder -Force | Out-Null
}

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    $stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $ReportPath = Join-Path $ReportFolder ("patchops_llm_browser_broad_validation_{0}.txt" -f $stamp)
}

if ([string]::IsNullOrWhiteSpace($PointerPath)) {
    $PointerPath = Join-Path $desktop 'patchops_latest_llm_browser_broad_validation_report.txt'
}

$python = Resolve-PythonCommand -Root $resolvedRepoRoot
$pythonFile = [string]$python.FilePath
$pythonPrefixArgs = [string[]]$python.PrefixArgs

Add-Section 'PATCHOPS LLM-BROWSER BROAD VALIDATION'
Add-Line ("Started    : {0}" -f (Get-Date).ToString('s'))
Add-Line ("RepoRoot   : {0}" -f $resolvedRepoRoot)
Add-Line ("ReportPath : {0}" -f $ReportPath)
Add-Line ("ReportFolder : {0}" -f $ReportFolder)
Add-Line ("PointerPath  : {0}" -f $PointerPath)
Add-Line ("PlanOnly   : {0}" -f ([bool]$PlanOnly))
Add-Line ("SkipPytest : {0}" -f ([bool]$SkipFullPytest))
Add-Line ''
Add-Line 'Safety: this script does not start a browser, click downloads, paste/send messages, run PatchOps packages, or commit/push git changes.'

Add-Plan -PythonFile $pythonFile -PythonPrefixArgs $pythonPrefixArgs

if (-not $PlanOnly) {
    Invoke-NativeCapture -Label 'git status' -FilePath 'git' -Arguments @('status', '--short', '--branch') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    Invoke-NativeCapture -Label 'compileall patchops tests' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'compileall', 'patchops', 'tests')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutMediumSeconds | Out-Null

    Invoke-NativeCapture -Label 'llm-browser release-gate' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'release-gate', '--repo-root', $resolvedRepoRoot, '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    Invoke-NativeCapture -Label 'llm-browser checkpoint' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'checkpoint', '--repo-root', $resolvedRepoRoot, '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    Invoke-NativeCapture -Label 'llm-browser doctor none' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'doctor', '--browser', 'none', '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    $missingAuditPath = Join-Path $env:TEMP 'patchops_llm_browser_missing_audit_for_readback_smoke.jsonl'
    Remove-Item -LiteralPath $missingAuditPath -Force -ErrorAction SilentlyContinue
    Invoke-NativeCapture -Label 'llm-browser audit-log missing-file readback' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'audit-log', '--path', $missingAuditPath, '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    if (-not $SkipFullPytest) {
        Invoke-NativeCapture -Label 'full pytest' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'pytest', '-q')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutFullPytestSeconds | Out-Null
    }
}

Add-Section 'SUMMARY'
if ($PlanOnly) {
    Add-Line 'Result     : PASS'
    Add-Line 'ExitCode   : 0'
    Add-Line 'Mode       : PLAN_ONLY'
} elseif ($script:Failures.Count -eq 0) {
    Add-Line 'Result     : PASS'
    Add-Line 'ExitCode   : 0'
    Add-Line 'Mode       : EXECUTED'
} else {
    Add-Line 'Result     : FAIL'
    Add-Line 'ExitCode   : 1'
    Add-Line 'Mode       : EXECUTED'
    Add-Line ''
    Add-Line 'Failures:'
    foreach ($failure in $script:Failures) {
        Add-Line ("- {0}" -f $failure)
    }
}
Add-Line ''
Add-Line ("Commands captured : {0}" -f $script:CommandResults.Count)
Add-Line ("ReportPath        : {0}" -f $ReportPath)
Add-Line ("ReportFolder      : {0}" -f $ReportFolder)
Add-Line ("PointerPath       : {0}" -f $PointerPath)
Add-Line ''
Add-Line 'Next operator action: if this report is PASS, commit the dry-mode browser-runner changes and then push when ready.'

$reportText = [string]::Join([Environment]::NewLine, [string[]]$script:Lines.ToArray())
Write-Utf8NoBom -Path $ReportPath -Content $reportText

$summaryResult = if ($PlanOnly -or $script:Failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$pointerLines = @(
    'Latest PatchOps LLM-browser broad validation report',
    ('Updated      : {0}' -f (Get-Date).ToString('s')),
    ('Result       : {0}' -f $summaryResult),
    ('ReportPath   : {0}' -f $ReportPath),
    ('ReportFolder : {0}' -f $ReportFolder),
    '',
    'Open report with:',
    ('notepad "{0}"' -f $ReportPath)
)
Write-Utf8NoBom -Path $PointerPath -Content ([string]::Join([Environment]::NewLine, [string[]]$pointerLines))

Write-Host $ReportPath

if ($PlanOnly -or $script:Failures.Count -eq 0) {
    exit 0
}
exit 1
