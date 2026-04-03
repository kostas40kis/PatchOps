param(
    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,
    [string]$PythonExe = ""
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapperRoot = Split-Path -Parent $scriptRoot

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $pythonArgs = @("-3", "-m", "patchops.cli", "check", $ManifestPath)
    }
    else {
        $PythonExe = "python"
        $pythonArgs = @("-m", "patchops.cli", "check", $ManifestPath)
    }
}
else {
    $pythonArgs = @("-m", "patchops.cli", "check", $ManifestPath)
}

& $PythonExe @pythonArgs
exit $LASTEXITCODE