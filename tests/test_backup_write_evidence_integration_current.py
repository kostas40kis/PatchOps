from __future__ import annotations

import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def _build_manifest(target_root: Path, report_dir: Path, files_to_write: list[dict[str, object]], patch_name: str) -> dict[str, object]:
    return {
        "manifest_version": "1",
        "patch_name": patch_name,
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": files_to_write,
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": patch_name,
            "write_to_desktop": False,
        },
    }


def test_apply_manifest_report_matches_backup_and_write_for_existing_target(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    wrapper_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    destination = target_root / "docs" / "existing.txt"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("old payload", encoding="utf-8")

    manifest_path = manifest_root / "patch_manifest.json"
    manifest = _build_manifest(
        target_root,
        report_dir,
        [
            {
                "path": "docs/existing.txt",
                "content": "new payload",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "mp24_existing_backup_write_alignment",
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert destination.read_text(encoding="utf-8") == "new payload"

    backup_path = result.backup_root / "docs" / "existing.txt"
    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == "old payload"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert f"BACKUP : {destination} -> {backup_path}" in report_text
    assert f"WROTE : {destination}" in report_text


def test_apply_manifest_report_marks_missing_and_write_for_new_target(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    wrapper_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    destination = target_root / "docs" / "new.txt"

    manifest_path = manifest_root / "patch_manifest.json"
    manifest = _build_manifest(
        target_root,
        report_dir,
        [
            {
                "path": "docs/new.txt",
                "content": "created by proof",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
        "mp24_missing_backup_write_alignment",
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    assert result.result_label == "PASS"
    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "created by proof"

    report_text = result.report_path.read_text(encoding="utf-8")
    assert f"MISSING: {destination}" in report_text
    assert f"WROTE : {destination}" in report_text
