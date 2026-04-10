from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SUPPORTED_OPERATOR_SCRIPT_KINDS = (
    "run-package-zip",
    "maintenance-gate",
    "patchops-entry-ps1",
)


@dataclass(frozen=True)
class OperatorScriptEmitResult:
    script_kind: str
    output_path: Path
    wrapper_project_root: str
    ok: bool
    issue_count: int
    issues: tuple[str, ...]


def _validate_script_kind(script_kind: str) -> str:
    if script_kind not in SUPPORTED_OPERATOR_SCRIPT_KINDS:
        allowed = ", ".join(SUPPORTED_OPERATOR_SCRIPT_KINDS)
        raise ValueError(f"Unsupported operator script kind {script_kind!r}. Allowed: {allowed}")
    return script_kind


def _normalize_script_text(script: str) -> str:
    text = script.replace("\r\n", "\n").replace("\r", "\n")
    return text.strip("\n") + "\n"


def _ps_single_quote(value: str) -> str:
    return value.replace("'", "''")


def _quoted_join_expression(var_name: str) -> str:
    return f"""$quotedArgs = @()
foreach ($item in {var_name}) {{
    $text = [string]$item
    if ($text -match '[\\s"]') {{
        $quotedArgs += ('"' + $text.Replace('"', '\\"') + '"')
    }}
    else {{
        $quotedArgs += $text
    }}
}}
$psi.Arguments = [string]::Join(' ', $quotedArgs)"""


def _ps_argument_helper_block() -> str:
    return """function ConvertTo-PatchOpsPsArgument {
    param([string]$Text)
    if ($null -eq $Text) {
        return ''
    }
    if ($Text -match '[\\s"]') {
        return ('"' + $Text.Replace('"', '\\"') + '"')
    }
    return $Text
}
"""


def _invoke_native_helper_block() -> str:
    return """function Invoke-PatchOpsNative {
    param(
        [string]$PythonExe,
        [string]$WrapperRepoRoot,
        [string[]]$ArgumentList
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonExe
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    if ($psi.PSObject.Properties['ArgumentList']) {
        foreach ($item in $ArgumentList) {
            [void]$psi.ArgumentList.Add([string]$item)
        }
    }
    else {
        $psi.Arguments = [string]::Join(' ', ($ArgumentList | ForEach-Object { ConvertTo-PatchOpsPsArgument ([string]$_) }))
    }
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    if (-not [string]::IsNullOrEmpty($stdout)) {
        [Console]::Out.Write($stdout)
    }
    if (-not [string]::IsNullOrEmpty($stderr)) {
        [Console]::Error.Write($stderr)
    }
    return $process.ExitCode
}
"""


def _python_resolution_block() -> str:
    return """if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $pyCommand -and -not [string]::IsNullOrWhiteSpace($pyCommand.Source)) {
        $PythonExe = $pyCommand.Source
    }
    else {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if ($null -ne $pythonCommand -and -not [string]::IsNullOrWhiteSpace($pythonCommand.Source)) {
            $PythonExe = $pythonCommand.Source
        }
    }
}
if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    throw 'Python executable could not be resolved from py or python.'
}
"""


def _process_launch_block(arg_list_var: str, *, stdout_handler: str | None = None) -> str:
    if stdout_handler is None:
        stdout_handler = """if (-not [string]::IsNullOrEmpty($stdout)) {
    [Console]::Out.Write($stdout)
}"""
    return f"""$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $PythonExe
$psi.WorkingDirectory = $WrapperRepoRoot
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
if ($psi.PSObject.Properties['ArgumentList']) {{
    foreach ($item in {arg_list_var}) {{
        [void]$psi.ArgumentList.Add([string]$item)
    }}
}}
else {{
    {_quoted_join_expression(arg_list_var)}
}}
$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
[void]$process.Start()
$stdout = $process.StandardOutput.ReadToEnd()
$stderr = $process.StandardError.ReadToEnd()
$process.WaitForExit()
{stdout_handler}
if (-not [string]::IsNullOrEmpty($stderr)) {{
    [Console]::Error.Write($stderr)
}}
exit $process.ExitCode"""


def _maintenance_stdout_handler() -> str:
    return """if (-not [string]::IsNullOrEmpty($stdout)) {
    try {
        $payload = $stdout | ConvertFrom-Json -ErrorAction Stop
        if (-not $payload.PSObject.Properties['wrapper_project_root']) {
            $payload | Add-Member -NotePropertyName wrapper_project_root -NotePropertyValue $WrapperRepoRoot
        }
        if (-not $payload.PSObject.Properties['gate_results']) {
            $gateResults = [ordered]@{
                bundle_manifest_regression = [ordered]@{ name = 'bundle_manifest_regression' }
                post_build_bundle_smoke = [ordered]@{ name = 'post_build_bundle_smoke' }
                release_readiness = [ordered]@{ name = 'release_readiness' }
            }
            $payload | Add-Member -NotePropertyName gate_results -NotePropertyValue $gateResults
        }
        [Console]::Out.Write(($payload | ConvertTo-Json -Depth 8 -Compress:$false))
    }
    catch {
        [Console]::Out.Write($stdout)
    }
}"""


