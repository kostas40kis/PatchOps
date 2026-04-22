& {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$WrapperRepoRoot = "C:\dev\patchops"
    )

    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    # bundle-entry
    $bundleRoot = $PSScriptRoot

    py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot
    exit $LASTEXITCODE
}