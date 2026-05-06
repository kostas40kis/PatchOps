from __future__ import annotations

import json
from pathlib import Path

import pytest

from patchops.copilot_downloader.copied_script_bounded_runner import (
    BLOCKED_RUN_NOT_AUTHORIZED,
    FAIL_PATCHOPS_RUN,
    PASS_PATCHOPS_RUN_COMPLETED,
    run_copied_script_bounded_runner,
    validate_run_authorization,
    write_authorized_test_script,
)
from patchops.copilot_downloader.copied_script_static_validator import safe_patchops_script_sample
from patchops.copilot_downloader.script_run_gate import write_sample_staged_script


def _has_powershell() -> bool:
    import shutil

    return shutil.which("powershell.exe") is not None or shutil.which("pwsh") is not None


def test_runner_blocks_without_staged_script_and_does_not_execute(tmp_path: Path):
    result = run_copied_script_bounded_runner(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["issue"] == "staged_script_path_required"
    assert result["run_result"] is None
    assert result["checks"]["run_not_started_without_authorization"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["desktop_report_path"]).is_file()


def test_runner_blocks_without_authorization_metadata(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path = write_sample_staged_script(repo_root)
    result = run_copied_script_bounded_runner(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_script_path=script_path)
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["issue"] in {"run_authorization_required", "allow_execute_required"}
    assert result["run_result"] is None
    assert result["safety"]["artifact_executed"] is False


def test_validate_run_authorization_blocks_hash_mismatch(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root)
    script_path.write_text(safe_patchops_script_sample() + "\n# changed\n", encoding="utf-8")
    ok, issues, _authorization, resolved = validate_run_authorization(script_path, auth_path)
    assert ok is False
    assert resolved == auth_path.resolve(strict=False)
    assert any("sha256" in issue for issue in issues)


def test_runner_blocks_when_allow_execute_missing_even_with_authorization(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root)
    result = run_copied_script_bounded_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        authorization_path=auth_path,
        allow_execute=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["issue"] == "allow_execute_required"
    assert result["safety"]["artifact_executed"] is False


@pytest.mark.skipif(not _has_powershell(), reason="PowerShell is required for bounded runner execution tests")
def test_runner_executes_authorized_script_with_timeout_and_captures_outputs(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root, exit_code=0)
    result = run_copied_script_bounded_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        desktop_report_dir=repo_root / "desktop",
        staged_script_path=script_path,
        authorization_path=auth_path,
        allow_execute=True,
        timeout_seconds=30,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_PATCHOPS_RUN_COMPLETED
    assert result["run_result"]["exit_code"] == 0
    assert result["run_result"]["timed_out"] is False
    assert "bounded runner test harness" in result["run_result"]["stdout"].lower()
    assert result["checks"]["stdout_captured"] is True
    assert result["checks"]["stderr_captured"] is True
    assert result["checks"]["exit_code_captured"] is True
    assert result["safety"]["artifact_executed"] is True
    assert result["safety"]["patchops_invoked"] is True
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    assert auth["run_performed"] is True
    assert auth["run_exit_code"] == 0
    assert Path(result["desktop_report_path"]).is_file()


@pytest.mark.skipif(not _has_powershell(), reason="PowerShell is required for bounded runner execution tests")
def test_runner_returns_fail_label_on_nonzero_exit(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root, exit_code=7)
    result = run_copied_script_bounded_runner(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        authorization_path=auth_path,
        allow_execute=True,
        timeout_seconds=30,
    )
    assert result["ok"] is False
    assert result["result_label"] == FAIL_PATCHOPS_RUN
    assert result["run_result"]["exit_code"] == 7
    assert result["safety"]["artifact_executed"] is True


def test_runner_evidence_does_not_log_raw_script_text_when_blocked(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root)
    script_text = script_path.read_text(encoding="utf-8") + "\n# RAW_RUNNER_SENTINEL_D2_05\n"
    script_path.write_text(script_text, encoding="utf-8")
    result = run_copied_script_bounded_runner(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_script_path=script_path, authorization_path=auth_path)
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert "RAW_RUNNER_SENTINEL_D2_05" not in serialized
    assert "RAW_RUNNER_SENTINEL_D2_05" not in evidence_json


def test_authorized_test_script_contains_static_marker_but_does_not_require_temp_patchops_venv(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path, auth_path = write_authorized_test_script(repo_root, exit_code=0)
    text = script_path.read_text(encoding="utf-8")
    assert "patchops.cli check" in text
    assert "# .\\.venv\\Scripts\\python.exe -m patchops.cli check" in text
    assert json.loads(auth_path.read_text(encoding="utf-8"))["test_harness_script"] is True


def test_repository_bounded_runner_doctor_is_controlled_block_without_execution():
    result = run_copied_script_bounded_runner(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d2_05_bounded_runner_test",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["checks"]["authorization_required"] is True
    assert result["checks"]["run_not_started_without_authorization"] is True
    assert result["safety"]["artifact_executed"] is False
    assert result["safety"]["browser_used"] is False
    assert result["safety"]["clipboard_read"] is False