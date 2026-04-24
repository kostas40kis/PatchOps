& {
    param(
        [string]$WrapperRepoRoot = "C:\dev\patchops"
    )

    $ErrorActionPreference = "Stop"
    Set-StrictMode -Version Latest
    $bundleRoot = $PSScriptRoot
    $manifestPath = Join-Path $bundleRoot "manifest.json"

    Push-Location -LiteralPath $WrapperRepoRoot
    try {
        # compatibility contract marker:
        # py -m patchops.cli apply $manifestPath
        & py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}
