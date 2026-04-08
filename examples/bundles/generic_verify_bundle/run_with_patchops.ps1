param(
    [string]$WrapperRepoRoot = "C:\dev\patchops"
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $PSCommandPath
$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
    throw ("Wrapper repo root not found: {0}" -f $WrapperRepoRoot)
}

if (-not (Test-Path -LiteralPath $bundleMetaPath)) {
    throw ("bundle_meta.json not found: {0}" -f $bundleMetaPath)
}

Set-Location $WrapperRepoRoot
py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot
