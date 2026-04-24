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
$firstArgument = ''
if ($PatchOpsArguments -and $PatchOpsArguments.Count -gt 0 -and $null -ne $PatchOpsArguments[0]) {{
    $firstArgument = [string]$PatchOpsArguments[0]
}}
if (($firstArgument -eq 'maintenance-gate' -or $firstArgument -eq 'setup-windows-env') -and -not ($PatchOpsArguments -contains '--wrapper-root')) {{
    $argList += '--wrapper-root'
    $argList += $WrapperRepoRoot
}}
{_process_launch_block('$argList')}"""
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

# PATCHOPS_D2_OPERATOR_SCRIPT_EMITTER_RUNTIME_OVERRIDE_20260423
from dataclasses import dataclass as _patchops_d2_dataclass
from pathlib import Path as _patchops_d2_Path

@_patchops_d2_dataclass
class OperatorScriptEmissionResult:
    ok: bool
    issue_count: int
    output_path: _patchops_d2_Path
    script_kind: str

SUPPORTED_OPERATOR_SCRIPT_KINDS = (
    "run-package-zip",
    "maintenance-gate",
    "patchops-entry-ps1",
)

def _patchops_d2_run_package_script(*, wrapper_project_root: str, default_bundle_zip_path: str | None = None) -> str:
    bundle_default = default_bundle_zip_path or r"D:\patch_bundle.zip"
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(Mandatory=$false)][string]$BundleZipPath = "{bundle_default}"
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\s"]') {{
        return '"' + ($Value -replace '"', '\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$exitCode = Invoke-PatchOpsNative -FilePath "py" -Arguments @(
    "-m", "patchops.cli", "run-package", $BundleZipPath, "--wrapper-root", $WrapperRepoRoot
)
exit $exitCode
"""

def _patchops_d2_maintenance_gate_script(*, wrapper_project_root: str) -> str:
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(Mandatory=$false)][string]$ReportPath = "",
    [Parameter(Mandatory=$false)][string]$CoreTestsGreen = ""
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\s"]') {{
        return '"' + ($Value -replace '"', '\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$argsList = @("-m", "patchops.cli", "maintenance-gate", "--wrapper-root", $WrapperRepoRoot)
if ($CoreTestsGreen) {{
    $argsList += @("--core-tests-green", $CoreTestsGreen)
}}
if ($ReportPath) {{
    $argsList += @("--report-path", $ReportPath)
}}
$exitCode = Invoke-PatchOpsNative -FilePath "py" -Arguments $argsList
exit $exitCode
"""

def _patchops_d2_patchops_entry_script(*, wrapper_project_root: str) -> str:
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$PatchOpsArguments
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\s"]') {{
        return '"' + ($Value -replace '"', '\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$exitCode = Invoke-PatchOpsNative -FilePath "py" -Arguments (@("-m", "patchops.cli") + $PatchOpsArguments)
exit $exitCode
"""

def render_operator_script(script_kind: str, *, wrapper_project_root: str, default_bundle_zip_path: str | None = None) -> str:
    if script_kind == "run-package-zip":
        return _patchops_d2_run_package_script(
            wrapper_project_root=wrapper_project_root,
            default_bundle_zip_path=default_bundle_zip_path,
        )
    if script_kind == "maintenance-gate":
        return _patchops_d2_maintenance_gate_script(
            wrapper_project_root=wrapper_project_root,
        )
    if script_kind == "patchops-entry-ps1":
        return _patchops_d2_patchops_entry_script(
            wrapper_project_root=wrapper_project_root,
        )
    raise ValueError(f"Unsupported operator script kind: {script_kind}")

def emit_operator_script(
    output_path,
    *,
    script_kind: str,
    wrapper_project_root: str,
    default_bundle_zip_path: str | None = None,
):
    rendered = render_operator_script(
        script_kind,
        wrapper_project_root=wrapper_project_root,
        default_bundle_zip_path=default_bundle_zip_path,
    )
    output = _patchops_d2_Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n")
    return OperatorScriptEmissionResult(
        ok=True,
        issue_count=0,
        output_path=output,
        script_kind=script_kind,
    )

# PATCHOPS_D2A_OPERATOR_SCRIPT_RUNTIME_OVERRIDE_20260423
def _patchops_d2a_run_package_script(*, wrapper_project_root: str, default_bundle_zip_path: str | None = None) -> str:
    bundle_default = default_bundle_zip_path or r"D:\patch_bundle.zip"
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(Mandatory=$false)][string]$BundleZipPath = "{bundle_default}"
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\\s"]') {{
        return '"' + ($Value -replace '"', '\\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$exitCode = Invoke-PatchOpsNative -FilePath 'py' -Arguments @(
    '-m', 'patchops.cli', 'run-package', $BundleZipPath, '--wrapper-root', $WrapperRepoRoot
)
exit $exitCode
"""

def _patchops_d2a_maintenance_gate_script(*, wrapper_project_root: str) -> str:
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(Mandatory=$false)][string]$ReportPath = "",
    [Parameter(Mandatory=$false)][string]$CoreTestsGreen = ""
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\\s"]') {{
        return '"' + ($Value -replace '"', '\\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$argsList = @('-m', 'patchops.cli', 'maintenance-gate', '--wrapper-root', $WrapperRepoRoot)
if ($CoreTestsGreen) {{
    $argsList += @('--core-tests-green', $CoreTestsGreen)
}}
if ($ReportPath) {{
    $argsList += @('--report-path', $ReportPath)
}}
$exitCode = Invoke-PatchOpsNative -FilePath 'py' -Arguments $argsList
exit $exitCode
"""

