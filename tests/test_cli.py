from pathlib import Path

import patchops.cli as cli
from patchops.models import Manifest, ResolvedProfile, WorkflowResult


def _build_result(tmp_path: Path, mode: str, exit_code: int = 0, result_label: str = "PASS") -> WorkflowResult:
    return WorkflowResult(
        mode=mode,
        manifest_path=tmp_path / "manifest.json",
        manifest=Manifest(
            manifest_version="1",
            patch_name=f"{mode}_demo",
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
        backup_root=tmp_path / "backup_root",
        report_path=tmp_path / f"{mode}_report.txt",
        backup_records=[],
        write_records=[],
        validation_results=[],
        smoke_results=[],
        audit_results=[],
        cleanup_results=[],
        archive_results=[],
        failure=None,
        exit_code=exit_code,
        result_label=result_label,
    )


def test_apply_command_prints_labeled_console_summary(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "apply_manifest", lambda manifest, wrapper_project_root=None: _build_result(tmp_path, "apply"))

    exit_code = cli.main(["apply", "example.json"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "PATCHOPS RUN SUMMARY" in output
    assert "Mode               : apply" in output
    assert "Patch Name         : apply_demo" in output
    assert "Active Profile     : generic_python" in output
    assert f"Target Project Root: {tmp_path / 'target_project'}" in output
    assert f"Report Path        : {tmp_path / 'apply_report.txt'}" in output
    assert "ExitCode           : 0" in output
    assert "Result             : PASS" in output


def test_verify_command_prints_labeled_console_summary(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "verify_only", lambda manifest, wrapper_project_root=None: _build_result(tmp_path, "verify_only", exit_code=3, result_label="FAIL"))

    exit_code = cli.main(["verify", "example.json"])

    output = capsys.readouterr().out
    assert exit_code == 3
    assert "PATCHOPS RUN SUMMARY" in output
    assert "Mode               : verify_only" in output
    assert "Patch Name         : verify_only_demo" in output
    assert "ExitCode           : 3" in output
    assert "Result             : FAIL" in output


def test_wrapper_retry_command_prints_labeled_console_summary(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "execute_wrapper_only_retry",
        lambda manifest, wrapper_project_root=None, reason=None: _build_result(
            tmp_path,
            "wrapper_only_retry",
            exit_code=0,
            result_label="PASS",
        ),
    )

    exit_code = cli.main(
        [
            "wrapper-retry",
            "example.json",
            "--retry-reason",
            "report writer failed after validation",
        ]
    )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "PATCHOPS RUN SUMMARY" in output
    assert "Mode               : wrapper_only_retry" in output
    assert "Patch Name         : wrapper_only_retry_demo" in output
    assert "ExitCode           : 0" in output
    assert "Result             : PASS" in output