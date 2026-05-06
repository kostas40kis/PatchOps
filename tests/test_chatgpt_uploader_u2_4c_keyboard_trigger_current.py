from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.upload_trigger import (
    UploadTriggerRun,
    default_trigger_safety_flags,
    score_menu_candidate,
    score_plus_candidate,
    write_upload_trigger_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_keyboard_shortcut_flag_is_recorded_in_safety_flags() -> None:
    flags = default_trigger_safety_flags(picker_open_attempted=True, keyboard_shortcut_attempted=True)
    assert flags["upload_trigger_attempted"] is True
    assert flags["file_picker_open_attempted"] is True
    assert flags["keyboard_shortcut_attempted"] is True
    assert flags["file_path_written"] is False
    assert flags["open_button_pressed"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_scoring_still_rejects_send_and_accepts_uploadish_controls() -> None:
    score, reason = score_plus_candidate(name="Attach files", automation_id="composer-plus-btn", control_type="Button", class_name="Button")
    assert score >= 90
    assert "positive_automation_id" in reason
    bad_score, bad_reason = score_plus_candidate(name="Send message", automation_id="send-button", control_type="Button", class_name="Button")
    assert bad_score < 0
    assert bad_reason == "rejected_by_name"


def test_menu_scoring_accepts_upload_file_wording() -> None:
    score, reason = score_menu_candidate(name="Upload file", automation_id="", control_type="MenuItem", class_name="")
    assert score >= 80
    assert "positive_menu_name" in reason


def test_trigger_evidence_includes_backend_and_status_counts(tmp_path) -> None:
    run = UploadTriggerRun(
        status="FAIL_OR_BLOCKED",
        attempts_requested=1,
        attempts_completed=1,
        pass_count=0,
        attempts=[
            {
                "index": 1,
                "status": "FAIL_PICKER_NOT_DETECTED",
                "trigger_backend": "keyboard_shortcut",
                "safety_flags": default_trigger_safety_flags(picker_open_attempted=True, keyboard_shortcut_attempted=True),
            }
        ],
        safety_flags=default_trigger_safety_flags(picker_open_attempted=True, keyboard_shortcut_attempted=True),
        created_at="2026-01-01T00:00:00Z",
    )
    json_path, txt_path = write_upload_trigger_evidence(run, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["safety_flags"]["keyboard_shortcut_attempted"] is True
    text = txt_path.read_text(encoding="utf-8")
    assert "KeyboardShortcutAttempt : true" in text
    assert "BackendCounts" in text
    assert "StatusCounts" in text


def test_open_picker_script_dry_run_accepts_keyboard_flag_without_opening(tmp_path) -> None:
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
            "--allow-keyboard-shortcut",
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
    assert "KEYBOARD_SHORTCUT_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
