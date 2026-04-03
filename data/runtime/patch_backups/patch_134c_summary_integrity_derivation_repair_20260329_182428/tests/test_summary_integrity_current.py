from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult, Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.renderer import render_workflow_report


def _command(name: str, exit_code: int, phase: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=Path(r"C:\dev\patchops"),
        exit_code=exit_code,
        stdout="",
        stderr="",
        display_command="py -m pytest -q",
        phase=phase,
    )


def _build_result(
    tmp_path: Path,
    *,
    validation_results: list[CommandResult] | None = None,
    smoke_results: list[CommandResult] | None = None,
    exit_code: int = 0,
    result_label: str = "PASS",
) -> WorkflowResult:
    target_root = tmp_path / "target_project"
    target_root.mkdir(parents=True, exist_ok=True)

    return WorkflowResult(
        mode="apply",
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name="patch_133a_summary_integrity_manifest_path_repair",
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
        target_project_root=target_root,
        runtime_path=None,
        backup_root=None,
        report_path=tmp_path / "report.txt",
        backup_records=[],
        write_records=[],
        validation_results=validation_results or [],
        smoke_results=smoke_results or [],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=exit_code,
        result_label=result_label,
    )


def test_summary_cannot_claim_pass_when_required_validation_failed(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "VALIDATION COMMANDS" in report
    assert "NAME    : required_validation" in report
    assert "EXIT    : 4" in report
    assert "ExitCode : 4" in report
    assert "Result   : FAIL" in report


def test_summary_keeps_earlier_required_failure_sticky_after_later_success(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        smoke_results=[_command("later_smoke", 0, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : required_validation" in report
    assert "NAME    : later_smoke" in report
    assert "EXIT    : 4" in report
    assert "ExitCode : 4" in report
    assert "Result   : FAIL" in report