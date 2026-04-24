from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.reporting import (
    ReportHeaderMetadata,
    RunOriginMetadata,
    build_report_header_metadata,
    build_run_origin_metadata,
    render_report_header,
    render_report_header_lines,
)


def test_render_report_header_lines_include_file_write_origin_when_present() -> None:
    manifest_path = Path("C:/bundle/manifest.json")
    metadata = ReportHeaderMetadata(
        patch_name="mp28_file_write_origin_report_contract",
        timestamp="2026-04-24 15:49:05",
        workspace_root=Path("C:/dev"),
        wrapper_project_root=Path("C:/dev/patchops"),
        target_project_root=Path("C:/dev/patchops"),
        active_profile="generic_python",
        runtime_path=None,
        report_path=Path("C:/Users/kostas/Desktop/report.txt"),
        manifest_path=manifest_path,
        mode="apply",
        backup_root=Path("C:/dev/patchops/data/runtime/patch_backups/mp28"),
        manifest_version="1",
        run_origin=RunOriginMetadata(
            workflow_mode="apply",
            manifest_path=manifest_path,
            active_profile="generic_python",
            resolved_runtime=None,
            wrapper_project_root=Path("C:/dev/patchops"),
            target_project_root=Path("C:/dev/patchops"),
            file_write_origin="wrapper_owned_write_engine",
        ),
    )

    lines = render_report_header_lines(metadata)
    text = "\n".join(lines)

    assert lines[0] == "PATCHOPS APPLY"
    assert "Patch Name           : mp28_file_write_origin_report_contract" in text
    assert "Wrapper Mode Used    : apply" in text
    assert "File Write Origin    : wrapper_owned_write_engine" in text


def test_build_run_origin_metadata_keeps_explicit_file_write_origin() -> None:
    result = SimpleNamespace(
        mode="apply",
        manifest_path=Path("C:/bundle/manifest.json"),
        resolved_profile=SimpleNamespace(name="generic_python"),
        runtime_path=None,
        wrapper_project_root=Path("C:/dev/patchops"),
        target_project_root=Path("C:/dev/patchops"),
        file_write_origin="wrapper_owned_write_engine",
        write_records=[],
    )

    origin = build_run_origin_metadata(result)

    assert origin.workflow_mode == "apply"
    assert origin.file_write_origin == "wrapper_owned_write_engine"


def test_build_report_header_metadata_keeps_file_write_origin_visible() -> None:
    result = SimpleNamespace(
        manifest=SimpleNamespace(
            patch_name="mp28_file_write_origin_metadata_contract",
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
        backup_root=Path("C:/dev/patchops/data/runtime/patch_backups/mp28"),
        run_origin=RunOriginMetadata(
            workflow_mode="apply",
            manifest_path=Path("C:/bundle/manifest.json"),
            active_profile="generic_python",
            resolved_runtime=None,
            wrapper_project_root=Path("C:/dev/patchops"),
            target_project_root=Path("C:/dev/patchops"),
            file_write_origin="wrapper_owned_write_engine",
        ),
        file_write_origin="wrapper_owned_write_engine",
        write_records=[],
    )

    metadata = build_report_header_metadata(result)
    header = render_report_header(metadata)

    assert metadata.patch_name == "mp28_file_write_origin_metadata_contract"
    assert metadata.run_origin is not None
    assert metadata.run_origin.file_write_origin == "wrapper_owned_write_engine"
    assert "File Write Origin    : wrapper_owned_write_engine" in header
    assert "Wrapper Mode Used    : apply" in header
