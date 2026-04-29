param(
    [string]$RepoRoot = 'C:\dev\patchops',
    [string]$ReportPath = '',
    [string]$ReportFolder = '',
    [string]$PointerPath = '',
    [switch]$PlanOnly,
    [switch]$SkipCloseoutValidation,
    [switch]$SkipFullPytest,
    [int]$TimeoutShortSeconds = 120,
    [int]$TimeoutCloseoutSeconds = 2700
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

function Resolve-PowerShellCommand {
    $pwsh = Join-Path $env:ProgramFiles 'PowerShell\7\pwsh.exe'
    if (Test-Path -LiteralPath $pwsh) {
        return $pwsh
    }
    return 'powershell.exe'
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [int]$TimeoutSeconds = 120,
        [switch]$DoNotFailOnNonZero
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

    if (-not $DoNotFailOnNonZero) {
        if ($timedOut) {
            [void]$script:Failures.Add(("{0}: timed out after {1}s" -f $Label, $TimeoutSeconds))
        } elseif ([int]$exitCode -ne 0) {
            [void]$script:Failures.Add(("{0}: exit code {1}" -f $Label, $exitCode))
        }
    }

    return $result
}

function Get-ReportPathFromPointer {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return ''
    }
    $pointerText = Get-Content -LiteralPath $Path -Raw
    $match = [regex]::Match($pointerText, 'ReportPath\s*:\s*(.+)')
    if (-not $match.Success) {
        return ''
    }
    return $match.Groups[1].Value.Trim()
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
    $ReportPath = Join-Path $ReportFolder ("patchops_llm_browser_final_operator_commit_checkpoint_{0}.txt" -f $stamp)
}

if ([string]::IsNullOrWhiteSpace($PointerPath)) {
    $PointerPath = Join-Path $desktop 'patchops_latest_llm_browser_final_operator_commit_checkpoint.txt'
}

$python = Resolve-PythonCommand -Root $resolvedRepoRoot
$pythonFile = [string]$python.FilePath
$pythonPrefixArgs = [string[]]$python.PrefixArgs
$psFile = Resolve-PowerShellCommand

$closeoutPointerPath = Join-Path $desktop 'patchops_latest_llm_browser_closeout_checkpoint.txt'
$broadPointerPath = Join-Path $desktop 'patchops_latest_llm_browser_broad_validation_report.txt'
$closeoutReportPath = ''
$broadReportPath = ''

Add-Section 'PATCHOPS LLM-BROWSER FINAL OPERATOR VALIDATION AND COMMIT CHECKPOINT'
Add-Line ("Started      : {0}" -f (Get-Date).ToString('s'))
Add-Line ("RepoRoot     : {0}" -f $resolvedRepoRoot)
Add-Line ("ReportPath   : {0}" -f $ReportPath)
Add-Line ("ReportFolder : {0}" -f $ReportFolder)
Add-Line ("PointerPath  : {0}" -f $PointerPath)
Add-Line ("PlanOnly     : {0}" -f ([bool]$PlanOnly))
Add-Line ("SkipCloseoutValidation : {0}" -f ([bool]$SkipCloseoutValidation))
Add-Line ("SkipFullPytest         : {0}" -f ([bool]$SkipFullPytest))
Add-Line ''
Add-Line 'Safety: this final checkpoint does not run git commit or git push. It only validates evidence and prints manual operator commands.'

Add-Section 'PLAN'
Add-Line '1. Optionally run the closeout validation and push checkpoint script.'
Add-Line '2. Read the closeout pointer and broad-validation pointer.'
Add-Line '3. Parse the latest broad-validation report with --strict.'
Add-Line '4. Run release-gate and checkpoint JSON smokes.'
Add-Line '5. Capture git status.'
Add-Line '6. Print final manual commit and push commands.'
Add-Line ''
Add-Line 'Default pointer locations:'
Add-Line ("- Closeout pointer         : {0}" -f $closeoutPointerPath)
Add-Line ("- Broad validation pointer : {0}" -f $broadPointerPath)
Add-Line ("- Final checkpoint pointer : {0}" -f $PointerPath)

