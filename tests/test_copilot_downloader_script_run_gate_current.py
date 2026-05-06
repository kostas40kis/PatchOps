from __future__ import annotations

import json
from pathlib import Path

from patchops.copilot_downloader.copied_script_static_validator import BLOCKED_INVALID_SCRIPT, PASS_SCRIPT_VALIDATED_RUN_BLOCKED, safe_patchops_script_sample
from patchops.copilot_downloader.script_payload_contract import REQUIRED_CONFIRMATION
from patchops.copilot_downloader.script_run_gate import (
    BLOCKED_RUN_NOT_AUTHORIZED,
    PASS_SCRIPT_RUN_AUTHORIZED,
    run_script_explicit_run_gate,
    write_sample_staged_script,
)


def _write_staged_script(repo_root: Path, script_text: str | None = None) -> Path:
    stage_dir = repo_root / "data" / "runtime" / "copilot_downloader" / "copied_scripts" / "staged" / "manual"
    stage_dir.mkdir(parents=True, exist_ok=True)
    script_path = stage_dir / "extracted_script.ps1"
    script_path.write_text(script_text or safe_patchops_script_sample(), encoding="utf-8")
    return script_path


def test_run_gate_default_doctor_uses_sample_and_blocks_without_authorization(tmp_path: Path):
    result = run_script_explicit_run_gate(repo_root=tmp_path, evidence_root=tmp_path / "evidence")
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["issue"] == "allow_run_required"
    assert result["used_sample_staged_script"] is True
    assert result["authorization_state"]["authorized"] is False
    assert result["authorization_path"] is None
    assert result["checks"]["run_not_authorized_unless_validated_and_confirmed"] is True
    assert result["checks"]["script_not_executed"] is True
    assert result["safety"]["artifact_executed"] is False
    assert Path(result["evidence_files"]["json"]).is_file()


def test_run_gate_requires_existing_staged_script_when_sample_disabled_controlled_block(tmp_path: Path):
    result = run_script_explicit_run_gate(
        repo_root=tmp_path,
        evidence_root=tmp_path / "evidence",
        allow_sample_when_missing=False,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_INVALID_SCRIPT
    assert result["issue"] == "staged_validated_script_required"
    assert result["authorization_state"]["authorized"] is False
    assert result["checks"]["staged_script_required_or_controlled_block"] is True
    assert result["checks"]["no_staged_script_never_authorized"] is True


def test_run_gate_valid_staged_script_without_allow_run_stops_before_run(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path = _write_staged_script(repo_root)
    result = run_script_explicit_run_gate(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["validation_result"]["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["authorization_state"]["authorized"] is False
    assert result["checks"]["script_not_executed"] is True
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True


def test_run_gate_allow_run_with_wrong_confirmation_blocks_authorization(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path = _write_staged_script(repo_root)
    result = run_script_explicit_run_gate(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        allow_run=True,
        confirm_run_text="WRONG_CONFIRM",
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_RUN_NOT_AUTHORIZED
    assert result["issue"] == "confirm_run_text_required"
    assert result["confirm_run_text_matched"] is False
    assert result["authorization_path"] is None
    assert result["authorization_state"]["authorized"] is False
    assert result["checks"]["run_not_authorized_unless_validated_and_confirmed"] is True


def test_run_gate_authorizes_only_after_allow_run_confirmation_and_validation(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_path = _write_staged_script(repo_root)
    result = run_script_explicit_run_gate(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_RUN_AUTHORIZED
    assert result["authorization_state"]["authorized"] is True
    assert result["authorization_state"]["run_performed"] is False
    assert result["authorization_state"]["bounded_runner_required_next"] is True
    assert result["checks"]["authorization_metadata_written_when_authorized"] is True
    assert result["checks"]["script_not_executed"] is True
    auth_path = Path(result["authorization_path"])
    assert auth_path.is_file()
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    assert auth["authorized"] is True
    assert auth["run_performed"] is False
    assert auth["patchops_invoked"] is False


def test_run_gate_blocks_invalid_staged_script_even_with_confirmation_controlled_block(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    bad_script = safe_patchops_script_sample() + "\nInvoke-Expression $payload\n"
    script_path = _write_staged_script(repo_root, bad_script)
    result = run_script_explicit_run_gate(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
    )
    assert result["ok"] is True
    assert result["result_label"] == BLOCKED_INVALID_SCRIPT
    assert result["issue"] == "staged_script_static_validation_failed"
    assert result["authorization_state"]["authorized"] is False
    assert result["authorization_path"] is None
    assert result["checks"]["invalid_script_not_authorized"] is True
    assert result["checks"]["invalid_script_with_confirmation_still_not_authorized"] is True
    assert result["checks"]["run_not_authorized_unless_validated_and_confirmed"] is True


def test_run_gate_evidence_does_not_log_raw_script_text(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    script_text = safe_patchops_script_sample() + "\n# RAW_SCRIPT_SENTINEL_D2_04\n"
    script_path = _write_staged_script(repo_root, script_text)
    result = run_script_explicit_run_gate(
        repo_root=repo_root,
        evidence_root=repo_root / "evidence",
        staged_script_path=script_path,
        allow_run=True,
        confirm_run_text=REQUIRED_CONFIRMATION,
    )
    serialized = json.dumps(result)
    evidence_json = Path(result["evidence_files"]["json"]).read_text(encoding="utf-8")
    assert "RAW_SCRIPT_SENTINEL_D2_04" not in serialized
    assert "RAW_SCRIPT_SENTINEL_D2_04" not in evidence_json
    assert "patchops.cli check" not in evidence_json


def test_write_sample_staged_script_creates_static_valid_sample(tmp_path: Path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    path = write_sample_staged_script(repo_root)
    assert path.is_file()
    result = run_script_explicit_run_gate(repo_root=repo_root, evidence_root=repo_root / "evidence", staged_script_path=path)
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["used_sample_staged_script"] is False


def test_repository_script_run_gate_doctor_is_green_without_clipboard_browser_or_execution():
    result = run_script_explicit_run_gate(
        repo_root=Path.cwd(),
        evidence_root="data/runtime/copilot_downloader/d2_04_script_run_gate_test",
    )
    assert result["ok"] is True
    assert result["result_label"] == PASS_SCRIPT_VALIDATED_RUN_BLOCKED
    assert result["checks"]["clipboard_not_read"] is True
    assert result["checks"]["browser_not_used"] is True
    assert result["checks"]["script_not_executed"] is True
    assert result["checks"]["patchops_not_invoked_by_downloader_runtime"] is True
    assert result["safety"]["artifact_executed"] is False