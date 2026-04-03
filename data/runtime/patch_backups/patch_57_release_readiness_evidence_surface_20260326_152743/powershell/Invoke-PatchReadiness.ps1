[CmdletBinding()]
param(
    [string]$WrapperRoot = "",
    [string]$Profile = "",
    [switch]$CoreTestsGreen,
    [string]$PythonExe = ""
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($WrapperRoot)) {
    $WrapperRoot = Split-Path -Path $PSScriptRoot -Parent
}

$arguments = @('-m', 'patchops.cli')
$arguments += @("release-readiness", "--wrapper-root", $WrapperRoot)

if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $arguments += @("--profile", $Profile)
}

if ($CoreTestsGreen.IsPresent) {
    $arguments += @("--core-tests-green")
}

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $py = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $py) {
        $PythonExe = $py.Source
        $prefixArgs = @('-3')
    }
    else {
        $python = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -eq $python) {
            throw 'Could not find py or python on PATH.'
        }
        $PythonExe = $python.Source
        $prefixArgs = @()
    }
}
else {
    $prefixArgs = @()
}

& $PythonExe @($prefixArgs + $arguments)
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE