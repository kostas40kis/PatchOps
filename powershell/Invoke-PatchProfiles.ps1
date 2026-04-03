param(
    [string]$Name = "",
    [string]$PythonExe = ""
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapperRoot = Split-Path -Parent $scriptRoot

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $pythonArgs = @("-3", "-m", "patchops.cli", "profiles", "--wrapper-root", $wrapperRoot)
    }
    else {
        $PythonExe = "python"
        $pythonArgs = @("-m", "patchops.cli", "profiles", "--wrapper-root", $wrapperRoot)
    }
}
else {
    $pythonArgs = @("-m", "patchops.cli", "profiles", "--wrapper-root", $wrapperRoot)
}

if (-not [string]::IsNullOrWhiteSpace($Name)) {
    $pythonArgs += @("--name", $Name)
}

& $PythonExe @pythonArgs
exit $LASTEXITCODE