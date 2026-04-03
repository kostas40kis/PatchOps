param(
    [Parameter(Mandatory = $true)][string]$Profile,
    [ValidateSet("apply", "verify")][string]$Mode = "apply",
    [string]$PatchName = "template_patch",
    [string]$TargetRoot = "",
    [string]$OutputPath = "",
    [string]$PythonExe = ""
)

$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapperRoot = Split-Path -Parent $scriptRoot

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonExe = "py"
        $pythonArgs = @("-3", "-m", "patchops.cli", "template", "--wrapper-root", $wrapperRoot)
    }
    else {
        $PythonExe = "python"
        $pythonArgs = @("-m", "patchops.cli", "template", "--wrapper-root", $wrapperRoot)
    }
}
else {
    $pythonArgs = @("-m", "patchops.cli", "template", "--wrapper-root", $wrapperRoot)
}

$pythonArgs += @("--profile", $Profile, "--mode", $Mode, "--patch-name", $PatchName)

if (-not [string]::IsNullOrWhiteSpace($TargetRoot)) {
    $pythonArgs += @("--target-root", $TargetRoot)
}

if (-not [string]::IsNullOrWhiteSpace($OutputPath)) {
    $pythonArgs += @("--output-path", $OutputPath)
}

& $PythonExe @pythonArgs
exit $LASTEXITCODE