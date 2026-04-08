from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

from .launcher_builder import build_patchops_bundle_launcher
from .launcher_self_check import check_launcher_path


ROOT_BUNDLE_LAUNCHER_NAME = "run_with_patchops.ps1"
METADATA_DRIVEN_LAUNCHER_MODE = "metadata"


@dataclass(frozen=True)
class BundleLauncherEmitResult:
    launcher_path: Path
    mode: str
    wrapper_project_root: str
    script_text: str
    exists: bool
    ok: bool
    issue_count: int
    issues: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "launcher_path": str(self.launcher_path),
            "mode": self.mode,
            "wrapper_project_root": self.wrapper_project_root,
            "exists": self.exists,
            "ok": self.ok,
            "issue_count": self.issue_count,
            "issues": list(self.issues),
        }


def resolve_root_bundle_launcher_path(bundle_root_or_launcher_path: str | Path) -> Path:
    candidate = Path(bundle_root_or_launcher_path)
    if candidate.suffix.lower() == ".ps1":
        return candidate
    return candidate / ROOT_BUNDLE_LAUNCHER_NAME


def _render_metadata_driven_root_bundle_launcher(*, wrapper_project_root: str) -> str:
    script = textwrap.dedent(
        f'''\
param(
    [string]$WrapperRepoRoot = "{wrapper_project_root}"
)

$ErrorActionPreference = "Stop"

$bundleRoot = Split-Path -Parent $PSCommandPath
$bundleMetaPath = Join-Path $bundleRoot "bundle_meta.json"

if (-not (Test-Path -LiteralPath $WrapperRepoRoot)) {{
    throw ("Wrapper repo root not found: {{0}}" -f $WrapperRepoRoot)
}}

if (-not (Test-Path -LiteralPath $bundleMetaPath)) {{
    throw ("bundle_meta.json not found: {{0}}" -f $bundleMetaPath)
}}

Set-Location $WrapperRepoRoot
py -m patchops.cli bundle-entry $bundleRoot --wrapper-root $WrapperRepoRoot
'''
    )
    return script.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n") + "\n"


def render_root_bundle_launcher(
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    mode: str = METADATA_DRIVEN_LAUNCHER_MODE,
    safe_wrapper_mode: str = "never",
) -> str:
    lowered = str(mode or METADATA_DRIVEN_LAUNCHER_MODE).strip().lower()
    if lowered == METADATA_DRIVEN_LAUNCHER_MODE:
        return _render_metadata_driven_root_bundle_launcher(wrapper_project_root=wrapper_project_root)
    return build_patchops_bundle_launcher(
        wrapper_project_root=wrapper_project_root,
        mode=lowered,
        launcher_directory_relative_to_bundle_root=False,
        safe_wrapper_mode=safe_wrapper_mode,
    )


def emit_root_bundle_launcher(
    bundle_root_or_launcher_path: str | Path,
    *,
    wrapper_project_root: str = r"C:\dev\patchops",
    mode: str = METADATA_DRIVEN_LAUNCHER_MODE,
    safe_wrapper_mode: str = "never",
) -> BundleLauncherEmitResult:
    launcher_path = resolve_root_bundle_launcher_path(bundle_root_or_launcher_path)
    launcher_path.parent.mkdir(parents=True, exist_ok=True)

    script_text = render_root_bundle_launcher(
        wrapper_project_root=wrapper_project_root,
        mode=mode,
        safe_wrapper_mode=safe_wrapper_mode,
    )
    launcher_path.write_text(script_text, encoding="utf-8")

    payload = check_launcher_path(launcher_path)
    issues = tuple(str(item) for item in payload.get("issues", []))
    return BundleLauncherEmitResult(
        launcher_path=launcher_path,
        mode=str(mode).strip().lower(),
        wrapper_project_root=wrapper_project_root,
        script_text=script_text,
        exists=bool(payload.get("exists")),
        ok=bool(payload.get("ok")),
        issue_count=int(payload.get("issue_count") or 0),
        issues=issues,
    )
