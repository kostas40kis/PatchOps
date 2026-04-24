from __future__ import annotations

import json
from pathlib import Path

from patchops.workflows.apply_patch import apply_manifest


def _build_manifest(
    target_root: Path,
    report_dir: Path,
    *,
    patch_name: str,
    files_to_write: list[dict[str, object]],
) -> dict[str, object]:
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


def _run_apply(manifest_root: Path, target_root: Path, report_dir: Path, *, patch_name: str, files_to_write: list[dict[str, object]]):
    manifest_path = manifest_root / "patch_manifest.json"
    manifest = _build_manifest(
        target_root,
        report_dir,
        patch_name=patch_name,
        files_to_write=files_to_write,
    )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return apply_manifest(manifest_path, wrapper_root=manifest_root)


def test_apply_manifest_existing_file_renders_backup_and_write_evidence(tmp_path: Path) -> None:
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    destination = target_root / "docs" / "existing.txt"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("old payload", encoding="utf-8")

    result = _run_apply(
        manifest_root,
        target_root,
        report_dir,
        patch_name="patch10_existing_backup_write_alignment",
        files_to_write=[
            {
                "path": "docs/existing.txt",
                "content": "new payload",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
    )

    report_text = Path(result.report_path).read_text(encoding="utf-8")
    assert "Result : PASS" in report_text
    assert "TARGET FILES" in report_text
    assert "WRITING FILES" in report_text
    assert f"BACKUP : {destination}" in report_text
    assert "docs/existing.txt" in report_text


def test_apply_manifest_missing_file_renders_missing_and_write_evidence(tmp_path: Path) -> None:
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    destination = target_root / "docs" / "new_file.txt"

    result = _run_apply(
        manifest_root,
        target_root,
        report_dir,
        patch_name="patch10_missing_backup_write_alignment",
        files_to_write=[
            {
                "path": "docs/new_file.txt",
                "content": "fresh payload",
                "content_path": None,
                "encoding": "utf-8",
            }
        ],
    )

    report_text = Path(result.report_path).read_text(encoding="utf-8")
    assert "Result : PASS" in report_text
    assert "TARGET FILES" in report_text
    assert "WRITING FILES" in report_text
    assert f"CREATED: {destination}" in report_text
    assert "docs/new_file.txt" in report_text