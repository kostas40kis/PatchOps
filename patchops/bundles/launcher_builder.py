from __future__ import annotations

from patchops.bundles.launcher_formatter import (
    ensure_safe_launcher_wrapper,
    normalize_bundle_launcher_text,
)


def build_patchops_bundle_launcher(
    manifest_relative_path: str = "manifest.json",
    wrapper_project_root: str = r"C:\dev\patchops",
    mode: str = "apply",
    launcher_directory_relative_to_bundle_root: bool = False,
    safe_wrapper_mode: str = "always",
) -> str:
    lowered_mode = (mode or "").strip().lower()
    if lowered_mode not in {"apply", "verify"}:
        raise ValueError(f"Unsupported launcher mode: {mode}")

    bundle_root_expression = "$PSScriptRoot"
    if launcher_directory_relative_to_bundle_root:
        bundle_root_expression = "(Split-Path -Parent $PSScriptRoot)"

    script = f"""param(
    [string]$WrapperRepoRoot = '{wrapper_project_root}'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$bundleRoot = {bundle_root_expression}
$manifestPath = Join-Path $bundleRoot '{manifest_relative_path}'

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

if (-not (Test-Path -LiteralPath $manifestPath)) {{
    throw ("Manifest not found: {{0}}" -f $manifestPath)
}}

Push-Location -LiteralPath $WrapperRepoRoot
try {{
    & py -m patchops.cli check $manifestPath
    & py -m patchops.cli inspect $manifestPath
    & py -m patchops.cli plan $manifestPath
    & py -m patchops.cli {lowered_mode} $manifestPath
}}
finally {{
    Pop-Location
}}
"""
    return normalize_bundle_launcher_text(
        script,
        safe_wrapper_mode=safe_wrapper_mode,
    )


def build_run_package_bundle_root_launcher(
    wrapper_project_root: str = r"C:\dev\patchops",
    safe_wrapper_mode: str = "always",
) -> str:
    script = f"""param(
    [string]$WrapperRepoRoot = '{wrapper_project_root}'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$bundleRoot = $PSScriptRoot

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

Push-Location -LiteralPath $WrapperRepoRoot
try {{
    & py -m patchops.cli run-package $bundleRoot --wrapper-root $WrapperRepoRoot
}}
finally {{
    Pop-Location
}}
"""
    return normalize_bundle_launcher_text(
        script,
        safe_wrapper_mode=safe_wrapper_mode,
    )


ensure_powershell_block_wrapped = ensure_safe_launcher_wrapper
render_single_launcher_script = build_patchops_bundle_launcher
