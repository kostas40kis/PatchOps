[CmdletBinding()]
param(
    [string]$Profile = 'trader',
    [string]$TargetRoot
)

$ErrorActionPreference = 'Stop'
$wrapperRoot = Split-Path -Parent $PSScriptRoot

Push-Location $wrapperRoot
try {
    $arguments = @('-m', 'patchops.cli', 'doctor', '--profile', $Profile)
    if (-not [string]::IsNullOrWhiteSpace($TargetRoot)) {
        $arguments += @('--target-root', $TargetRoot)
    }

    & py @arguments
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
