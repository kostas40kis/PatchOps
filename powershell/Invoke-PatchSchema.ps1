param()
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

$py = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
if ($null -eq $py) {
    $py = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
}
if ($null -eq $py) {
    throw 'Could not find py or python on PATH.'
}

& $py.Source -m patchops.cli schema
exit $LASTEXITCODE
