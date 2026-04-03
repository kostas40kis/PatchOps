from __future__ import annotations

from datetime import datetime
from hashlib import sha1
from pathlib import Path

from patchops.files.paths import ensure_directory


WINDOWS_SAFE_REPORT_PATH_LIMIT = 220


def infer_workspace_root(target_project_root: Path) -> Path | None:
    return target_project_root.parent if target_project_root.parent != target_project_root else None


def default_report_directory() -> Path:
    return Path.home() / "Desktop"


def build_report_path(prefix: str, patch_name: str, report_dir: Path) -> Path:
    safe_prefix = prefix.lower().replace(" ", "_")
    safe_patch = patch_name.lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_directory(report_dir)

    name_token = safe_prefix if safe_prefix == safe_patch else f"{safe_prefix}_{safe_patch}"
    preferred = report_dir / f"{name_token}_{timestamp}.txt"

    if len(str(preferred)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return preferred

    digest_source = f"{safe_prefix}|{safe_patch}|{report_dir}"
    digest = sha1(digest_source.encode("utf-8")).hexdigest()[:12]
    compact_base = safe_patch[:40] if safe_patch else "report"
    compact = report_dir / f"{compact_base}_{digest}_{timestamp}.txt"

    if len(str(compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return compact

    very_compact = report_dir / f"r_{digest}_{timestamp}.txt"
    if len(str(very_compact)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return very_compact

    fallback_dir = default_report_directory() / "patchops_reports"
    ensure_directory(fallback_dir)

    desktop_name = f"r_{digest}_{timestamp}.txt"
    desktop_path = fallback_dir / desktop_name
    if len(str(desktop_path)) <= WINDOWS_SAFE_REPORT_PATH_LIMIT:
        return desktop_path

    return default_report_directory() / f"r_{digest}_{timestamp}.txt"
