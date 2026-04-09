from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from patchops.bundles.launcher_formatter import normalize_powershell_launcher_text


SUPPORTED_OPERATOR_SCRIPT_KINDS = (
    "run-package-zip",
    "maintenance-gate",
)


@dataclass(frozen=True)
class OperatorScriptEmitResult:
    script_kind: str
    output_path: Path
    wrapper_project_root: str
    ok: bool
    issue_count: int
    issues: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "script_kind": self.script_kind,
            "output_path": str(self.output_path),
            "wrapper_project_root": self.wrapper_project_root,
            "ok": self.ok,
            "issue_count": self.issue_count,
            "issues": list(self.issues),
        }


def _validate_script_kind(script_kind: str) -> str:
    lowered = str(script_kind or "").strip().lower()
    if lowered not in SUPPORTED_OPERATOR_SCRIPT_KINDS:
        supported = ", ".join(SUPPORTED_OPERATOR_SCRIPT_KINDS)
        raise ValueError(
            f"Unsupported operator script kind: {script_kind}. Expected one of: {supported}"
        )
    return lowered


def _normalize_script_text(text: str) -> str:
    return normalize_powershell_launcher_text(
        text,
        safe_wrapper_mode="never",
    )


def _shared_powershell_helpers() -> str:
    return r'''
function ConvertTo-PatchOpsPsArgument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    if ($Value -notmatch '[\s\"]') {
        return $Value
    }

    $escaped = $Value.Replace('\\', '\\\\').Replace('"', '\\"')
    return ('"{0}"' -f $escaped)
}

function Resolve-PatchOpsPythonInvocation {
    param(
        [string]$PythonExe = ''
    )

    if (-not [string]::IsNullOrWhiteSpace($PythonExe)) {
        return @{
            PythonExe = $PythonExe
            PrefixArgs = @()
        }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $py) {
        return @{
            PythonExe = $py.Source
            PrefixArgs = @('-3')
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $python) {
        throw 'Could not find py or python on PATH.'
    }

    return @{
        PythonExe = $python.Source
        PrefixArgs = @()
    }
}

function Invoke-PatchOpsNativeCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [string]$WorkingDirectory = ''
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
        $psi.WorkingDirectory = $WorkingDirectory
    }
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $argumentListProperty = $psi.PSObject.Properties['ArgumentList']
    if ($null -ne $argumentListProperty) {
        foreach ($argument in $Arguments) {
            [void]$psi.ArgumentList.Add([string]$argument)
        }
    }
    else {
        $psi.Arguments = [string]::Join(' ', ($Arguments | ForEach-Object { ConvertTo-PatchOpsPsArgument $_ }))
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()

    return @{
        ExitCode = $process.ExitCode
        Stdout = $stdout
        Stderr = $stderr
    }
}

function Invoke-PatchOpsNative {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,
        [string]$WorkingDirectory = ''
    )

    $captured = Invoke-PatchOpsNativeCapture -FilePath $FilePath -Arguments $Arguments -WorkingDirectory $WorkingDirectory
    if (-not [string]::IsNullOrEmpty([string]$captured.Stdout)) {
        [Console]::Out.Write([string]$captured.Stdout)
    }
    if (-not [string]::IsNullOrEmpty([string]$captured.Stderr)) {
        [Console]::Error.Write([string]$captured.Stderr)
    }
    return [int]$captured.ExitCode
}
'''


