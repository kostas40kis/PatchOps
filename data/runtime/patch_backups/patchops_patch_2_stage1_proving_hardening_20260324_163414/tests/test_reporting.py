from pathlib import Path

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.renderer import render_workflow_report


def test_report_contains_summary():
    result = WorkflowResult(
        mode="apply",
        manifest=Manifest(manifest_version="1", patch_name="x", active_profile="generic_python"),
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
