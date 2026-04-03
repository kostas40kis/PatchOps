from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from patchops.reporting import RunOriginMetadata, build_run_origin_metadata
from patchops.workflows.apply_patch import apply_manifest


def test_build_run_origin_metadata_extracts_wrapper_run_provenance(tmp_path: Path) -> None:
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
        "patch_name": "mp26_run_origin_apply_contract",
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
            "report_name_prefix": "mp26_apply_contract",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)
    origin = build_run_origin_metadata(result)

    assert origin == RunOriginMetadata(
        workflow_mode="apply",
        manifest_path=manifest_path.resolve(),
        active_profile="generic_python",
        resolved_runtime=None,
        wrapper_project_root=wrapper_root.resolve(),
        target_project_root=target_root,
    )


def test_build_run_origin_metadata_allows_optional_fields_when_missing() -> None:
    result = SimpleNamespace(
        mode="inspect",
        manifest_path=Path("C:/demo/manifest.json"),
        resolved_profile=None,
        runtime_path=None,
        wrapper_project_root=Path("C:/demo/wrapper"),
        target_project_root=None,
    )

    origin = build_run_origin_metadata(result)

    assert origin == RunOriginMetadata(
        workflow_mode="inspect",
        manifest_path=Path("C:/demo/manifest.json"),
        active_profile=None,
        resolved_runtime=None,
        wrapper_project_root=Path("C:/demo/wrapper"),
        target_project_root=None,
    )
