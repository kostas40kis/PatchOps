param(
    [Parameter(Mandatory = $true)]
    [string]$PackagePath,

    [string]$WrapperRepoRoot = "C:\dev\patchops",

    [string]$PythonExe = "py",

    [switch]$PassThruRawOutput
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# compatibility shim only. The canonical operator-facing runner is Invoke-QuietRunPackage.ps1.
$canonicalPath = Join-Path $PSScriptRoot 'Invoke-QuietRunPackage.ps1'
if (-not (Test-Path -LiteralPath $canonicalPath)) {
    throw ("Canonical runner not found: {0}" -f $canonicalPath)
}

& $canonicalPath @PSBoundParameters
exit $LASTEXITCODE
