from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader import upload_trigger
from patchops.chatgpt_uploader.upload_trigger import run_open_picker_attempts

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_missing_pywinauto_blocks_before_picker_open(monkeypatch) -> None:
    monkeypatch.setattr(upload_trigger, "pywinauto_available", lambda: False)
    run = run_open_picker_attempts(target_config_path=Path("missing.json"), attempts=5, allow_open_picker=True)
    assert run.status == "BLOCKED_MISSING_PYWINAUTO"
    assert run.attempts_requested == 5
    assert run.attempts_completed == 0
    assert run.pass_count == 0
    assert run.safety_flags["file_picker_open_attempted"] is False
    assert run.safety_flags["file_path_written"] is False
    assert run.safety_flags["file_selected"] is False
    assert run.safety_flags["open_button_pressed"] is False
    assert run.safety_flags["chatgpt_submit_performed"] is False
    assert run.attempts[0]["status"] == "BLOCKED_MISSING_PYWINAUTO"


def test_dry_run_still_does_not_require_pywinauto(monkeypatch) -> None:
    monkeypatch.setattr(upload_trigger, "pywinauto_available", lambda: False)
    run = run_open_picker_attempts(target_config_path=Path("missing.json"), attempts=1, allow_open_picker=False)
    assert run.status == "PASS_DRY_RUN_NO_PICKER_OPEN"
    assert run.safety_flags["file_picker_open_attempted"] is False


def test_open_picker_script_missing_pywinauto_returns_controlled_exit(monkeypatch, tmp_path) -> None:
    # This is a subprocess smoke of the script shape. It may return PASS if pywinauto happens to be installed,
    # or controlled exit 2 if unavailable, but it must not print a traceback and safety flags must be present.
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
            "--allow-open-picker",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode in {0, 2}
    assert "Traceback" not in result.stderr
    assert "PATCHOPS_UPLOADER_OPEN_PICKER_STATUS:" in result.stdout
    assert "FILE_PATH_WRITTEN: false" in result.stdout
    assert "OPEN_BUTTON_PRESSED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
