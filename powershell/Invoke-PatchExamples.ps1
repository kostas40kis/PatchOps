param(
    [string]$Profile
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

Set-Location $repoRoot

$argsList = @('-m', 'patchops.cli', 'examples')

if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $argsList += @('--profile', $Profile)
}

& py @argsList
exit $LASTEXITCODE
