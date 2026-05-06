from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.slash_enter_trigger import slash_enter_safety_flags

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_slash_enter_safety_flags_forbid_tab_and_second_enter() -> None:
    flags = slash_enter_safety_flags(open_attempted=True, safe_click_attempted=True, slash_sent=True)
    assert flags["file_picker_open_attempted"] is True
    assert flags["safe_click_attempted"] is True
    assert flags["slash_sent"] is True
    assert flags["tab_sent"] is False
    assert flags["second_enter_attempted"] is False
    assert flags["plus_control_search_attempted"] is False
    assert flags["menu_control_search_attempted"] is False
    assert flags["ctrl_u_attempted"] is False
    assert flags["open_button_pressed"] is False
    assert flags["chatgpt_submit_performed"] is False


def test_slash_enter_script_dry_run_has_expected_flags(tmp_path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_open_picker_slash_enter.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_SLASH_ENTER_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "FILE_PICKER_OPEN_ATTEMPTED: false" in result.stdout
    assert "SLASH_SENT: false" in result.stdout
    assert "TAB_SENT: false" in result.stdout
    assert "SECOND_ENTER_ATTEMPTED: false" in result.stdout
    assert "OPEN_BUTTON_PRESSED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
