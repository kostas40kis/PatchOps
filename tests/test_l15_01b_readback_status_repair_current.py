from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_live_open_proof as l15_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-open-proof"


def test_l15_01_default_readback_status_is_pass_but_launch_execution_stays_false() -> None:
    payload = l15_01.build_edge_live_open_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["execution_mode"] == "readback_only"
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_process_launch_authorized"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["send_or_submit_performed"] is False


def test_l15_01_cli_default_readback_status_is_pass_and_non_executing() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["execution_mode"] == "readback_only"
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["send_or_submit_performed"] is False


def test_l15_01_brief_validator_uses_readback_pass_contract() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/patch_l15_01_brief_validate.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["readback_status"] == "PASS"
    assert payload["readback_ok"] is True
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
