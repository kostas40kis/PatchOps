from __future__ import annotations

from pathlib import Path

import patchops.cli as cli
from patchops.handoff import build_current_handoff_payload, build_latest_report_index_payload, build_next_action_recommendation
from patchops.models import CommandResult, CommandSpec, Manifest, ResolvedProfile, WorkflowResult
from patchops.result_integrity import derive_effective_summary_fields


def _command(name: str, exit_code: int, phase: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest"],
        working_directory=Path("."),
        exit_code=exit_code,
        stdout="",
        stderr="",
        display_command="py -m pytest",
        phase=phase,
    )


def _result(
    tmp_path: Path,
    *,
    mode: str = "apply",
    exit_code: int = 0,
    result_label: str = "PASS",
    validation_results: list[CommandResult] | None = None,
    smoke_results: list[CommandResult] | None = None,
    validation_allowed_exit_codes: list[int] | None = None,
) -> WorkflowResult:
    target_root = tmp_path / "target_project"
    target_root.mkdir(parents=True, exist_ok=True)
    report_path = tmp_path / f"{mode}_report.txt"
    report_path.write_text("placeholder\n", encoding="utf-8")

    manifest = Manifest(
        manifest_version="1",
        patch_name=f"{mode}_demo",
        active_profile="generic_python",
        files_to_write=[],
        validation_commands=[
            CommandSpec(
                name="required_validation",
                program="py",
                args=["-m", "pytest"],
                allowed_exit_codes=validation_allowed_exit_codes or [0],
            )
        ] if validation_results else [],
        smoke_commands=[
            CommandSpec(
                name="required_smoke",
                program="py",
                args=["-m", "pytest"],
                allowed_exit_codes=[0],
            )
        ] if smoke_results else [],
    )

    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=manifest,
        resolved_profile=ResolvedProfile(
            name="generic_python",
            default_target_root=None,
            runtime_path=None,
        ),
        workspace_root=tmp_path.parent,
        wrapper_project_root=tmp_path,
        target_project_root=target_root,
        runtime_path=None,
        backup_root=tmp_path / "backup_root",
        report_path=report_path,
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


def test_helper_derives_fail_from_required_validation_even_if_workflow_result_is_pass(tmp_path: Path) -> None:
    result = _result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    effective = derive_effective_summary_fields(result)

    assert effective["exit_code"] == 4
    assert effective["result_label"] == "FAIL"
    assert effective["source"] == "required_command_failure"


def test_helper_preserves_tolerated_nonzero_exit(tmp_path: Path) -> None:
    result = _result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        validation_allowed_exit_codes=[0, 4],
        exit_code=0,
        result_label="PASS",
    )

    effective = derive_effective_summary_fields(result)

    assert effective["exit_code"] == 0
    assert effective["result_label"] == "PASS"


def test_cli_summary_and_return_code_use_effective_summary_fields(tmp_path: Path, monkeypatch, capsys) -> None:
    result = _result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    monkeypatch.setattr(cli, "apply_manifest", lambda manifest, wrapper_project_root=None: result)

    exit_code = cli.main(["apply", "example.json"])

    output = capsys.readouterr().out
    assert exit_code == 4
    assert "PATCHOPS RUN SUMMARY" in output
    assert "ExitCode           : 4" in output
    assert "Result             : FAIL" in output


def test_handoff_surfaces_fail_closed_when_required_command_evidence_failed(tmp_path: Path) -> None:
    result = _result(
        tmp_path,
        validation_results=[_command("required_validation", 4, "validation")],
        exit_code=0,
        result_label="PASS",
    )

    recommendation = build_next_action_recommendation(result)
    current_payload = build_current_handoff_payload(result)
    latest_index = build_latest_report_index_payload(result)

    assert recommendation["recommended_mode"] == "repair_patch"
    assert "required validation or smoke evidence failed" in recommendation["rationale"].lower()
    assert current_payload["repo_state"]["current_status"] == "fail"
    assert current_payload["latest_patch"]["latest_passed_patch"] == "unknown from this run"
    assert current_payload["repo_state"]["failure_class"] == "target_project_failure"
    assert latest_index["current_status"] == "fail"
    assert latest_index["failure_class"] == "target_project_failure"