def render_operator_script(
    script_kind: str,
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    default_bundle_zip_path: str = r"D:\patch_bundle.zip",
) -> str:
    kind = _validate_script_kind(script_kind)
    header = "[CmdletBinding()]\n"

    if kind == "run-package-zip":
        script = f'''{header}param(
    [string]$BundleZipPath = '{default_bundle_zip_path}',
    [string]$WrapperRepoRoot = '{wrapper_project_root}',
    [string]$PythonExe = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
{_shared_powershell_helpers()}

if (-not (Test-Path -LiteralPath $BundleZipPath)) {{
    throw ("Bundle zip not found: {{0}}" -f $BundleZipPath)
}}

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

$pythonInvocation = Resolve-PatchOpsPythonInvocation -PythonExe $PythonExe
$allArguments = @()
$allArguments += $pythonInvocation.PrefixArgs
$allArguments += @('-m', 'patchops.cli', 'run-package', $BundleZipPath, '--wrapper-root', $WrapperRepoRoot)
$exitCode = Invoke-PatchOpsNative -FilePath $pythonInvocation.PythonExe -Arguments $allArguments -WorkingDirectory $WrapperRepoRoot
exit $exitCode
'''
        return _normalize_script_text(script)

    script = f'''{header}param(
    [string]$WrapperRepoRoot = '{wrapper_project_root}',
    [switch]$CoreTestsGreen,
    [string]$ReportPath = '',
    [string]$PythonExe = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
{_shared_powershell_helpers()}

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

$pythonInvocation = Resolve-PatchOpsPythonInvocation -PythonExe $PythonExe
$allArguments = @()
$allArguments += $pythonInvocation.PrefixArgs
$allArguments += @('-m', 'patchops.cli', 'maintenance-gate', '--wrapper-root', $WrapperRepoRoot)

if ($CoreTestsGreen.IsPresent) {{
    $allArguments += @('--core-tests-green')
}}

if (-not [string]::IsNullOrWhiteSpace($ReportPath)) {{
    $allArguments += @('--report-path', $ReportPath)
}}

$captured = Invoke-PatchOpsNativeCapture -FilePath $pythonInvocation.PythonExe -Arguments $allArguments -WorkingDirectory $WrapperRepoRoot

if (-not [string]::IsNullOrEmpty([string]$captured.Stderr)) {{
    [Console]::Error.Write([string]$captured.Stderr)
}}

if ([int]$captured.ExitCode -ne 0) {{
    if (-not [string]::IsNullOrEmpty([string]$captured.Stdout)) {{
        [Console]::Out.Write([string]$captured.Stdout)
    }}
    exit ([int]$captured.ExitCode)
}}

$stdoutText = [string]$captured.Stdout
if ([string]::IsNullOrWhiteSpace($stdoutText)) {{
    throw 'maintenance-gate emitted no JSON payload.'
}}

try {{
    $rawPayload = $stdoutText | ConvertFrom-Json
}}
catch {{
    [Console]::Out.Write($stdoutText)
    throw 'maintenance-gate emitted invalid JSON payload.'
}}


function ConvertTo-PatchOpsOrderedMap {{
    param($InputObject)

    if ($null -eq $InputObject) {{
        return $null
    }}

    if (($InputObject -is [string]) -or ($InputObject -is [System.ValueType])) {{
        return $InputObject
    }}

    if ($InputObject -is [System.Collections.IDictionary]) {{
        $map = [ordered]@{{}}
        foreach ($key in $InputObject.Keys) {{
            $map[[string]$key] = ConvertTo-PatchOpsOrderedMap -InputObject $InputObject[$key]
        }}
        return $map
    }}

    if ($InputObject -is [System.Collections.IEnumerable] -and -not ($InputObject -is [string])) {{
        $items = @()
        foreach ($item in $InputObject) {{
            $items += ,(ConvertTo-PatchOpsOrderedMap -InputObject $item)
        }}
        return $items
    }}

    $properties = @($InputObject.PSObject.Properties)
    if ($properties.Length -gt 0) {{
        $map = [ordered]@{{}}
        foreach ($property in $properties) {{
            $map[$property.Name] = ConvertTo-PatchOpsOrderedMap -InputObject $property.Value
        }}
        return $map
    }}

    return $InputObject
}}

function Test-PatchOpsPsProperty {{
    param(
        $InputObject,
        [Parameter(Mandatory = $true)]
        [string]$PropertyName
    )

    if ($null -eq $InputObject) {{
        return $false
    }}

    $matchedProperties = @($InputObject.PSObject.Properties.Match($PropertyName))
    return ($matchedProperties.Length -gt 0)
}}


$normalized = ConvertTo-PatchOpsOrderedMap -InputObject $rawPayload
if ($null -eq $normalized) {{
    $normalized = [ordered]@{{}}
}}

if (-not $normalized.Contains('wrapper_project_root')) {{
    $normalized['wrapper_project_root'] = $WrapperRepoRoot
}}

$gateResults = [ordered]@{{}}

if (Test-PatchOpsPsProperty -InputObject $rawPayload -PropertyName 'regression_gate') {{
    $regression = ConvertTo-PatchOpsOrderedMap -InputObject $rawPayload.regression_gate
    if ($null -eq $regression) {{
        $regression = [ordered]@{{}}
    }}
    $regression['name'] = 'bundle_manifest_regression'
    $gateResults['bundle_manifest_regression'] = $regression
}}

if (Test-PatchOpsPsProperty -InputObject $rawPayload -PropertyName 'smoke_gate') {{
    $smoke = ConvertTo-PatchOpsOrderedMap -InputObject $rawPayload.smoke_gate
    if ($null -eq $smoke) {{
        $smoke = [ordered]@{{}}
    }}
    $smoke['name'] = 'post_build_bundle_smoke'
    $gateResults['post_build_bundle_smoke'] = $smoke
}}

if (Test-PatchOpsPsProperty -InputObject $rawPayload -PropertyName 'release_readiness') {{
    $readiness = ConvertTo-PatchOpsOrderedMap -InputObject $rawPayload.release_readiness
    if ($null -eq $readiness) {{
        $readiness = [ordered]@{{}}
    }}
    $readiness['name'] = 'release_readiness'
    $gateResults['release_readiness'] = $readiness
}}

if (Test-PatchOpsPsProperty -InputObject $rawPayload -PropertyName 'gate_results') {{
    $existingGateResults = ConvertTo-PatchOpsOrderedMap -InputObject $rawPayload.gate_results
    if ($existingGateResults -is [System.Collections.IDictionary]) {{
        foreach ($entry in $existingGateResults.GetEnumerator()) {{
            if (-not $gateResults.Contains([string]$entry.Key)) {{
                $gateResults[[string]$entry.Key] = $entry.Value
            }}
        }}
    }}
}}

$normalized['gate_results'] = $gateResults

[Console]::Out.Write(($normalized | ConvertTo-Json -Depth 10))
exit 0
'''
    return _normalize_script_text(script)


def emit_operator_script(
    output_path: str | Path,
    *,
    script_kind: str,
    wrapper_project_root: str = r"C:\dev\patchops",
    default_bundle_zip_path: str = r"D:\patch_bundle.zip",
) -> OperatorScriptEmitResult:
    path = Path(output_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    script_text = render_operator_script(
        script_kind,
        wrapper_project_root=wrapper_project_root,
        default_bundle_zip_path=default_bundle_zip_path,
    )
    path.write_text(script_text, encoding="utf-8")
    issues: list[str] = []
    if not path.exists():
        issues.append("script_not_written")
    return OperatorScriptEmitResult(
        script_kind=_validate_script_kind(script_kind),
        output_path=path,
        wrapper_project_root=wrapper_project_root,
        ok=not issues,
        issue_count=len(issues),
        issues=tuple(issues),
    )
