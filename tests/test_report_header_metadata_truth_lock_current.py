from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.metadata import ReportHeaderMetadata, build_report_header_metadata


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def main() -> int:
    tmp_path = Path.cwd() / "data" / "runtime" / "report_header_metadata_truth_lock_tmp"
    tmp_path.mkdir(parents=True, exist_ok=True)

    result = _build_result(tmp_path)
    metadata = build_report_header_metadata(
        result,
        timestamp=datetime(2026, 4, 8, 17, 30, 0),
    )

    _assert(
        metadata == ReportHeaderMetadata(
            patch_name="metadata_demo",
            timestamp="2026-04-08 17:30:00",
            workspace_root=tmp_path.parent,
            wrapper_project_root=tmp_path,
            target_project_root=tmp_path / "target_project",
            active_profile="generic_python",
            runtime_path=tmp_path / ".venv" / "Scripts" / "python.exe",
            report_path=tmp_path / "metadata_demo_report.txt",
            manifest_path=tmp_path / "manifest.json",
        ),
        "ReportHeaderMetadata equality no longer matches the current header metadata contract.",
    )
    _assert(metadata.manifest_identity == str(tmp_path / "manifest.json"), "manifest_identity drifted")

    result_without_optional = WorkflowResult(
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
    metadata_without_optional = build_report_header_metadata(result_without_optional)
    _assert(metadata_without_optional.patch_name == "metadata_demo", "patch_name missing when optional fields omitted")
    _assert(metadata_without_optional.workspace_root is None, "workspace_root should remain optional")
    _assert(metadata_without_optional.runtime_path is None, "runtime_path should remain optional")
    _assert(metadata_without_optional.report_path == tmp_path / "metadata_demo_report.txt", "report_path drifted")
    _assert(metadata_without_optional.manifest_path == tmp_path / "manifest.json", "manifest_path drifted")

    print("report-header-metadata truth-lock validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
