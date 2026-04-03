from __future__ import annotations

import json
from pathlib import Path

from patchops.reporting import build_report_header_metadata, render_report_header
from patchops.reporting.sections import header_section
from patchops.workflows.apply_patch import apply_manifest


def test_header_section_delegates_to_metadata_renderer(tmp_path: Path) -> None:
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
        "patch_name": "mp27c_header_section_bridge",
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
            "report_name_prefix": "mp27c_header_section_bridge",
            "write_to_desktop": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")

    result = apply_manifest(manifest_path, wrapper_project_root=wrapper_root)

    expected = render_report_header(build_report_header_metadata(result))
    actual = header_section(result)

    assert actual == expected
    assert "Wrapper Mode Used    : apply" in actual
    assert f"Manifest Path Used   : {manifest_path.resolve()}" in actual
