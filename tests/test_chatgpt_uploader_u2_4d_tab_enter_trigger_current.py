from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.upload_trigger import (
    UploadTriggerRun,
    default_trigger_safety_flags,
    write_upload_trigger_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_tab_enter_and_neutral_click_flags_are_recorded() -> None:
    flags = default_trigger_safety_flags(picker_open_attempted=True, tab_enter_attempted=True, neutral_click_attempted=True)
    assert flags["upload_trigger_attempted"] is True
    assert flags["file_picker_open_attempted"] is True
    assert flags["tab_enter_attempted"] is True
    assert flags["neutral_click_attempted"] is True
    assert flags["random_page_click_performed"] is False
    assert flags["file_path_written"] is False
    assert flags["open_button_pressed"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_trigger_evidence_keeps_old_spacing_and_new_flags(tmp_path) -> None:
    run = UploadTriggerRun(
        status="FAIL_OR_BLOCKED",
        attempts_requested=1,
        attempts_completed=1,
        pass_count=0,
        attempts=[
            {
                "index": 1,
                "status": "FAIL_PICKER_NOT_DETECTED",
                "trigger_backend": "neutral_click_tab_enter",
                "tab_enter_attempted": True,
                "neutral_click_attempted": True,
                "safety_flags": default_trigger_safety_flags(picker_open_attempted=True, tab_enter_attempted=True, neutral_click_attempted=True),
            }
        ],
        safety_flags=default_trigger_safety_flags(picker_open_attempted=True, tab_enter_attempted=True, neutral_click_attempted=True),
        created_at="2026-01-01T00:00:00Z",
    )
    json_path, txt_path = write_upload_trigger_evidence(run, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["safety_flags"]["tab_enter_attempted"] is True
    assert payload["safety_flags"]["neutral_click_attempted"] is True
    text = txt_path.read_text(encoding="utf-8")
    assert "OpenButtonPressed      : false" in text
    assert "KeyboardShortcutAttempt : false" in text
    assert "TabEnterAttempted      : true" in text
    assert "NeutralClickAttempted  : true" in text
    assert "BackendCounts" in text
    assert "StatusCounts" in text


def test_open_picker_script_dry_run_accepts_tab_enter_flags_without_opening(tmp_path) -> None:
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
            "--allow-tab-enter-sequence",
            "--allow-neutral-click",
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
    assert "TAB_ENTER_ATTEMPTED: false" in result.stdout
    assert "NEUTRAL_CLICK_ATTEMPTED: false" in result.stdout
    assert "OPEN_BUTTON_PRESSED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
