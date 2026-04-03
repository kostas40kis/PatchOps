from pathlib import Path

from patchops.models import CommandResult, CommandSpec, FileWriteSpec, Manifest, ResolvedProfile, WorkflowResult
from patchops.reporting.renderer import render_workflow_report
from patchops.reporting.sections import display_path
from patchops.workflows.wrapper_retry import active_wrapper_only_retry_context


def _build_result(tmp_path: Path, mode: str, files_to_write: list[FileWriteSpec] | None = None) -> WorkflowResult:
    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name=f"{mode}_demo",
            active_profile="generic_python",
            files_to_write=files_to_write or [],
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
        report_path=tmp_path / f"{mode}_report.txt",
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


def test_report_contains_summary_and_manifest_path(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    text = render_workflow_report(result)
    assert "SUMMARY" in text
    assert "ExitCode : 0" in text
    assert f"Manifest Path        : {display_path(result.manifest_path)}" in text


def test_report_lists_target_files_from_manifest_even_without_writes(tmp_path: Path):
    result = _build_result(
        tmp_path,
        "verify_only",
        files_to_write=[FileWriteSpec(path="example.txt", content="ignored")],
    )
    text = render_workflow_report(result)
    assert display_path(result.target_project_root / "example.txt") in text


def test_wrapper_only_retry_report_contains_explicit_retry_section(tmp_path: Path):
    result = _build_result(
        tmp_path,
        "wrapper_only_retry",
        files_to_write=[FileWriteSpec(path="example.txt", content="ignored")],
    )

    with active_wrapper_only_retry_context(" report writer failed after validation "):
        text = render_workflow_report(result)

    assert "PATCHOPS WRAPPER_ONLY_RETRY" in text
    assert "WRAPPER-ONLY RETRY" in text
    assert "Retry Kind       : wrapper_only_retry" in text
    assert "Retry Reason     : report writer failed after validation" in text
    assert "Writes Skipped   : yes" in text
    assert "Expected Targets : 1" in text
    assert "Existing Targets : 0" in text
    assert "Missing Targets  : 1" in text
    assert "Escalation       : full apply review required" in text


def test_wrapper_only_retry_report_marks_stay_narrow_when_expected_files_exist(tmp_path: Path):
    target_root = tmp_path / "target_project"
    target_root.mkdir(parents=True, exist_ok=True)
    (target_root / "example.txt").write_text("ok", encoding="utf-8")

    result = _build_result(
        tmp_path,
        "wrapper_only_retry",
        files_to_write=[FileWriteSpec(path="example.txt", content="ignored")],
    )

    with active_wrapper_only_retry_context(None):
        text = render_workflow_report(result)

    assert "Retry Reason     : wrapper/reporting failure after likely content success" in text
    assert "Existing Targets : 1" in text
    assert "Missing Targets  : 0" in text
    assert "Escalation       : stay narrow" in text


def test_verify_only_report_does_not_render_wrapper_only_retry_section(tmp_path: Path):
    result = _build_result(tmp_path, "verify_only")
    text = render_workflow_report(result)
    assert "WRAPPER-ONLY RETRY" not in text
    assert "Retry Kind       : wrapper_only_retry" not in text

# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_START
def _command(name: str, exit_code: int, phase: str = "validation") -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=Path("."),
        exit_code=exit_code,
        stdout="",
        stderr="",
        display_command="py -m pytest -q",
        phase=phase,
    )


def _command_spec(name: str, *, allowed_exit_codes: list[int] | None = None) -> CommandSpec:
    return CommandSpec(
        name=name,
        program="py",
        args=["-m", "pytest", "-q"],
        working_directory=".",
        use_profile_runtime=False,
        allowed_exit_codes=list(allowed_exit_codes or [0]),
    )


def test_report_summary_derives_fail_from_required_validation_result(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    result.manifest.validation_commands.append(_command_spec("required_validation"))
    result.validation_results.append(_command("required_validation", 4, "validation"))

    text = render_workflow_report(result)

    assert "NAME    : required_validation" in text
    assert "EXIT    : 4" in text
    assert "ExitCode : 4" in text
    assert "Result   : FAIL" in text


def test_report_summary_respects_allowed_exit_codes_for_validation(tmp_path: Path):
    result = _build_result(tmp_path, "apply")
    result.manifest.validation_commands.append(
        _command_spec("expected_verifier", allowed_exit_codes=[0, 3])
    )
    result.validation_results.append(_command("expected_verifier", 3, "validation"))

    text = render_workflow_report(result)

    assert "NAME    : expected_verifier" in text
    assert "EXIT    : 3" in text
    assert "ExitCode : 0" in text
    assert "Result   : PASS" in text
# PATCHOPS_PATCH134_REPORT_SUMMARY_INTEGRITY_END
