from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.upload_trigger import default_trigger_safety_flags, score_menu_candidate, score_plus_candidate, write_upload_trigger_evidence, UploadTriggerRun

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_plus_candidate_scoring_prefers_composer_plus() -> None:
    score, reason = score_plus_candidate(name="Add", automation_id="composer-plus-btn", control_type="Button", class_name="Button")
    assert score >= 90
    assert "positive_automation_id" in reason


def test_plus_candidate_rejects_send() -> None:
    score, reason = score_plus_candidate(name="Send message", automation_id="send-button", control_type="Button", class_name="Button")
    assert score < 0
    assert reason == "rejected_by_name"


def test_menu_candidate_scoring_prefers_add_photos_files() -> None:
    score, reason = score_menu_candidate(name="Add photos & files", automation_id="", control_type="MenuItem", class_name="")
    assert score >= 80
    assert "positive_menu_name" in reason


def test_menu_candidate_rejects_drive_connectors() -> None:
    score, reason = score_menu_candidate(name="Connect Google Drive", automation_id="", control_type="MenuItem", class_name="")
    assert score < 0
    assert reason == "rejected_by_name"


def test_trigger_safety_flags_no_path_no_open_no_send() -> None:
    flags = default_trigger_safety_flags(picker_open_attempted=True)
    assert flags["file_picker_open_attempted"] is True
    assert flags["file_path_written"] is False
    assert flags["file_selected"] is False
    assert flags["open_button_pressed"] is False
    assert flags["attachment_confirmed"] is False
    assert flags["chatgpt_submit_performed"] is False
    assert flags["selenium_used"] is False
    assert flags["webdriver_used"] is False
    assert flags["browser_dom_automation_used"] is False


def test_write_upload_trigger_evidence(tmp_path) -> None:
    run = UploadTriggerRun(
        status="PASS_DRY_RUN_NO_PICKER_OPEN",
        attempts_requested=5,
        attempts_completed=0,
        pass_count=0,
        attempts=[],
        safety_flags=default_trigger_safety_flags(picker_open_attempted=False),
        created_at="2026-01-01T00:00:00Z",
    )
    json_path, txt_path = write_upload_trigger_evidence(run, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_DRY_RUN_NO_PICKER_OPEN"
    assert payload["safety_flags"]["file_picker_open_attempted"] is False
    text = txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER UPLOAD TRIGGER" in text
    assert "OpenButtonPressed      : false" in text


def test_open_picker_script_dry_run_does_not_open_picker(tmp_path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_open_picker_live.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--attempts",
            "1",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_OPEN_PICKER_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "FILE_PICKER_OPEN_ATTEMPTED: false" in result.stdout
    assert "FILE_SELECTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
