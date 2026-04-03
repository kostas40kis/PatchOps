from pathlib import Path

project_root = Path(r"C:\dev\patchops")

metadata_path = project_root / "patchops" / "reporting" / "metadata.py"
metadata_path.parent.mkdir(parents=True, exist_ok=True)
metadata_path.write_text(
    """from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from patchops.models import WorkflowResult


@dataclass(frozen=True)
class ReportHeaderMetadata:
    patch_name: str
    timestamp: str | None
    workspace_root: Path | None
    wrapper_project_root: Path | None
    target_project_root: Path
    active_profile: str
    runtime_path: Path | None
    report_path: Path
    manifest_path: Path | None

    @property
    def manifest_identity(self) -> str | None:
        if self.manifest_path is None:
            return None
        return str(self.manifest_path)


def _normalize_timestamp(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)


def build_report_header_metadata(
    result: WorkflowResult,
    *,
    timestamp: datetime | str | None = None,
) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        patch_name=result.manifest.patch_name,
        timestamp=_normalize_timestamp(timestamp),
        workspace_root=result.workspace_root,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        active_profile=result.resolved_profile.name,
        runtime_path=result.runtime_path,
        report_path=result.report_path,
        manifest_path=result.manifest_path,
    )
""",
    encoding="utf-8",
)

test_path = project_root / "tests" / "test_report_metadata_model.py"
test_path.parent.mkdir(parents=True, exist_ok=True)
test_path.write_text(
    """from __future__ import annotations

from datetime import datetime
from pathlib import Path

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.metadata import ReportHeaderMetadata, build_report_header_metadata


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
        timestamp=datetime(2026, 3, 31, 12, 30, 0),
    )

    assert metadata == ReportHeaderMetadata(
        patch_name="metadata_demo",
        timestamp="2026-03-31 12:30:00",
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=tmp_path / "target_project",
        active_profile="generic_python",
        runtime_path=tmp_path / ".venv" / "Scripts" / "python.exe",
        report_path=tmp_path / "metadata_demo_report.txt",
        manifest_path=tmp_path / "manifest.json",
    )


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

    assert metadata.timestamp is None
    assert metadata.workspace_root is None
    assert metadata.runtime_path is None
    assert metadata.manifest_identity == str(result.manifest_path)
""",
    encoding="utf-8",
)

print(str(metadata_path))
print(str(test_path))