from __future__ import annotations

from datetime import datetime
from pathlib import Path

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.metadata import build_report_header_metadata


def _build_result(tmp_path: Path) -> WorkflowResult:
    return WorkflowResult(
        mode="apply",
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name="metadata_demo",
            active_profile="generic_python",
            files_to_write=[],
        ),
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path / "target_project",
        runtime_path=tmp_path / ".venv" / "Scripts" / "python.exe",
        backup_root=tmp_path / "backup_root",
        report_path=tmp_path / "metadata_demo_report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=0,
        result_label="PASS",
    )


def test_build_report_header_metadata_extracts_current_header_fields(tmp_path: Path) -> None:
    result = _build_result(tmp_path)

    metadata = build_report_header_metadata(
        result,
        timestamp=datetime(2026, 4, 5, 14, 30, 0),
    )

    assert metadata.patch_name == "metadata_demo"
    assert metadata.timestamp == "2026-04-05 14:30:00"
    assert metadata.workspace_root == tmp_path.parent
    assert metadata.wrapper_project_root == tmp_path
    assert metadata.target_project_root == tmp_path / "target_project"
    assert metadata.active_profile == "generic_python"
    assert metadata.runtime_path == tmp_path / ".venv" / "Scripts" / "python.exe"
    assert metadata.report_path == tmp_path / "metadata_demo_report.txt"
    assert metadata.manifest_path == tmp_path / "manifest.json"


def test_build_report_header_metadata_allows_missing_optional_fields(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    result = WorkflowResult(
        mode=result.mode,
        manifest_path=result.manifest_path,
        manifest=result.manifest,
        resolved_profile=result.resolved_profile,
        workspace_root=None,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        runtime_path=None,
        backup_root=result.backup_root,
        report_path=result.report_path,
        backup_records=result.backup_records,
        write_records=result.write_records,
        validation_results=result.validation_results,
        smoke_results=result.smoke_results,
        audit_results=result.audit_results,
        cleanup_results=result.cleanup_results,
        archive_results=result.archive_results,
        failure=result.failure,
        exit_code=result.exit_code,
        result_label=result.result_label,
    )

    metadata = build_report_header_metadata(result)

    assert metadata.patch_name == "metadata_demo"
    assert metadata.workspace_root is None
    assert metadata.runtime_path is None
    assert metadata.report_path == tmp_path / "metadata_demo_report.txt"
    assert metadata.manifest_path == tmp_path / "manifest.json"
