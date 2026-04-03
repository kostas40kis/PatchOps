[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot = '',

    [string]$RetryReason = '',

    [switch]$Preview
)

# Example preview usage:
# .\Invoke-PatchWrapperRetry.ps1 -ManifestPath .\examples\trader_first_verify_patch.json -Preview

function Resolve-PatchOpsPython {
    param([string]$ResolvedWrapperRoot)

    $venvPython = Join-Path $ResolvedWrapperRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) {
        return @{ FilePath = $venvPython; PrefixArgs = @() }
    }

    $altVenvPython = Join-Path $ResolvedWrapperRoot 'venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $altVenvPython) {
        return @{ FilePath = $altVenvPython; PrefixArgs = @() }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCommand -and $pyCommand.Source) {
        return @{ FilePath = $pyCommand.Source; PrefixArgs = @('-3') }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $pythonCommand -and $pythonCommand.Source) {
        return @{ FilePath = $pythonCommand.Source; PrefixArgs = @() }
    }

    throw 'Could not resolve a Python runtime for PatchOps.'
}

if ([string]::IsNullOrWhiteSpace($WrapperRoot)) {
    $resolvedWrapperRoot = Split-Path -Path $PSScriptRoot -Parent
}
else {
    $resolvedWrapperRoot = $WrapperRoot
}

$resolvedWrapperRoot = [System.IO.Path]::GetFullPath($resolvedWrapperRoot)
$resolvedManifestPath = if ([System.IO.Path]::IsPathRooted($ManifestPath)) {
    $ManifestPath
}
else {
    Join-Path $resolvedWrapperRoot $ManifestPath
}
$resolvedManifestPath = [System.IO.Path]::GetFullPath($resolvedManifestPath)

if (-not (Test-Path -LiteralPath $resolvedManifestPath)) {
    throw ("Manifest file not found: {0}" -f $resolvedManifestPath)
}

$python = Resolve-PatchOpsPython -ResolvedWrapperRoot $resolvedWrapperRoot
$arguments = @('-m', 'patchops.cli')
if ($Preview) {
    $arguments += 'plan'
    $arguments += $resolvedManifestPath
    $arguments += '--mode'
    $arguments += 'wrapper_retry'
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}
else {
    $arguments += 'wrapper-retry'
    $arguments += $resolvedManifestPath
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}
$arguments += '--wrapper-root'
$arguments += $resolvedWrapperRoot
$arguments = @($python.PrefixArgs + $arguments)

$exitCode = 0
Push-Location -LiteralPath $resolvedWrapperRoot
try {
    & $python.FilePath @arguments
    if ($null -ne $LASTEXITCODE) {
        $exitCode = [int]$LASTEXITCODE
    }
}
finally {
    Pop-Location
}

exit $exitCode