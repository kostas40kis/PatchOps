from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOKEN = "UPLOAD_ONE_ATTACHMENT_NO_SEND"


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7ha_script_contains_literal_confirmation_token_for_static_evidence() -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_u2_7h_live_single_upload_operator_gate.py"
    module = PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "live_operator_gate.py"

    script_text = script.read_text(encoding="utf-8")
    module_text = module.read_text(encoding="utf-8")

    assert TOKEN in module_text
    assert TOKEN in script_text
    assert "EXPECTED_OPERATOR_CONFIRMATION_TOKEN" in script_text


def test_u2_7ha_default_blocked_stdout_prints_expected_confirmation_token(tmp_path: Path) -> None:
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
    assert f"EXPECTED_CONFIRMATION_TOKEN: {TOKEN}" in result.stdout
    assert "LIVE_SINGLE_UPLOAD_ALLOWED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["expected_confirmation_token"] == TOKEN
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7ha_simulated_gated_run_still_passes_submission_blocker(tmp_path: Path) -> None:
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
            TOKEN,
            "--simulate-pass",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_U2_7H_STATUS: PASS" in result.stdout
    assert f"EXPECTED_CONFIRMATION_TOKEN: {TOKEN}" in result.stdout
    assert "SUBMISSION_BLOCKER_PASSED: true" in result.stdout
    assert "QUEUE_ITEM_COUNT: 1" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["operator_confirmation_valid"] is True
    assert payload["submission_blocker_passed"] is True
    assert payload["chatgpt_submit_performed"] is False
