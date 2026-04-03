[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,

    [string]$WrapperRoot = '',

    [string]$RetryReason = 'wrapper/reporting failure after likely content success',

    [switch]$Preview
)

$ErrorActionPreference = 'Stop'

function Resolve-PatchOpsPythonCommand {
    param([string]$ResolvedWrapperRoot)

    $repoVenv = Join-Path $ResolvedWrapperRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $repoVenv) {
        return [pscustomobject]@{
            FilePath   = (Resolve-Path -LiteralPath $repoVenv).Path
            PrefixArgs = @()
        }
    }

    $repoAltVenv = Join-Path $ResolvedWrapperRoot 'venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $repoAltVenv) {
        return [pscustomobject]@{
            FilePath   = (Resolve-Path -LiteralPath $repoAltVenv).Path
            PrefixArgs = @()
        }
    }

    if ($env:VIRTUAL_ENV) {
        $activeVenv = Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'
        if (Test-Path -LiteralPath $activeVenv) {
            return [pscustomobject]@{
                FilePath   = (Resolve-Path -LiteralPath $activeVenv).Path
                PrefixArgs = @()
            }
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        return [pscustomobject]@{
            FilePath   = $pyCommand.Source
            PrefixArgs = @('-3')
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return [pscustomobject]@{
            FilePath   = $pythonCommand.Source
            PrefixArgs = @()
        }
    }

    throw 'Could not resolve a Python command for PatchOps.'
}

if (-not $WrapperRoot) {
    $WrapperRoot = Split-Path -Path $PSScriptRoot -Parent
}

$resolvedWrapperRoot = (Resolve-Path -LiteralPath $WrapperRoot).Path
$resolvedManifestPath = (Resolve-Path -LiteralPath $ManifestPath).Path

$pythonCommand = Resolve-PatchOpsPythonCommand -ResolvedWrapperRoot $resolvedWrapperRoot

$arguments = @('-m', 'patchops.cli')

if ($Preview) {
    $arguments += @(
        'plan',
        $resolvedManifestPath,
        '--mode',
        'wrapper_retry',
        '--wrapper-root',
        $resolvedWrapperRoot,
        '--retry-reason',
        $RetryReason
    )
}
else {
    $arguments += @(
        'wrapper-retry',
        $resolvedManifestPath,
        '--wrapper-root',
        $resolvedWrapperRoot,
        '--retry-reason',
        $RetryReason
    )
}

$finalArguments = @()
if ($pythonCommand.PrefixArgs) {
    $finalArguments += $pythonCommand.PrefixArgs
}
$finalArguments += $arguments

& $pythonCommand.FilePath @finalArguments
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE