from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.models import Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.continuation import (
    build_failure_continuation_metadata,
    recommended_next_mode_label,
)
from patchops.reporting.renderer import render_workflow_report
from patchops.reporting.sections import failure_section, full_output_section


class _Category:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_build_failure_continuation_metadata_exposes_current_fields() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed after writes already landed",
            details="full output already recorded",
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    metadata = build_failure_continuation_metadata(result)

    assert metadata is not None
    assert metadata.failure_class == "target_project_failure"
    assert metadata.failure_reason == "validation failed after writes already landed"
    assert metadata.recommended_next_mode == "verify_only"
    assert metadata.category_display == "target_project_failure"
    assert metadata.message_display == "validation failed after writes already landed"
    assert metadata.details_display == "full output already recorded"


def test_recommended_next_mode_label_returns_content_repair_when_target_not_already_present() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed before content was proven landed",
            details=None,
        ),
        target_content_already_present=False,
        writes_applied_by_wrapper=False,
    )

    assert recommended_next_mode_label(result) == "content_repair"


def test_failure_section_uses_python_owned_continuation_metadata() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="report capture mismatch",
            details="stdout and stderr drifted",
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "FAILURE DETAILS" in rendered
    assert "Failure Class : wrapper_failure" in rendered
    assert "Failure Reason: report capture mismatch" in rendered
    assert "Recommended Next Mode : wrapper_only_repair" in rendered
    assert "Details  : stdout and stderr drifted" in rendered


def test_full_output_section_returns_none_for_empty_results() -> None:
    rendered = full_output_section([], "SMOKE OUTPUT")
    assert "SMOKE OUTPUT" in rendered
    assert "(none)" in rendered


def test_render_workflow_report_handles_empty_command_groups_without_crashing(tmp_path: Path) -> None:
    result = WorkflowResult(
        mode="apply",
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name="empty_groups_demo",
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
        runtime_path=None,
        backup_root=None,
        report_path=tmp_path / "report.txt",
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

    report = render_workflow_report(result)

    assert "SMOKE OUTPUT" in report
    assert "AUDIT OUTPUT" in report
    assert "CLEANUP OUTPUT" in report
    assert "ARCHIVE OUTPUT" in report
    assert report.count("(none)") >= 4
