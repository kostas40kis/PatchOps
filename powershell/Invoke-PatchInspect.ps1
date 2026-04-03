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
        $pythonArgs = @("-3", "-m", "patchops.cli", "inspect", $ManifestPath)
    }
    else {
        $PythonExe = "python"
        $pythonArgs = @("-m", "patchops.cli", "inspect", $ManifestPath)
    }
}
else {
    $pythonArgs = @("-m", "patchops.cli", "inspect", $ManifestPath)
}

& $PythonExe @pythonArgs
exit $LASTEXITCODE