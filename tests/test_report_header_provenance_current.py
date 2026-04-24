from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.reporting import (
    ReportHeaderMetadata,
    RunOriginMetadata,
    build_report_header_metadata,
    render_report_header,
    render_report_header_lines,
)


def test_render_report_header_lines_include_run_origin_fields() -> None:
    manifest_path = Path("C:/bundle/manifest.json")
    metadata = ReportHeaderMetadata(
        patch_name="mp27_report_header_provenance_contract",
        timestamp="2026-04-24 15:31:05",
        workspace_root=Path("C:/dev"),
        wrapper_project_root=Path("C:/dev/patchops"),
        target_project_root=Path("C:/dev/patchops"),
        active_profile="generic_python",
        runtime_path=None,
        report_path=Path("C:/Users/kostas/Desktop/report.txt"),
        manifest_path=manifest_path,
        mode="apply",
        backup_root=Path("C:/dev/patchops/data/runtime/patch_backups/mp27"),
        manifest_version="1",
        run_origin=RunOriginMetadata(
            workflow_mode="apply",
            manifest_path=manifest_path,
            active_profile="generic_python",
            resolved_runtime=None,
            wrapper_project_root=Path("C:/dev/patchops"),
            target_project_root=Path("C:/dev/patchops"),
        ),
    )

    lines = render_report_header_lines(metadata)
    text = "\n".join(lines)

    assert lines[0] == "PATCHOPS APPLY"
    assert "Patch Name           : mp27_report_header_provenance_contract" in text
    assert "Wrapper Mode Used    : apply" in text
    assert f"Manifest Path Used   : {manifest_path}" in text
    assert "Profile Resolved     : generic_python" in text
    assert "Runtime Resolved     : (none)" in text
    assert "Manifest Version     : 1" in text


def test_build_report_header_metadata_keeps_run_origin_visible() -> None:
    result = SimpleNamespace(
        manifest=SimpleNamespace(
            patch_name="mp27_report_header_provenance_contract",
            manifest_version=1,
        ),
        workspace_root=Path("C:/dev"),
        wrapper_project_root=Path("C:/dev/patchops"),
        target_project_root=Path("C:/dev/patchops"),
        resolved_profile=SimpleNamespace(name="generic_python"),
        runtime_path=None,
        report_path=Path("C:/Users/kostas/Desktop/report.txt"),
        manifest_path=Path("C:/bundle/manifest.json"),
        mode="apply",
        backup_root=Path("C:/dev/patchops/data/runtime/patch_backups/mp27"),
        run_origin=RunOriginMetadata(
            workflow_mode="apply",
            manifest_path=Path("C:/bundle/manifest.json"),
            active_profile="generic_python",
            resolved_runtime=None,
            wrapper_project_root=Path("C:/dev/patchops"),
            target_project_root=Path("C:/dev/patchops"),
        ),
        write_records=[],
    )

    metadata = build_report_header_metadata(result)
    header = render_report_header(metadata)

    assert metadata.patch_name == "mp27_report_header_provenance_contract"
    assert metadata.manifest_version == "1"
    assert metadata.active_profile == "generic_python"
    assert metadata.run_origin is not None
    assert metadata.run_origin.workflow_mode == "apply"
    assert metadata.run_origin.manifest_path == Path("C:/bundle/manifest.json")
    assert "Wrapper Mode Used    : apply" in header
    assert f"Manifest Path Used   : {result.manifest_path}" in header
    assert "Profile Resolved     : generic_python" in header
    assert "Runtime Resolved     : (none)" in header