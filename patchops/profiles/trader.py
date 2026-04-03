from __future__ import annotations

from pathlib import Path

from patchops.models import Manifest, ResolvedProfile


DEFAULT_TRADER_ROOT = Path(r"C:\dev\trader")


def build_profile(manifest: Manifest, wrapper_project_root: Path) -> ResolvedProfile:
    target_root = Path(manifest.target_project_root) if manifest.target_project_root else DEFAULT_TRADER_ROOT
    runtime_path = target_root / ".venv" / "Scripts" / "python.exe"
    return ResolvedProfile(
        name="trader",
        default_target_root=target_root,
        runtime_path=runtime_path,
        backup_root_name="data/runtime/patch_backups",
        report_prefix="trader_patch",
        strict_one_report=True,
        notes="Trader profile. Trader-specific assumptions stay here, not in the generic core.",
    )
