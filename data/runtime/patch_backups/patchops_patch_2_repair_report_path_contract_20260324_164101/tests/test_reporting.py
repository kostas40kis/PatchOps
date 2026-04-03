from pathlib import Path

from patchops.models import FileWriteSpec, Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.renderer import render_workflow_report


def test_report_contains_summary_and_manifest_path():
    result = WorkflowResult(
        mode="apply",
        manifest_path=Path("/wrapper/examples/example.json"),
        manifest=Manifest(
            manifest_version="1",
            patch_name="x",
            active_profile="generic_python",
            files_to_write=[],
        ),
        resolved_profile=ResolvedProfile(name="generic_python", default_target_root=None, runtime_path=None),
        workspace_root=None,
        wrapper_project_root=Path("/wrapper"),
        target_project_root=Path("/target"),
        runtime_path=None,
        backup_root=None,
        report_path=Path("/report.txt"),
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
    text = render_workflow_report(result)
    assert "SUMMARY" in text
    assert "ExitCode : 0" in text
    assert "Manifest Path        : /wrapper/examples/example.json" in text


def test_report_lists_target_files_from_manifest_even_without_writes():
    result = WorkflowResult(
        mode="verify_only",
        manifest_path=Path("/wrapper/examples/verify.json"),
        manifest=Manifest(
            manifest_version="1",
            patch_name="verify",
            active_profile="generic_python",
            files_to_write=[
                FileWriteSpec(path="example.txt", content="ignored"),
            ],
        ),
        resolved_profile=ResolvedProfile(name="generic_python", default_target_root=None, runtime_path=None),
        workspace_root=None,
        wrapper_project_root=Path("/wrapper"),
        target_project_root=Path("/target"),
        runtime_path=None,
        backup_root=None,
        report_path=Path("/report.txt"),
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
    text = render_workflow_report(result)
    assert "/target/example.txt" in text