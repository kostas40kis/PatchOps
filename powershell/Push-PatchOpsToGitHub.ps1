param(
    [string]$RepoPath = 'C:\dev\patchops',
    [string]$RepoUrl = 'https://github.com/kostas40kis/PatchOps.git',
    [string]$Branch = 'main',
    [string]$CommitMessage = ''
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
            '"' + (($arg -replace '(\\*)"', '$1$1\"') -replace '(\\+)$', '$1$1') + '"'
        }
    }

    $escaped -join ' '
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Args,
        [switch]$AllowFailure
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = 'git'
    $psi.WorkingDirectory = (Get-Location).Path
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $psi.Arguments = Convert-ToWindowsArgumentString -Args $Args

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    $result = [pscustomobject]@{
        ExitCode = $process.ExitCode
        StdOut   = $stdout.Trim()
        StdErr   = $stderr.Trim()
    }

    if (-not $AllowFailure -and $result.ExitCode -ne 0) {
        $details = @()
        if (-not [string]::IsNullOrWhiteSpace($result.StdOut)) { $details += $result.StdOut }
        if (-not [string]::IsNullOrWhiteSpace($result.StdErr)) { $details += $result.StdErr }
        $cmdText = 'git ' + ($Args -join ' ')
        if ($details.Count -eq 0) { throw $cmdText }
        throw ($cmdText + [Environment]::NewLine + ($details -join [Environment]::NewLine))
    }

    $result
}

function Add-GitignoreLines {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string[]]$Lines
    )

    $existing = @()
    if (Test-Path -LiteralPath $Path) {
        $existing = Get-Content -LiteralPath $Path
    }

    $toAppend = New-Object System.Collections.Generic.List[string]
    foreach ($line in $Lines) {
        if ($existing -notcontains $line) {
            [void]$toAppend.Add($line)
        }
    }

    if ($toAppend.Count -gt 0) {
        Add-Content -LiteralPath $Path -Value @('', '# Local/generated exclusions for GitHub upload', $toAppend.ToArray())
    }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available on PATH."
}

if (-not (Test-Path -LiteralPath $RepoPath)) {
    throw "Repo path does not exist: $RepoPath"
}

$resolvedRepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$gitDir = Join-Path $resolvedRepoPath '.git'
$indexLockPath = Join-Path $gitDir 'index.lock'

if (-not (Test-Path -LiteralPath $gitDir)) {
    throw "Missing .git folder. This does not look like an initialized Git repo: $resolvedRepoPath"
}

if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    $CommitMessage = 'Update PatchOps repo ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
}

$sourceItems = @(
    '.gitignore',
    'README.md',
    'pyproject.toml',
    'docs',
    'examples',
    'handoff',
    'llm',
    'onboarding',
    'patchops',
    'powershell',
    'tests'
)

Write-Host "Repo path: $resolvedRepoPath"
Write-Host "Remote   : $RepoUrl"
Write-Host "Branch   : $Branch"
Write-Host ''

$runningGit = @(Get-Process -Name git -ErrorAction SilentlyContinue)
if ((Test-Path -LiteralPath $indexLockPath) -and $runningGit.Count -gt 0) {
    throw "A git.exe process is running. Close any Git process that is using this repo, then run the script again."
}

if (Test-Path -LiteralPath $indexLockPath) {
    Write-Host 'Removing stale .git\index.lock...'
    Remove-Item -LiteralPath $indexLockPath -Force
}

Push-Location $resolvedRepoPath
try {
    Write-Host '[1/8] Checking Git...'
    Invoke-Git -Args @('--version') | Out-Null

    Write-Host '[2/8] Checking Git identity...'
    $userName = Invoke-Git -Args @('config', 'user.name') -AllowFailure
    $userEmail = Invoke-Git -Args @('config', 'user.email') -AllowFailure
    if ([string]::IsNullOrWhiteSpace($userName.StdOut) -or [string]::IsNullOrWhiteSpace($userEmail.StdOut)) {
        throw @"
Git user.name and/or user.email are not configured.

Run these first:

git config --global user.name "Your Name"
git config --global user.email "you@example.com"
"@
    }

    Write-Host '[3/8] Updating .gitignore exclusions...'
    $gitignorePath = Join-Path $resolvedRepoPath '.gitignore'
    Add-GitignoreLines -Path $gitignorePath -Lines @(
        '.pytest_cache/'
        '__pycache__/'
        '*.pyc'
        '*.pyo'
        '.venv/'
        'venv/'
        'env/'
        '.mypy_cache/'
        '.ruff_cache/'
        '.coverage'
        'htmlcov/'
        'dist/'
        'build/'
        '*.egg-info/'
        'data/runtime/'
    )

    Write-Host '[4/8] Ensuring remote origin...'
    $currentOrigin = Invoke-Git -Args @('remote', 'get-url', 'origin') -AllowFailure
    if ($currentOrigin.ExitCode -eq 0) {
        if ($currentOrigin.StdOut -ne $RepoUrl) {
            Write-Host "Updating origin from $($currentOrigin.StdOut) to $RepoUrl"
            Invoke-Git -Args @('remote', 'set-url', 'origin', $RepoUrl) | Out-Null
        }
    }
    else {
        Write-Host 'Adding origin...'
        Invoke-Git -Args @('remote', 'add', 'origin', $RepoUrl) | Out-Null
    }

    Write-Host '[5/8] Staging project files...'
    foreach ($item in $sourceItems) {
        $fullPath = Join-Path $resolvedRepoPath $item
        if (Test-Path -LiteralPath $fullPath) {
            Write-Host ("  adding {0}" -f $item)
            Invoke-Git -Args @('add', '--', $item) | Out-Null
        }
    }

    $extraRootFiles = Get-ChildItem -LiteralPath $resolvedRepoPath -File |
        Where-Object {
            $_.Name -notin $sourceItems -and
            $_.Name -match '\.(md|txt|json|ps1|yml|yaml)$'
        }

    foreach ($file in $extraRootFiles) {
        Write-Host ("  adding extra root file {0}" -f $file.Name)
        Invoke-Git -Args @('add', '--', $file.Name) | Out-Null
    }

    Write-Host '[6/8] Reviewing staged changes...'
    $status = Invoke-Git -Args @('status', '--short')
    if ([string]::IsNullOrWhiteSpace($status.StdOut)) {
        Write-Host 'No changes to commit.'
        return
    }
    Write-Host $status.StdOut

    Write-Host '[7/8] Creating commit...'
    Invoke-Git -Args @('commit', '-m', $CommitMessage) | Out-Null

    Write-Host '[8/8] Pushing to GitHub...'
    Invoke-Git -Args @('branch', '-M', $Branch) | Out-Null
    Invoke-Git -Args @('push', '-u', 'origin', $Branch) | Out-Null

    Write-Host ''
    Write-Host 'Done.'
    Write-Host "Pushed latest PatchOps changes to $RepoUrl"
}
finally {
    Pop-Location
}
