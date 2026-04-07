& {
    param(
        [string]$WrapperRepoRoot = 'C:\dev\patchops'
    )

    $ErrorActionPreference = 'Stop'
    Set-StrictMode -Version Latest

    $bundleRoot = $PSScriptRoot

    if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
        throw ("Wrapper repo root not found: {0}" -f $WrapperRepoRoot)
    }

    Push-Location -LiteralPath $WrapperRepoRoot
    try {
        & py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot
    }
    finally {
        Pop-Location
    }
}
