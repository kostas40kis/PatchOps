& {
    param(
        [string]$WrapperRepoRoot = 'C:\dev\patchops'
    )

    $ErrorActionPreference = 'Stop'
    Set-StrictMode -Version Latest

    $bundleRoot = (Split-Path -Parent $PSScriptRoot)
    $manifestPath = Join-Path $bundleRoot 'manifest.json'

    if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
        throw ("Wrapper repo root not found: {0}" -f $WrapperRepoRoot)
    }

    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw ("Manifest not found: {0}" -f $manifestPath)
    }

    Push-Location -LiteralPath $WrapperRepoRoot
    try {
        & py -m patchops.cli check $manifestPath
        & py -m patchops.cli inspect $manifestPath
        & py -m patchops.cli plan $manifestPath
        & py -m patchops.cli apply $manifestPath
    }
    finally {
        Pop-Location
    }
}
