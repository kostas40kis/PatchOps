from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7c_delegate_command_passes_live_picker_permission(tmp_path: Path) -> None:
    from scripts.run_uploader_existing_target_preferred_live import build_delegate_command

    cmd = build_delegate_command(
        repo_root=PROJECT_ROOT,
        report_path=tmp_path / "report.txt",
        evidence_dir=tmp_path / "evidence",
        timeout_seconds=120,
        allow_live_picker=True,
    )

    assert "--allow-live-picker" in cmd
    assert "--report-path" in cmd
    assert "--evidence-dir" in cmd


def test_u2_7c_delegate_without_live_permission_stays_dry_run_blocked(tmp_path: Path) -> None:
    report_path = tmp_path / "report.txt"
    evidence_dir = tmp_path / "evidence"
    report_path.write_text("body\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_recover_upload_verify_attachment_no_send.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(report_path),
            "--evidence-dir",
            str(evidence_dir),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "UPLOAD_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "CANONICAL_TRIGGER_ATTEMPTED: false" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["failure_layer"] == "live_picker_permission_missing"
    assert payload["canonical_trigger_attempted"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False


def test_u2_7c_delegate_accepts_live_permission_flag_without_send_on_missing_report(tmp_path: Path) -> None:
    missing_report = tmp_path / "missing.txt"
    evidence_dir = tmp_path / "evidence"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_recover_upload_verify_attachment_no_send.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--report-path",
            str(missing_report),
            "--evidence-dir",
            str(evidence_dir),
            "--allow-live-picker",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "UPLOAD_STATUS: BLOCKED_REPORT_UNAVAILABLE" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
    assert "SELENIUM_USED: false" in result.stdout
    assert "WEBDRIVER_USED: false" in result.stdout
    assert "BROWSER_DOM_AUTOMATION_USED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["failure_layer"] == "report_unavailable"
    assert payload["chatgpt_submit_performed"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
