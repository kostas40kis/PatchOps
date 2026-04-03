[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot = '',

    [switch]$Preview
)

$ErrorActionPreference = 'Stop'

function Resolve-PatchOpsPython {
    param([string]$ResolvedWrapperRoot)

    $venvPython = Join-Path $ResolvedWrapperRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
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

$pythonExe = Resolve-PatchOpsPython -ResolvedWrapperRoot $resolvedWrapperRoot

$arguments = @('-m', 'patchops.cli')
if ($Preview) {
    $arguments += 'plan'
    $arguments += $resolvedManifestPath
    $arguments += '--mode'
    $arguments += 'verify'
}
else {
    $arguments += 'verify'
    $arguments += $resolvedManifestPath
}
$arguments += '--wrapper-root'
$arguments += $resolvedWrapperRoot

$exitCode = 0
Push-Location -LiteralPath $resolvedWrapperRoot
try {
    & $pythonExe @arguments
    if ($null -ne $LASTEXITCODE) {
        $exitCode = [int]$LASTEXITCODE
    }
}
finally {
    Pop-Location
}

exit $exitCode
