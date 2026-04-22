& {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$WrapperRepoRoot = "C:\dev\patchops"
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $bundleRoot = (Split-Path -Parent $PSScriptRoot)
    $manifestPath = Join-Path $bundleRoot 'manifest.json'

    Push-Location -LiteralPath $WrapperRepoRoot
    try {
        py -m patchops.cli apply $manifestPath --wrapper-root $WrapperRepoRoot
        exit $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}