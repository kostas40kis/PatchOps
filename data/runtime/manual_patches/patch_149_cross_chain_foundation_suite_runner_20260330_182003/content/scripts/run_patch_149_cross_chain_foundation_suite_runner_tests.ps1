param(
    [string]$ProjectRoot = 'C:\dev\trader'
)

$ErrorActionPreference = 'Stop'
$python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw ('Expected python not found: {0}' -f $python)
}

& $python -m pytest -q `
    tests/test_cross_chain_foundation_suite_runner.py `
    tests/test_chain_execution_context.py `
    tests/test_connector_capability_profile.py `
    tests/test_order_style_capability_matrix.py `
    tests/test_chain_reserve_policy_registry.py `
    tests/test_chain_aware_route_score_inputs.py `
    tests/test_chain_aware_mode_policy.py `
    tests/test_multi_chain_provider_health_snapshot.py `
    tests/test_connector_selection_policy.py `
    tests/test_chain_support_validation.py

exit $LASTEXITCODE