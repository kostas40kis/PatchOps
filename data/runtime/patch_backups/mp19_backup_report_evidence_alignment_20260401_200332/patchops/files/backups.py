from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import shutil

from patchops.files.paths import ensure_directory, safe_relative_path
from patchops.models import BackupRecord


@dataclass(frozen=True)
class BackupPlan:
    source: Path
    destination: Path
    existed: bool
    missing: bool
    relative_path: Path


def generate_backup_root(target_project_root: Path, backup_root_name: str, patch_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_patch = patch_name.lower().replace(" ", "_")
    return target_project_root / backup_root_name / f"{safe_patch}_{timestamp}"



def build_backup_plan(source: Path, target_project_root: Path, backup_root: Path) -> BackupPlan:
    relative = safe_relative_path(source, target_project_root)
    destination = backup_root / relative
    existed = source.exists()
    return BackupPlan(
        source=source,
        destination=destination,
        existed=existed,
        missing=not existed,
        relative_path=relative,
    )



def execute_backup_plan(plan: BackupPlan) -> BackupRecord:
    if plan.missing:
        return BackupRecord(source=plan.source, destination=None, existed=False)

    ensure_directory(plan.destination.parent)
    shutil.copy2(plan.source, plan.destination)
    return BackupRecord(source=plan.source, destination=plan.destination, existed=True)



def backup_file(source: Path, target_project_root: Path, backup_root: Path) -> BackupRecord:
    plan = build_backup_plan(source, target_project_root, backup_root)
    return execute_backup_plan(plan)