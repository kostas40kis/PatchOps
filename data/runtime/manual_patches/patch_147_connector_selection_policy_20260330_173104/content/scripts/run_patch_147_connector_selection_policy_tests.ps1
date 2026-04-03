param(
    [string]$ProjectRoot = 'C:\dev\trader'
)

$ErrorActionPreference = 'Stop'
$python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw ('Expected python not found: {0}' -f $python)
}

& $python -m pytest -q `
    tests/test_connector_selection_policy.py `
    tests/test_multi_chain_provider_health_snapshot.py

exit $LASTEXITCODE