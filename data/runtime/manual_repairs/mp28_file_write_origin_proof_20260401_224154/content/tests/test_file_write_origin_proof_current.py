from __future__ import annotations

import json
from pathlib import Path

from patchops.reporting import build_report_header_metadata
from patchops.workflows.apply_patch import apply_manifest


def test_run_origin_metadata_marks_wrapper_owned_file_write_engine_when_writes_exist(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper_root"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    wrapper_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp28_file_write_origin_metadata_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/example.txt",
                "content": "written by wrapper",
                "content_path": None,
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
            "report_name_prefix": "mp28_file_write_origin_metadata_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
    metadata = build_report_header_metadata(result)

    assert result.result_label == "PASS"
    assert metadata.run_origin is not None
    assert metadata.run_origin.file_write_origin == "wrapper_owned_write_engine"


def test_canonical_report_header_shows_file_write_origin_for_wrapper_writes(tmp_path: Path) -> None:
    wrapper_root = tmp_path / "wrapper_root"
    manifest_root = tmp_path / "manifest_root"
    target_root = tmp_path / "target_root"
    report_dir = tmp_path / "reports"

    wrapper_root.mkdir(parents=True, exist_ok=True)
    manifest_root.mkdir(parents=True, exist_ok=True)
    target_root.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_root / "patch_manifest.json"
    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp28_file_write_origin_report_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [
            {
                "path": "docs/example.txt",
                "content": "written by wrapper",
                "content_path": None,
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
            "report_name_prefix": "mp28_file_write_origin_report_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
    report_text = result.report_path.read_text(encoding="utf-8")

    assert result.result_label == "PASS"
    assert "File Write Origin    : wrapper_owned_write_engine" in report_text
    assert "WROTE : " in report_text
