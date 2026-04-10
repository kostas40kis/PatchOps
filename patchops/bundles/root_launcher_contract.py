\
from __future__ import annotations


_LAUNCHER_TEMPLATE = """param(
    [string]$WrapperRepoRoot = "__WRAPPER_REPO_ROOT__"
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $PSCommandPath
$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"
if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {
    throw ("Wrapper repo root not found: {0}" -f $WrapperRepoRoot)
}

if (-not (Test-Path -LiteralPath $bundleMetaPath)) {
    throw ("bundle_meta.json not found: {0}" -f $bundleMetaPath)
}

Set-Location $WrapperRepoRoot
py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot
exit $LASTEXITCODE
"""


def emit_run_with_patchops_launcher(wrapper_repo_root: str = r"C:\dev\patchops") -> str:
    """Return the canonical root-level run_with_patchops.ps1 text.

    This helper exists to give bundle authoring one maintained source of truth for the
    root launcher shape. The launcher must begin directly with ``param(`` on the first
    line so future bundle packaging cannot accidentally prepend a stray character before
    the parameter block.
    """
    return _LAUNCHER_TEMPLATE.replace("__WRAPPER_REPO_ROOT__", wrapper_repo_root)
