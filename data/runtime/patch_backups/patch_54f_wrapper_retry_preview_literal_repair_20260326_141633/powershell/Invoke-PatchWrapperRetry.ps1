[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot = '',

    [string]$RuntimePath = '',

    [switch]$Preview,

    [string]$RetryReason = ''
)

$ErrorActionPreference = 'Stop'

function Resolve-PatchOpsPython {
    param(
        [string]$WrapperRoot,
        [string]$RuntimePath
    )

    if (-not [string]::IsNullOrWhiteSpace($RuntimePath)) {
        return [pscustomobject]@{ FilePath = $RuntimePath; PrefixArgs = @() }
    }

    $repoVenv = Join-Path $WrapperRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $repoVenv) {
        return [pscustomobject]@{ FilePath = $repoVenv; PrefixArgs = @() }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return [pscustomobject]@{ FilePath = $py.Source; PrefixArgs = @('-3') }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return [pscustomobject]@{ FilePath = $python.Source; PrefixArgs = @() }
    }

    throw 'Unable to resolve Python for PatchOps wrapper retry launcher.'
}

if ([string]::IsNullOrWhiteSpace($WrapperRoot)) {
    if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $WrapperRoot = Split-Path -Path $PSScriptRoot -Parent
    }
    else {
        $WrapperRoot = (Get-Location).Path
    }
}

if ([string]::IsNullOrWhiteSpace($RetryReason)) {
    $RetryReason = 'wrapper/reporting failure after likely content success'
}

$python = Resolve-PatchOpsPython -WrapperRoot $WrapperRoot -RuntimePath $RuntimePath
$arguments = @('-m', 'patchops.cli')

if ($Preview) {
    $arguments += @(
        'plan',
        $ManifestPath,
        '--wrapper-root',
        $WrapperRoot,
        '--mode',
        'wrapper_retry',
        '--retry-reason',
        $RetryReason
    )
}
else {
    $arguments += @(
        'wrapper-retry',
        $ManifestPath,
        '--wrapper-root',
        $WrapperRoot,
        '--retry-reason',
        $RetryReason
    )
}

$arguments = @($python.PrefixArgs + $arguments)
& $python.FilePath @arguments
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE