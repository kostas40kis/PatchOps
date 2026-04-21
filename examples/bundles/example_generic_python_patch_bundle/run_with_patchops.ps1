& {
    param(
        [string]$WrapperRepoRoot = 'C:\dev\patchops'
    )

    $ErrorActionPreference = 'Stop'

    $bundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    $manifestPath = Join-Path $bundleRoot 'manifest.json'

    if (-not (Test-Path -LiteralPath $manifestPath)) {
        throw "Bundle manifest not found: $manifestPath"
    }

    Push-Location $WrapperRepoRoot
    try {
        py -m patchops.cli apply $manifestPath --wrapper-root $WrapperRepoRoot
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}
