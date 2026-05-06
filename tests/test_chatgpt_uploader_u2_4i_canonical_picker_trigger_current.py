from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.canonical_picker_trigger import (
    CANONICAL_FORBIDDEN_TRIGGER_BACKENDS,
    CANONICAL_PICKER_TRIGGER_NAME,
    CANONICAL_PICKER_TRIGGER_SEQUENCE,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_canonical_trigger_contract_names_only_slash_enter_path() -> None:
    assert CANONICAL_PICKER_TRIGGER_NAME == "safe_click_slash_enter_once"
    assert CANONICAL_PICKER_TRIGGER_SEQUENCE == (
        "focus_edge",
        "safe_click_once",
        "slash_once",
        "enter_once",
        "detect_picker",
    )
    assert "tab" in CANONICAL_FORBIDDEN_TRIGGER_BACKENDS
    assert "second_enter" in CANONICAL_FORBIDDEN_TRIGGER_BACKENDS
    assert "plus_control_search" in CANONICAL_FORBIDDEN_TRIGGER_BACKENDS
    assert "menu_control_search" in CANONICAL_FORBIDDEN_TRIGGER_BACKENDS
    assert "ctrl_u" in CANONICAL_FORBIDDEN_TRIGGER_BACKENDS


def test_canonical_script_dry_run_uses_one_attempt_and_no_fallbacks(tmp_path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_open_picker_canonical.py"),
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
    assert "PATCHOPS_UPLOADER_CANONICAL_PICKER_STATUS: PASS_DRY_RUN_NO_PICKER_OPEN" in result.stdout
    assert "CANONICAL_PICKER_TRIGGER: safe_click_slash_enter_once" in result.stdout
    assert "CANONICAL_ATTEMPTS: 1" in result.stdout
    assert "TAB_SENT: false" in result.stdout
    assert "SECOND_ENTER_ATTEMPTED: false" in result.stdout
    assert "PLUS_CONTROL_SEARCH_ATTEMPTED: false" in result.stdout
    assert "MENU_CONTROL_SEARCH_ATTEMPTED: false" in result.stdout
    assert "CTRL_U_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout
