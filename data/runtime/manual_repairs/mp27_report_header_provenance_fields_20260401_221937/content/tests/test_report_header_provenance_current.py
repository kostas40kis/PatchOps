from __future__ import annotations

import json
from pathlib import Path

from patchops.reporting import RunOriginMetadata, build_report_header_metadata, render_report_header
from patchops.workflows.apply_patch import apply_manifest


def test_report_header_metadata_carries_run_origin_fields(tmp_path: Path) -> None:
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
        "patch_name": "mp27_header_provenance_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": "mp27_header_provenance_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
    metadata = build_report_header_metadata(result)

    assert metadata.run_origin == RunOriginMetadata(
        workflow_mode="apply",
        manifest_path=manifest_path.resolve(),
        active_profile="generic_python",
        resolved_runtime=None,
        wrapper_project_root=wrapper_root.resolve(),
        target_project_root=target_root,
    )

    text = render_report_header(metadata)
    assert "Wrapper Mode Used    : apply" in text
    assert f"Manifest Path Used   : {manifest_path.resolve()}" in text
    assert "Profile Resolved     : generic_python" in text
    assert "Runtime Resolved     : (none)" in text


def test_canonical_report_header_shows_provenance_fields(tmp_path: Path) -> None:
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
        "patch_name": "mp27_header_rendered_provenance_contract",
        "active_profile": "generic_python",
        "target_project_root": str(target_root),
        "backup_files": [],
        "files_to_write": [],
        "validation_commands": [],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str(report_dir),
            "report_name_prefix": "mp27_header_rendered_provenance_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
    report_text = result.report_path.read_text(encoding="utf-8")

    assert "Wrapper Mode Used    : apply" in report_text
    assert f"Manifest Path Used   : {manifest_path.resolve()}" in report_text
    assert "Profile Resolved     : generic_python" in report_text
    assert "Runtime Resolved     : (none)" in report_text
