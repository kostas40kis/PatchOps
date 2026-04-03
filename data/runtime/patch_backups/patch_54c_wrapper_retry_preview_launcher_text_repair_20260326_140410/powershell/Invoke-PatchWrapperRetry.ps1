[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot = '',

    [string]$RetryReason = '',

    [switch]$Preview
)

$ErrorActionPreference = 'Stop'

function Resolve-PatchOpsPython {
    param([string]$ResolvedWrapperRoot)

    $venvPython = Join-Path $ResolvedWrapperRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) {
        return [pscustomobject]@{
            FilePath = $venvPython
            Prefix   = @()
        }
    }

    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCommand -and $pyCommand.Source) {
        return [pscustomobject]@{
            FilePath = $pyCommand.Source
            Prefix   = @('-3')
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $pythonCommand -and $pythonCommand.Source) {
        return [pscustomobject]@{
            FilePath = $pythonCommand.Source
            Prefix   = @()
        }
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
    $commandName = "plan"
    $arguments += @($commandName, $resolvedManifestPath, '--wrapper-root', $resolvedWrapperRoot, '--mode', 'wrapper_retry')
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += @('--retry-reason', $RetryReason)
    }
}
else {
    $commandName = "wrapper-retry"
    $arguments += @($commandName, $resolvedManifestPath, '--wrapper-root', $resolvedWrapperRoot)
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += @('--reason', $RetryReason)
    }
}

$finalArguments = @()
$finalArguments += $python.Prefix
$finalArguments += $arguments

& $python.FilePath @finalArguments
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE