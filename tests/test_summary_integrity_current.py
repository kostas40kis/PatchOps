from pathlib import Path

from patchops.models import CommandResult, CommandSpec, Manifest, ReportPreferences, ResolvedProfile, WorkflowResult
from patchops.reporting.renderer import render_workflow_report


def _command_spec(name: str, allowed_exit_codes: list[int] | None = None) -> CommandSpec:
    return CommandSpec(
        name=name,
        program="py",
        args=["-c", "print('summary integrity test')"],
        working_directory=".",
        use_profile_runtime=False,
        allowed_exit_codes=list(allowed_exit_codes or [0]),
    )


def _command_result(name: str, exit_code: int, phase: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-c", "print('summary integrity test')"],
        working_directory=Path("."),
        exit_code=exit_code,
        stdout="summary integrity test\n",
        stderr="",
        display_command="py -c print('summary integrity test')",
        phase=phase,
    )


def _build_result(
    tmp_path: Path,
    *,
    validation_specs: list[CommandSpec] | None = None,
    validation_results: list[CommandResult] | None = None,
    smoke_specs: list[CommandSpec] | None = None,
    smoke_results: list[CommandResult] | None = None,
    exit_code: int = 0,
    result_label: str = "PASS",
) -> WorkflowResult:
    return WorkflowResult(
        mode="apply",
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name="summary_integrity_current",
            active_profile="generic_python",
            files_to_write=[],
            validation_commands=list(validation_specs or []),
            smoke_commands=list(smoke_specs or []),
            report_preferences=ReportPreferences(write_to_desktop=False),
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
        report_path=tmp_path / "summary_integrity_current.txt",
        backup_records=[],
        write_records=[],
        validation_results=list(validation_results or []),
        smoke_results=list(smoke_results or []),
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
        validation_specs=[_command_spec("required_validation", [0])],
        validation_results=[_command_result("required_validation", 4, "validation")],
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
        validation_specs=[_command_spec("required_validation", [0])],
        validation_results=[_command_result("required_validation", 4, "validation")],
        smoke_specs=[_command_spec("later_smoke", [0])],
        smoke_results=[_command_result("later_smoke", 0, "smoke")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : required_validation" in report
    assert "NAME    : later_smoke" in report
    assert "EXIT    : 4" in report
    assert "ExitCode : 4" in report
    assert "Result   : FAIL" in report


def test_summary_keeps_explicitly_tolerated_non_zero_exit_as_pass(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_specs=[_command_spec("tolerated_validation", [0, 3])],
        validation_results=[_command_result("tolerated_validation", 3, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "NAME    : tolerated_validation" in report
    assert "EXIT    : 3" in report
    assert "ExitCode : 0" in report
    assert "Result   : PASS" in report


def test_summary_preserves_existing_success_when_required_commands_are_clean(tmp_path: Path) -> None:
    result = _build_result(
        tmp_path,
        validation_specs=[_command_spec("validation_ok", [0])],
        validation_results=[_command_result("validation_ok", 0, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    report = render_workflow_report(result)

    assert "ExitCode : 0" in report
    assert "Result   : PASS" in report