def _patchops_d2a_patchops_entry_script(*, wrapper_project_root: str) -> str:
    return f"""[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)][string]$WrapperRepoRoot = "{wrapper_project_root}",
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$PatchOpsArguments
)

function ConvertTo-PatchOpsPsArgument {{
    param([AllowNull()][string]$Value)
    if ($null -eq $Value) {{ return '""' }}
    if ($Value -match '[\\s"]') {{
        return '"' + ($Value -replace '"', '\\"') + '"'
    }}
    return $Value
}}

function Invoke-PatchOpsNative {{
    param(
        [Parameter(Mandatory=$true)][string]$FilePath,
        [Parameter(Mandatory=$true)][string[]]$Arguments
    )

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FilePath
    $psi.WorkingDirectory = $WrapperRepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    if ($psi.PSObject.Properties['ArgumentList'] -and $null -ne $psi.ArgumentList) {{
        foreach ($arg in $Arguments) {{
            $null = $psi.ArgumentList.Add([string]$arg)
        }}
    }}
    else {{
        $converted = foreach ($arg in $Arguments) {{
            ConvertTo-PatchOpsPsArgument -Value $arg
        }}
        $psi.Arguments = [string]::Join(' ', $converted)
    }}

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    $null = $p.Start()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()
    if ($stdout) {{ [Console]::Out.Write($stdout) }}
    if ($stderr) {{ [Console]::Error.Write($stderr) }}
    return $p.ExitCode
}}

Set-Location -LiteralPath $WrapperRepoRoot
$forwarded = @($PatchOpsArguments)
if ($forwarded.Count -gt 0 -and $forwarded[0] -eq 'maintenance-gate') {{
    $remaining = @()
    if ($forwarded.Count -gt 1) {{
        $remaining = $forwarded[1..($forwarded.Count - 1)]
    }}
    $hasWrapperRoot = $false
    foreach ($item in $remaining) {{
        if ($item -eq '--wrapper-root') {{
            $hasWrapperRoot = $true
            break
        }}
    }}
    if (-not $hasWrapperRoot) {{
        $forwarded = @('maintenance-gate', '--wrapper-root', $WrapperRepoRoot) + $remaining
    }}
}}
$exitCode = Invoke-PatchOpsNative -FilePath 'py' -Arguments (@('-m', 'patchops.cli') + $forwarded)
exit $exitCode
"""

def render_operator_script(script_kind: str, *, wrapper_project_root: str, default_bundle_zip_path: str | None = None) -> str:
    if script_kind == "run-package-zip":
        return _patchops_d2a_run_package_script(
            wrapper_project_root=wrapper_project_root,
            default_bundle_zip_path=default_bundle_zip_path,
        )
    if script_kind == "maintenance-gate":
        return _patchops_d2a_maintenance_gate_script(
            wrapper_project_root=wrapper_project_root,
        )
    if script_kind == "patchops-entry-ps1":
        return _patchops_d2a_patchops_entry_script(
            wrapper_project_root=wrapper_project_root,
        )
    raise ValueError(f"Unsupported operator script kind: {script_kind}")

def emit_operator_script(
    output_path,
    *,
    script_kind: str,
    wrapper_project_root: str,
    default_bundle_zip_path: str | None = None,
):
    rendered = render_operator_script(
        script_kind,
        wrapper_project_root=wrapper_project_root,
        default_bundle_zip_path=default_bundle_zip_path,
    )
    output = _patchops_d2_Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n".encode("utf-8").decode("unicode_escape"))
    return OperatorScriptEmissionResult(
        ok=True,
        issue_count=0,
        output_path=output,
        script_kind=script_kind,
    )

# PATCHOPS_D2B_OPERATOR_SCRIPT_WRITE_NEWLINE_OVERRIDE_20260423
def emit_operator_script(
    output_path,
    *,
    script_kind: str,
    wrapper_project_root: str,
    default_bundle_zip_path: str | None = None,
):
    rendered = render_operator_script(
        script_kind,
        wrapper_project_root=wrapper_project_root,
        default_bundle_zip_path=default_bundle_zip_path,
    )
    output = _patchops_d2_Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8", newline="\n".encode("utf-8").decode("unicode_escape"))
    return OperatorScriptEmissionResult(
        ok=True,
        issue_count=0,
        output_path=output,
        script_kind=script_kind,
    )
