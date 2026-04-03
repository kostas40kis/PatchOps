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

# PATCHOPS_PATCH41_MIXED_PROFILE_HELPERS_START
from pathlib import Path as _PatchOpsPatch41Path

PATCHOPS_GENERIC_PYTHON_POWERSHELL_PROFILE_NAME = "generic_python_powershell"
PATCHOPS_GENERIC_PYTHON_POWERSHELL_MARKERS = ("python", "powershell")


def generic_python_powershell_runtime_candidates(target_project_root):
    root = _PatchOpsPatch41Path(str(target_project_root))
    return (
        str(root / ".venv" / "Scripts" / "python.exe"),
        "py",
        "python",
        str(root / ".venv" / "Scripts" / "pwsh.exe"),
        "pwsh",
        "powershell",
    )


def generic_python_powershell_profile_summary(target_project_root):
    return {
        "profile_name": PATCHOPS_GENERIC_PYTHON_POWERSHELL_PROFILE_NAME,
        "markers": PATCHOPS_GENERIC_PYTHON_POWERSHELL_MARKERS,
        "runtime_candidates": generic_python_powershell_runtime_candidates(target_project_root),
        "conservative": True,
        "notes": (
            "Use this profile for mixed Python and PowerShell repos without turning shell behavior into core wrapper logic.",
        ),
    }
# PATCHOPS_PATCH41_MIXED_PROFILE_HELPERS_END
