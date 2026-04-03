from __future__ import annotations

import json
from pathlib import Path

from patchops.files.writers import write_files
from patchops.models import FileWriteSpec, WriteRecord
from patchops.workflows.apply_patch import apply_manifest


def test_write_files_prefers_wrapper_project_root_for_content_path(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    wrapper_root = tmp_path / "wrapper"
    manifest_root = tmp_path / "manifest_root"

    wrapper_content = wrapper_root / "content" / "docs" / "source.txt"
    manifest_content = manifest_root / "content" / "docs" / "source.txt"
    wrapper_content.parent.mkdir(parents=True, exist_ok=True)
    manifest_content.parent.mkdir(parents=True, exist_ok=True)
    wrapper_content.write_text("wrapper-root-wins", encoding="utf-8")
    manifest_content.write_text("manifest-local-loses", encoding="utf-8")

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")

    spec = FileWriteSpec(
        path="docs/out.txt",
        content=None,
        content_path="content/docs/source.txt",
        encoding="utf-8",
    )

    records = write_files(
        [spec],
        target_root,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_root,
    )

    destination = target_root / "docs" / "out.txt"
    assert destination.read_text(encoding="utf-8") == "wrapper-root-wins"
    assert records == [WriteRecord(path=destination, encoding="utf-8")]


def test_write_files_falls_back_to_manifest_local_content_path(tmp_path: Path) -> None:
    target_root = tmp_path / "target"
    wrapper_root = tmp_path / "wrapper"
    manifest_root = tmp_path / "manifest_root"

    manifest_content = manifest_root / "content" / "docs" / "source.txt"
    manifest_content.parent.mkdir(parents=True, exist_ok=True)
    manifest_content.write_text("manifest-local-fallback", encoding="utf-8")

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")

    spec = FileWriteSpec(
        path="docs/out.txt",
        content=None,
        content_path="content/docs/source.txt",
        encoding="utf-8",
    )

    records = write_files(
        [spec],
        target_root,
        manifest_path=manifest_path,
        wrapper_project_root=wrapper_root,
    )

    destination = target_root / "docs" / "out.txt"
    assert destination.read_text(encoding="utf-8") == "manifest-local-fallback"
    assert records == [WriteRecord(path=destination, encoding="utf-8")]


def test_apply_manifest_preserves_wrapper_root_first_content_path_contract(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper_root"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    wrapper_content = wrapper_root / "content" / "payloads" / "demo.txt"
    manifest_content = manifest_root / "content" / "payloads" / "demo.txt"
    wrapper_content.parent.mkdir(parents=True, exist_ok=True)
    manifest_content.parent.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    wrapper_content.write_text("wrapper-apply-wins", encoding="utf-8")
    manifest_content.write_text("manifest-apply-loses", encoding="utf-8")

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp23_wrapper_root_first_apply_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/result.txt",
                "content": None,
                "content_path": "content/payloads/demo.txt",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": "mp23_apply_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    destination = target_root / "docs" / "result.txt"
    assert result.result_label == "PASS"
    assert destination.read_text(encoding="utf-8") == "wrapper-apply-wins"


def test_apply_manifest_keeps_manifest_local_content_path_fallback(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper_root"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    manifest_content = manifest_root / "content" / "payloads" / "demo.txt"
    manifest_content.parent.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest_content.write_text("manifest-apply-fallback", encoding="utf-8")

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp23_manifest_local_apply_fallback",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/result.txt",
                "content": None,
                "content_path": "content/payloads/demo.txt",
                "encoding": "utf-8",
            }
        ],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": "mp23_apply_fallback",
            "write_to_desktop": False,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    destination = target_root / "docs" / "result.txt"
    assert result.result_label == "PASS"
    assert destination.read_text(encoding="utf-8") == "manifest-apply-fallback"
