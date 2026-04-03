from __future__ import annotations

from pathlib import Path

from patchops.models import Manifest, ResolvedProfile


def build_profile(manifest: Manifest, wrapper_project_root: Path) -> ResolvedProfile:
    target_root = Path(manifest.target_project_root) if manifest.target_project_root else None
    runtime_path = None
    if target_root is not None:
        candidate = target_root / ".venv" / "Scripts" / "python.exe"
        runtime_path = candidate if candidate.exists() else None

    return ResolvedProfile(
        name="generic_python_powershell",
        default_target_root=target_root,
        runtime_path=runtime_path,
        backup_root_name="data/runtime/patch_backups",
        report_prefix="generic_python_powershell_patch",
        strict_one_report=True,
        notes="Generic mixed Python/PowerShell profile.",
    )
