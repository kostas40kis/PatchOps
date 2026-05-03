param(
    [string]$RepoRoot = 'C:\dev\patchops',
    [string]$Remote = 'origin',
    [string]$Branch = 'main',
    [string]$ReportPath = '',
    [string]$ReportFolder = '',
    [string]$PointerPath = '',
    [switch]$PlanOnly,
    [int]$TimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:Lines = [System.Collections.Generic.List[string]]::new()
$script:Failures = [System.Collections.Generic.List[string]]::new()
$script:CommandResults = [System.Collections.Generic.List[object]]::new()

function Add-Line {
    param([AllowNull()][object]$Text = '')
    if ($null -eq $Text) { $Text = '' }
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
    if ($null -eq $Content) { $Content = '' }
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
        if (-not [string]::IsNullOrWhiteSpace($desktop)) { return $desktop }
    } catch {}
    return (Join-Path $env:USERPROFILE 'Desktop')
}

function Join-NativeArguments {
    param([string[]]$Arguments)
    $rendered = New-Object System.Collections.Generic.List[string]
    foreach ($arg in @($Arguments)) {
        if ($null -eq $arg) { $arg = '' }
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

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [int]$TimeoutSeconds = 180,
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

        if (-not $timedOut) { $exitCode = $process.ExitCode } else { $exitCode = 124 }
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

function Get-FirstNonEmptyLine {
    param([AllowNull()][string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return '' }
    foreach ($line in ($Text -split "`r?`n")) {
        if (-not [string]::IsNullOrWhiteSpace($line)) { return $line.Trim() }
    }
    return ''
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
    $ReportPath = Join-Path $ReportFolder ("patchops_post_d0_43_push_verification_{0}.txt" -f $stamp)
}

if ([string]::IsNullOrWhiteSpace($PointerPath)) {
    $PointerPath = Join-Path $desktop 'patchops_latest_post_d0_43_push_verification.txt'
}

Add-Section 'PATCHOPS POST-D0.43 PUSH VERIFICATION'
Add-Line ("Started      : {0}" -f (Get-Date).ToString('s'))
Add-Line ("RepoRoot     : {0}" -f $resolvedRepoRoot)
Add-Line ("Remote       : {0}" -f $Remote)
Add-Line ("Branch       : {0}" -f $Branch)
Add-Line ("ReportPath   : {0}" -f $ReportPath)
Add-Line ("ReportFolder : {0}" -f $ReportFolder)
Add-Line ("PointerPath  : {0}" -f $PointerPath)
Add-Line ("PlanOnly     : {0}" -f ([bool]$PlanOnly))
Add-Line ''
Add-Line 'Purpose: verify that the D0.43 evidence patch has been manually committed and pushed.'
Add-Line 'Safety: this helper does not run git add, git commit, or git push.'

Add-Section 'PRECONDITION'
Add-Line 'Before running without -PlanOnly, the operator should manually run:'
Add-Line ''
Add-Line 'cd C:\dev\patchops'
Add-Line 'git status --short --branch'
Add-Line 'git add -A'
Add-Line 'git commit -m "D0.43 record final validation and GitHub upload evidence"'
Add-Line 'git push origin main'
Add-Line ''

$headHash = ''
$remoteHash = ''
$statusText = ''
$logLine = ''

if ($PlanOnly) {
    Add-Section 'PLAN'
    Add-Line 'Plan-only mode did not inspect git state.'
    Add-Line 'Run again without -PlanOnly after D0.43 is manually committed and pushed.'
} else {
    $statusBefore = Invoke-NativeCapture -Label 'git status before fetch' -FilePath 'git' -Arguments @('status', '--short', '--branch') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds -DoNotFailOnNonZero
    $statusText = $statusBefore.Stdout

    Invoke-NativeCapture -Label 'git fetch remote branch' -FilePath 'git' -Arguments @('fetch', $Remote, $Branch) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds | Out-Null

    $log = Invoke-NativeCapture -Label 'git log latest commit' -FilePath 'git' -Arguments @('log', '-1', '--oneline') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds
    $logLine = Get-FirstNonEmptyLine -Text $log.Stdout

    $head = Invoke-NativeCapture -Label 'git rev-parse HEAD' -FilePath 'git' -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds
    $headHash = Get-FirstNonEmptyLine -Text $head.Stdout

    $remoteRef = ('{0}/{1}' -f $Remote, $Branch)
    $remoteHead = Invoke-NativeCapture -Label ('git rev-parse {0}' -f $remoteRef) -FilePath 'git' -Arguments @('rev-parse', $remoteRef) -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds
    $remoteHash = Get-FirstNonEmptyLine -Text $remoteHead.Stdout

    $statusAfter = Invoke-NativeCapture -Label 'git status after fetch' -FilePath 'git' -Arguments @('status', '--short', '--branch') -WorkingDirectory $resolvedRepoRoot -TimeoutSeconds $TimeoutSeconds -DoNotFailOnNonZero
    $statusAfterText = $statusAfter.Stdout

    Add-Section 'POST-D0.43 PUSH INTERPRETATION'
    Add-Line ("LatestCommit : {0}" -f $logLine)
    Add-Line ("HeadHash     : {0}" -f $headHash)
    Add-Line ("RemoteHash   : {0}" -f $remoteHash)
    Add-Line ''

    if ([string]::IsNullOrWhiteSpace($headHash)) {
        [void]$script:Failures.Add('HEAD hash was empty.')
    }
    if ([string]::IsNullOrWhiteSpace($remoteHash)) {
        [void]$script:Failures.Add('Remote hash was empty.')
    }
    if (-not [string]::IsNullOrWhiteSpace($headHash) -and -not [string]::IsNullOrWhiteSpace($remoteHash) -and $headHash -ne $remoteHash) {
        [void]$script:Failures.Add("HEAD does not match ${Remote}/${Branch}.")
    }
    if ($statusAfterText -notmatch [regex]::Escape("## $Branch...$Remote/$Branch")) {
        [void]$script:Failures.Add("git status did not show expected branch relation: ## $Branch...$Remote/$Branch")
    }
    if ($statusAfterText -match '(?m)^\s*(M|A|D|R|C|UU|\?\?)\s+') {
        [void]$script:Failures.Add('Working tree still has modified, staged, conflicted, or untracked files.')
    }
    if ($logLine -notmatch 'D0\.43 record final validation and GitHub upload evidence') {
        [void]$script:Failures.Add('Latest commit message does not appear to be the expected D0.43 evidence commit.')
    }

    if ($script:Failures.Count -eq 0) {
        Add-Line 'Interpretation : PASS - D0.43 appears committed and pushed.'
    } else {
        Add-Line 'Interpretation : FAIL - D0.43 post-push verification did not pass.'
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
Add-Line ("LatestCommit      : {0}" -f $logLine)
Add-Line ("HeadHash          : {0}" -f $headHash)
Add-Line ("RemoteHash        : {0}" -f $remoteHash)
Add-Line ("ReportPath        : {0}" -f $ReportPath)
Add-Line ("ReportFolder      : {0}" -f $ReportFolder)
Add-Line ("PointerPath       : {0}" -f $PointerPath)
Add-Line ''
Add-Line 'Reminder: this helper never commits or pushes automatically.'

$reportText = [string]::Join([Environment]::NewLine, [string[]]$script:Lines.ToArray())
Write-Utf8NoBom -Path $ReportPath -Content $reportText

$summaryResult = if ($PlanOnly -or $script:Failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$pointerLines = @(
    'Latest PatchOps post-D0.43 push verification report',
    ('Updated      : {0}' -f (Get-Date).ToString('s')),
    ('Result       : {0}' -f $summaryResult),
    ('ReportPath   : {0}' -f $ReportPath),
    ('ReportFolder : {0}' -f $ReportFolder),
    ('LatestCommit : {0}' -f $logLine),
    ('HeadHash     : {0}' -f $headHash),
    ('RemoteHash   : {0}' -f $remoteHash),
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