if (-not $PlanOnly) {
    if (-not $SkipCloseoutValidation) {
        $closeoutArgs = @(
            '-NoProfile',
            '-ExecutionPolicy',
            'Bypass',
            '-File',
            (Join-Path $resolvedRepoRoot 'scripts\llm_browser_closeout_validation_push_checkpoint.ps1'),
            '-RepoRoot',
            $resolvedRepoRoot
        )
        if ($SkipFullPytest) {
            $closeoutArgs += '-SkipFullPytest'
        }
        Invoke-NativeCapture -Label 'closeout validation and push checkpoint' -FilePath $psFile -Arguments $closeoutArgs -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutCloseoutSeconds | Out-Null
    } else {
        Add-Section 'COMMAND: closeout validation and push checkpoint'
        Add-Line 'Skipped because -SkipCloseoutValidation was provided.'
    }

    $closeoutReportPath = Get-ReportPathFromPointer -Path $closeoutPointerPath
    if ([string]::IsNullOrWhiteSpace($closeoutReportPath)) {
        [void]$script:Failures.Add("latest closeout checkpoint pointer was missing or did not contain ReportPath: $closeoutPointerPath")
    } elseif (-not (Test-Path -LiteralPath $closeoutReportPath)) {
        [void]$script:Failures.Add("latest closeout checkpoint report path from pointer does not exist: $closeoutReportPath")
    } else {
        Add-Section 'CLOSEOUT REPORT POINTER CHECK'
        Add-Line ("CloseoutReportPath : {0}" -f $closeoutReportPath)
    }

    $broadReportPath = Get-ReportPathFromPointer -Path $broadPointerPath
    if ([string]::IsNullOrWhiteSpace($broadReportPath)) {
        [void]$script:Failures.Add("latest broad-validation report pointer was missing or did not contain ReportPath: $broadPointerPath")
    } elseif (-not (Test-Path -LiteralPath $broadReportPath)) {
        [void]$script:Failures.Add("latest broad-validation report path from pointer does not exist: $broadReportPath")
    } else {
        Invoke-NativeCapture -Label 'parse latest broad validation report' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'broad-report', '--path', $broadReportPath, '--json', '--strict')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null
    }

    Invoke-NativeCapture -Label 'llm-browser release-gate' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'release-gate', '--repo-root', $resolvedRepoRoot, '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    Invoke-NativeCapture -Label 'llm-browser checkpoint' -FilePath $pythonFile -Arguments ($pythonPrefixArgs + @('-m', 'patchops.cli', 'llm-browser', 'checkpoint', '--repo-root', $resolvedRepoRoot, '--json')) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds | Out-Null

    Invoke-NativeCapture -Label 'git status' -FilePath 'git' -Arguments @('status', '--short', '--branch') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutShortSeconds -DoNotFailOnNonZero | Out-Null
}

Add-Section 'FINAL OPERATOR COMMIT AND PUSH COMMANDS'
Add-Line 'Run these only after this final checkpoint report is PASS and you have reviewed the closeout and broad-validation reports.'
Add-Line ''
Add-Line 'cd C:\dev\patchops'
Add-Line 'git status --short --branch'
Add-Line 'git add -A'
Add-Line 'git commit -m "Close out llm-browser dry-mode validation stream"'
Add-Line 'git push origin main'
Add-Line ''
Add-Line 'Helpful report commands:'
Add-Line ('notepad "{0}"' -f $ReportPath)
Add-Line ('notepad "{0}"' -f $PointerPath)
Add-Line ('notepad "{0}"' -f $closeoutPointerPath)
Add-Line ('notepad "{0}"' -f $broadPointerPath)
if (-not [string]::IsNullOrWhiteSpace($closeoutReportPath)) {
    Add-Line ('notepad "{0}"' -f $closeoutReportPath)
}
if (-not [string]::IsNullOrWhiteSpace($broadReportPath)) {
    Add-Line ('notepad "{0}"' -f $broadReportPath)
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
Add-Line ("Commands captured   : {0}" -f $script:CommandResults.Count)
Add-Line ("CloseoutReportPath  : {0}" -f $closeoutReportPath)
Add-Line ("BroadReportPath     : {0}" -f $broadReportPath)
Add-Line ("ReportPath          : {0}" -f $ReportPath)
Add-Line ("ReportFolder        : {0}" -f $ReportFolder)
Add-Line ("PointerPath         : {0}" -f $PointerPath)
Add-Line ''
Add-Line 'Reminder: this final operator checkpoint never commits or pushes automatically.'

$reportText = [string]::Join([Environment]::NewLine, [string[]]$script:Lines.ToArray())
Write-Utf8NoBom -Path $ReportPath -Content $reportText

$summaryResult = if ($PlanOnly -or $script:Failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$pointerLines = @(
    'Latest PatchOps LLM-browser final operator validation and commit checkpoint',
    ('Updated      : {0}' -f (Get-Date).ToString('s')),
    ('Result       : {0}' -f $summaryResult),
    ('ReportPath   : {0}' -f $ReportPath),
    ('ReportFolder : {0}' -f $ReportFolder),
    ('CloseoutReportPath : {0}' -f $closeoutReportPath),
    ('BroadReportPath    : {0}' -f $broadReportPath),
    '',
    'Open final operator checkpoint with:',
    ('notepad "{0}"' -f $ReportPath)
)
Write-Utf8NoBom -Path $PointerPath -Content ([string]::Join([Environment]::NewLine, [string[]]$pointerLines))

Write-Host $ReportPath

if ($PlanOnly -or $script:Failures.Count -eq 0) {
    exit 0
}
exit 1
