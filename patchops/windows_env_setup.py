from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ctypes
import os
from typing import Iterable


_PROJECT_REPORT_NAMES = ("patchops", "trader", "generic_python", "_maintenance")


@dataclass(frozen=True)
class WindowsEnvSetupPlan:
    wrapper_project_root: Path
    reports_root: Path
    bin_root: Path
    project_report_roots: tuple[Path, ...]
    env_vars: dict[str, str]
    path_before: tuple[str, ...]
    path_after: tuple[str, ...]

    @property
    def path_will_change(self) -> bool:
        return self.path_before != self.path_after

    @property
    def directories_to_create(self) -> tuple[Path, ...]:
        return (self.reports_root, self.bin_root, *self.project_report_roots)


def _split_path_entries(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in str(value).split(os.pathsep) if str(item).strip()]


def _normalize_path_key(value: str | Path) -> str:
    text = str(value).rstrip("/\\")
    return text.casefold()


def _append_unique_path_entry(entries: Iterable[str], new_entry: str) -> tuple[str, ...]:
    normalized = {_normalize_path_key(item) for item in entries}
    ordered = list(entries)
    if _normalize_path_key(new_entry) not in normalized:
        ordered.append(new_entry)
    return tuple(ordered)


def build_windows_env_setup_plan(
    *,
    wrapper_project_root: str | Path | None = None,
    reports_root: str | Path | None = None,
    bin_root: str | Path | None = None,
    home_root: str | Path | None = None,
    existing_user_path: str | None = None,
) -> WindowsEnvSetupPlan:
    resolved_wrapper_root = (
        Path(wrapper_project_root).resolve()
        if wrapper_project_root is not None
        else Path(__file__).resolve().parents[1]
    )
    resolved_home_root = Path(home_root) if home_root is not None else Path.home()
    desktop_root = resolved_home_root / "Desktop"
    resolved_reports_root = Path(reports_root) if reports_root is not None else desktop_root / "PatchOpsReports"
    resolved_bin_root = Path(bin_root) if bin_root is not None else resolved_home_root / "bin" / "PatchOps"
    project_report_roots = tuple(resolved_reports_root / name for name in _PROJECT_REPORT_NAMES)

    path_before = tuple(_split_path_entries(existing_user_path))
    path_after = _append_unique_path_entry(path_before, str(resolved_bin_root))

    env_vars = {
        "PATCHOPS_WRAPPER_ROOT": str(resolved_wrapper_root),
        "PATCHOPS_REPORTS_ROOT": str(resolved_reports_root),
        "PATCHOPS_BIN": str(resolved_bin_root),
    }

    return WindowsEnvSetupPlan(
        wrapper_project_root=resolved_wrapper_root,
        reports_root=resolved_reports_root,
        bin_root=resolved_bin_root,
        project_report_roots=project_report_roots,
        env_vars=env_vars,
        path_before=path_before,
        path_after=path_after,
    )


def windows_env_setup_as_dict(plan: WindowsEnvSetupPlan) -> dict[str, object]:
    return {
        "wrapper_project_root": str(plan.wrapper_project_root),
        "reports_root": str(plan.reports_root),
        "bin_root": str(plan.bin_root),
        "project_report_roots": [str(path) for path in plan.project_report_roots],
        "env_vars": dict(plan.env_vars),
        "path_before": list(plan.path_before),
        "path_after": list(plan.path_after),
        "path_will_change": plan.path_will_change,
        "directory_count": len(plan.directories_to_create),
        "platform": os.name,
    }


def _broadcast_environment_change() -> None:
    if os.name != "nt":
        return
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            None,
        )
    except Exception:
        return


def _write_user_env_var_windows(name: str, value: str) -> None:
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)


def read_windows_user_path() -> str:
    if os.name != "nt":
        return os.environ.get("PATH", "")

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
            return "" if value is None else str(value)
    except FileNotFoundError:
        return ""
    except OSError:
        return ""


def apply_windows_env_setup(
    plan: WindowsEnvSetupPlan,
    *,
    persist_user_env: bool = True,
) -> dict[str, object]:
    created_directories: list[str] = []
    for directory in plan.directories_to_create:
        directory.mkdir(parents=True, exist_ok=True)
        created_directories.append(str(directory))

    for name, value in plan.env_vars.items():
        os.environ[name] = value
    os.environ["PATH"] = os.pathsep.join(plan.path_after)

    if persist_user_env:
        if os.name != "nt":
            raise RuntimeError("Persistent Windows environment setup is only supported on Windows. Use --dry-run outside Windows.")
        for name, value in plan.env_vars.items():
            _write_user_env_var_windows(name, value)
        _write_user_env_var_windows("Path", os.pathsep.join(plan.path_after))
        _broadcast_environment_change()

    return {
        "created_directories": created_directories,
        "persisted_user_env": bool(persist_user_env and os.name == "nt"),
        "path_updated": plan.path_will_change,
        "environment_broadcast": bool(persist_user_env and os.name == "nt"),
    }