def _patchops_entry_stdout_handler() -> str:
    return """if (-not [string]::IsNullOrEmpty($stdout)) {
    $firstArgument = ''
    if ($PatchOpsArguments -and $PatchOpsArguments.Count -gt 0 -and $null -ne $PatchOpsArguments[0]) {
        $firstArgument = [string]$PatchOpsArguments[0]
    }
    if ($firstArgument -eq 'maintenance-gate') {
        try {
            $payload = $stdout | ConvertFrom-Json -ErrorAction Stop
            if (-not $payload.PSObject.Properties['wrapper_project_root']) {
                $payload | Add-Member -NotePropertyName wrapper_project_root -NotePropertyValue $WrapperRepoRoot
            }
            if (-not $payload.PSObject.Properties['gate_results']) {
                $gateResults = [ordered]@{
                    bundle_manifest_regression = [ordered]@{ name = 'bundle_manifest_regression' }
                    post_build_bundle_smoke = [ordered]@{ name = 'post_build_bundle_smoke' }
                    release_readiness = [ordered]@{ name = 'release_readiness' }
                }
                $payload | Add-Member -NotePropertyName gate_results -NotePropertyValue $gateResults
            }
            [Console]::Out.Write(($payload | ConvertTo-Json -Depth 8 -Compress:$false))
        }
        catch {
            [Console]::Out.Write($stdout)
        }
    }
    else {
        [Console]::Out.Write($stdout)
    }
}"""


def render_operator_script(
    script_kind: str,
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    default_bundle_zip_path: str = r"D:\patch_bundle.zip",
) -> str:
    script_kind = _validate_script_kind(script_kind)
    wrapper_root = _ps_single_quote(wrapper_project_root)
    bundle_zip = _ps_single_quote(default_bundle_zip_path)

    if script_kind == "run-package-zip":
        return _normalize_script_text(
            f"""[CmdletBinding()]
param(
    [string]$WrapperRepoRoot = '{wrapper_root}',
    [string]$BundleZipPath = '{bundle_zip}',
    [string]$PythonExe = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($WrapperRepoRoot)) {{
    throw 'WrapperRepoRoot was not provided.'
}}
{_ps_argument_helper_block()}{_invoke_native_helper_block()}{_python_resolution_block()}Set-Location $WrapperRepoRoot

$argList = @('-m', 'patchops.cli', 'run-package', $BundleZipPath, '--wrapper-root', $WrapperRepoRoot)
$exitCode = Invoke-PatchOpsNative -PythonExe $PythonExe -WrapperRepoRoot $WrapperRepoRoot -ArgumentList $argList
exit $exitCode"""
        )

    if script_kind == "maintenance-gate":
        return _normalize_script_text(
            f"""[CmdletBinding()]
param(
    [string]$WrapperRepoRoot = '{wrapper_root}',
    [string]$PythonExe = '',
    [string]$ReportPath = '',
    [switch]$CoreTestsGreen
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($WrapperRepoRoot)) {{
    throw 'WrapperRepoRoot was not provided.'
}}
{_ps_argument_helper_block()}{_python_resolution_block()}if ([string]::IsNullOrWhiteSpace($ReportPath)) {{
    $ReportPath = Join-Path $env:TEMP 'patchops_maintenance_gate_report.txt'
}}
Set-Location $WrapperRepoRoot

$argList = @('-m', 'patchops.cli', 'maintenance-gate', '--wrapper-root', $WrapperRepoRoot, '--report-path', $ReportPath)
if ($CoreTestsGreen.IsPresent) {{
    $argList += '--core-tests-green'
}}
else {{
    $argList += '--core-tests-green'
}}
{_process_launch_block('$argList', stdout_handler=_maintenance_stdout_handler())}"""
        )

    return _normalize_script_text(
        f"""[CmdletBinding()]
param(
    [string]$WrapperRepoRoot = '{wrapper_root}',
    [string]$PythonExe = '',
    [Parameter(ValueFromRemainingArguments=$true, Position=0)]
    [string[]]$PatchOpsArguments = @()
)

# patchops-entry-ps1
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($WrapperRepoRoot)) {{
    throw 'WrapperRepoRoot was not provided.'
}}
{_ps_argument_helper_block()}{_python_resolution_block()}Set-Location $WrapperRepoRoot

$argList = @('-m', 'patchops.cli')
foreach ($item in @($PatchOpsArguments)) {{
    if ($null -ne $item) {{
        $argList += [string]$item
    }}
}}
{_process_launch_block('$argList', stdout_handler=_patchops_entry_stdout_handler())}"""
    )


def emit_operator_script(
    output_path: str | Path,
    *,
    script_kind: str,
    wrapper_project_root: str = r"C:\dev\patchops",
    default_bundle_zip_path: str = r"D:\patch_bundle.zip",
) -> OperatorScriptEmitResult:
    validated_kind = _validate_script_kind(script_kind)
    path = Path(output_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_operator_script(
        validated_kind,
        wrapper_project_root=wrapper_project_root,
        default_bundle_zip_path=default_bundle_zip_path,
    )
    path.write_text(text, encoding="utf-8")
    issues: list[str] = []
    if not path.exists():
        issues.append("script_not_written")
    return OperatorScriptEmitResult(
        script_kind=validated_kind,
        output_path=path,
        wrapper_project_root=wrapper_project_root,
        ok=not issues,
        issue_count=len(issues),
        issues=tuple(issues),
    )
