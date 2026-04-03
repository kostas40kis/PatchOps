from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from patchops.files.paths import ensure_directory, safe_relative_path
from patchops.models import BackupRecord


def generate_backup_root(target_project_root: Path, backup_root_name: str, patch_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_patch = patch_name.lower().replace(" ", "_")
    return target_project_root / backup_root_name / f"{safe_patch}_{timestamp}"


def backup_file(source: Path, target_project_root: Path, backup_root: Path) -> BackupRecord:
    if not source.exists():
        return BackupRecord(source=source, destination=None, existed=False)

    relative = safe_relative_path(source, target_project_root)
    destination = backup_root / relative
    ensure_directory(destination.parent)
    shutil.copy2(source, destination)
    return BackupRecord(source=source, destination=destination, existed=True)
