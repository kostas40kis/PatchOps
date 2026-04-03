[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ManifestPath,

    [string]$WrapperRoot,

    [string]$RetryReason,

    [switch]$Preview,

    [string]$RuntimePath
)

$ErrorActionPreference = 'Stop'

function Resolve-WrapperRoot {
    param([string]$ExplicitRoot)

    if (-not [string]::IsNullOrWhiteSpace($ExplicitRoot)) {
        return (Resolve-Path -LiteralPath $ExplicitRoot).Path
    }

    return (Split-Path -Parent $PSScriptRoot)
}

function Resolve-PythonCommand {
    param(
        [string]$WrapperRoot,
        [string]$RuntimePath
    )

    $candidates = New-Object System.Collections.Generic.List[object]

    if (-not [string]::IsNullOrWhiteSpace($RuntimePath)) {
        $candidates.Add([pscustomobject]@{
            FilePath = $RuntimePath
            PrefixArguments = @()
            RequiresExists = $true
        })
    }

    $candidates.Add([pscustomobject]@{
        FilePath = (Join-Path $WrapperRoot '.venv\Scripts\python.exe')
        PrefixArguments = @()
        RequiresExists = $true
    })

    $candidates.Add([pscustomobject]@{
        FilePath = (Join-Path $WrapperRoot 'venv\Scripts\python.exe')
        PrefixArguments = @()
        RequiresExists = $true
    })

    if ($env:VIRTUAL_ENV) {
        $candidates.Add([pscustomobject]@{
            FilePath = (Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe')
            PrefixArguments = @()
            RequiresExists = $true
        })
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        $candidates.Add([pscustomobject]@{
            FilePath = $py.Source
            PrefixArguments = @('-3')
            RequiresExists = $true
        })
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $candidates.Add([pscustomobject]@{
            FilePath = $python.Source
            PrefixArguments = @()
            RequiresExists = $true
        })
    }

    foreach ($candidate in $candidates) {
        if ($candidate.RequiresExists -and -not (Test-Path -LiteralPath $candidate.FilePath)) {
            continue
        }
        return $candidate
    }

    throw 'Unable to resolve a Python runtime. Pass -RuntimePath explicitly.'
}

$resolvedWrapperRoot = Resolve-WrapperRoot -ExplicitRoot $WrapperRoot
$python = Resolve-PythonCommand -WrapperRoot $resolvedWrapperRoot -RuntimePath $RuntimePath

$arguments = @()
$arguments += $python.PrefixArguments
$arguments += '-m'
$arguments += 'patchops.cli'

if ($Preview) {
    $arguments += 'plan'
    $arguments += $ManifestPath
    $arguments += '--mode'
    $arguments += 'wrapper_retry'
    $arguments += '--wrapper-root'
    $arguments += $resolvedWrapperRoot
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}
else {
    $arguments += 'wrapper-retry'
    $arguments += $ManifestPath
    $arguments += '--wrapper-root'
    $arguments += $resolvedWrapperRoot
    if (-not [string]::IsNullOrWhiteSpace($RetryReason)) {
        $arguments += '--retry-reason'
        $arguments += $RetryReason
    }
}

& $python.FilePath @arguments
if ($null -eq $LASTEXITCODE) {
    exit 0
}
exit $LASTEXITCODE