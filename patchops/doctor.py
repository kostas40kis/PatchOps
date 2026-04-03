from __future__ import annotations

import os
import shutil
from pathlib import Path


PROFILE_DEFAULT_TARGETS = {
    "trader": "C:/dev/trader",
    "generic_python": None,
    "generic_python_powershell": None,
}


def _profiles_dir() -> Path:
    return Path(__file__).resolve().parent / "profiles"


def available_profiles() -> list[str]:
    result: list[str] = []
    profiles_dir = _profiles_dir()
    if not profiles_dir.exists():
        return result
    for item in sorted(profiles_dir.glob("*.py")):
        if item.stem in {"__init__", "base"}:
            continue
        result.append(item.stem)
    return result


def run_doctor(profile_name: str = "trader", target_root: str | None = None) -> dict:
    cwd = Path.cwd()
    workspace_root_guess = cwd.parent if cwd.name.lower() == "patchops" else cwd
    available = available_profiles()
    resolved_target = target_root or PROFILE_DEFAULT_TARGETS.get(profile_name)
    issues: list[str] = []

    if profile_name not in available:
        issues.append(f"Requested profile is not available: {profile_name}")

    if resolved_target:
        target_path = Path(resolved_target)
        target_exists = target_path.exists()
        if not target_exists:
            issues.append(f"Resolved target root does not exist: {target_path}")
    else:
        target_exists = None

    desktop_path = Path.home() / "Desktop"
    desktop_exists = desktop_path.exists()
    if not desktop_exists:
        issues.append(f"Desktop path not found: {desktop_path}")

    powershell_path = shutil.which("powershell.exe") or shutil.which("pwsh")
    if not powershell_path:
        issues.append("PowerShell executable was not found on PATH")

    python_path = shutil.which("py") or shutil.which("python") or os.environ.get("PYTHON")
    if not python_path:
        issues.append("Python launcher was not found on PATH")

    profile_module_path = _profiles_dir() / f"{profile_name}.py"

    return {
        "profile_requested": profile_name,
        "profile_available": profile_name in available,
        "available_profiles": available,
        "profile_module_path": str(profile_module_path),
        "working_directory": str(cwd),
        "workspace_root_guess": str(workspace_root_guess),
        "target_root": resolved_target,
        "target_root_exists": target_exists,
        "desktop_path": str(desktop_path),
        "desktop_exists": desktop_exists,
        "python_executable": python_path,
        "powershell_executable": powershell_path,
        "issues": issues,
        "issue_count": len(issues),
        "ok": len(issues) == 0,
    }
