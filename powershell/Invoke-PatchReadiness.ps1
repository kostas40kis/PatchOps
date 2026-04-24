[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][Alias("WrapperProjectRoot","WrapperRepoRoot")][string]$WrapperRoot = (Split-Path -Path $PSScriptRoot -Parent),
    [Parameter(Mandatory=$false)][string]$Profile = "",
    [Parameter(Mandatory=$false)][switch]$CoreTestsGreen,
    [Parameter(Mandatory=$false)][string]$ReportPath = ""
)

$PatchOpsRepoRoot = Split-Path -Path $PSScriptRoot -Parent

function ConvertTo-PatchOpsPsArgument {
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) { return '""' }
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }
    return $Value
}

function Invoke-PatchOpsNative {
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $PatchOpsRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {
        foreach ($arg in $Arguments) {
            $null = $psi.ArgumentList.Add([string]$arg)
        }
    }
    else {
        $converted = foreach ($arg in $Arguments) {
            ConvertTo-PatchOpsPsArgument -Value $arg
        }
        $psi.Arguments = [string]::Join(' ', $converted)
    }

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) { [Console]::Out.Write($stdout) }
    if ($stderr) { [Console]::Error.Write($stderr) }
    return $p.ExitCode
}

Set-Location -LiteralPath $PatchOpsRepoRoot
$arguments = @('-m', 'patchops.cli')
$arguments += @("release-readiness")
$arguments += @('--wrapper-root', $WrapperRoot)
if ($Profile) {
    $arguments += @('--profile', $Profile)
}
if ($CoreTestsGreen) {
    $arguments += @('--core-tests-green')
}
if ($ReportPath) {
    $arguments += @('--report-path', $ReportPath)
}

# Usage note: -ReportPath forwards to --report-path on release-readiness.
$exitCode = Invoke-PatchOpsNative -FilePath "py" -Arguments $arguments
exit $exitCode