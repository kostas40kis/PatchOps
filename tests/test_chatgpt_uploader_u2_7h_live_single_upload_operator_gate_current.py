from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7h_gate_blocks_multiple_report_paths(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.live_operator_gate import validate_live_single_upload_request

    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("a\n", encoding="utf-8")
    b.write_text("b\n", encoding="utf-8")

    result = validate_live_single_upload_request(
        [a, b],
        allow_live_single_upload=True,
        operator_confirm="UPLOAD_ONE_ATTACHMENT_NO_SEND",
    ).to_payload()

    assert result["live_single_upload_allowed"] is False
    assert result["multi_upload_blocked"] is True
    assert result["report_path_count"] == 2
    assert result["gate_failure_layer"] == "exactly_one_report_required"


def test_u2_7h_gate_blocks_missing_confirmation(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.live_operator_gate import validate_live_single_upload_request

    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")

    result = validate_live_single_upload_request(
        [report],
        allow_live_single_upload=True,
        operator_confirm="wrong",
    ).to_payload()

    assert result["live_single_upload_allowed"] is False
    assert result["operator_confirmation_valid"] is False
    assert result["gate_failure_layer"] == "operator_confirmation_missing_or_invalid"


def test_u2_7h_gate_allows_exactly_one_report_with_exact_confirmation(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.live_operator_gate import validate_live_single_upload_request

    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")

    result = validate_live_single_upload_request(
        [report],
        allow_live_single_upload=True,
        operator_confirm="UPLOAD_ONE_ATTACHMENT_NO_SEND",
    ).to_payload()

    assert result["live_single_upload_allowed"] is True
    assert result["operator_confirmation_valid"] is True
    assert result["report_path_count"] == 1
    assert result["gate_result"] == "PASS_LIVE_SINGLE_UPLOAD_OPERATOR_GATE_OPEN"


def test_u2_7h_script_default_blocks_without_live_flag(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7h_live_single_upload_operator_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7H_STATUS: PASS_OR_BLOCKED" in result.stdout
    assert "LIVE_SINGLE_UPLOAD_ALLOWED: false" in result.stdout
    assert "FAILURE_LAYER: allow_live_single_upload_flag_missing" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["live_single_upload_allowed"] is False
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7h_script_simulate_pass_single_upload_runs_submission_blocker(tmp_path: Path) -> None:
    report = tmp_path / "report.txt"
    report.write_text("body\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_u2_7h_live_single_upload_operator_gate.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report),
            "--evidence-dir",
            str(tmp_path / "evidence_sim"),
            "--allow-live-single-upload",
            "--operator-confirm",
            "UPLOAD_ONE_ATTACHMENT_NO_SEND",
            "--simulate-pass",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7H_STATUS: PASS" in result.stdout
    assert "RESULT: PASS_U2_7H_LIVE_SINGLE_UPLOAD_OPERATOR_GATED_NO_SEND" in result.stdout
    assert "LIVE_SINGLE_UPLOAD_ALLOWED: true" in result.stdout
    assert "QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "SKIPPED_QUEUE_ITEM_COUNT: 0" in result.stdout
    assert "SUBMISSION_BLOCKER_PASSED: true" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["live_single_upload_allowed"] is True
    assert payload["queue_item_count"] == 1
    assert payload["submission_blocker_passed"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
