[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot = (Split-Path -Path $PSScriptRoot -Parent),

    [string]$RetryReason = 'wrapper/reporting failure after likely content success',

    [switch]$Preview
)

$ErrorActionPreference = 'Stop'

function Resolve-PatchOpsPython {
    param([string]$Root)

    $candidates = @(
        (Join-Path $Root '.venv\Scripts\python.exe'),
        (Join-Path $Root 'venv\Scripts\python.exe')
    )

    if ($env:VIRTUAL_ENV) {
        $candidates += (Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe')
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            return @{ FilePath = $candidate; Prefix = @() }
        }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ FilePath = $py.Source; Prefix = @('-3') }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{ FilePath = $python.Source; Prefix = @() }
    }

    throw 'Could not resolve a Python runtime for PatchOps.'
}

$python = Resolve-PatchOpsPython -Root $WrapperRoot
$arguments = @()
$arguments += $python.Prefix
$arguments += '-m'
$arguments += 'patchops.cli'

if ($Preview) {
    $arguments += 'plan'
    $arguments += $ManifestPath
    $arguments += '--wrapper-root'
    $arguments += $WrapperRoot
    $arguments += '--mode'
    $arguments += 'wrapper_retry'
    if ($RetryReason) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}
else {
    $arguments += 'wrapper-retry'
    $arguments += $ManifestPath
    $arguments += '--wrapper-root'
    $arguments += $WrapperRoot
    if ($RetryReason) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}

& $python.FilePath @arguments
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE