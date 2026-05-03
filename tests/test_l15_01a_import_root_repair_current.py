from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l15_01_brief_validator_direct_script_imports_patchops_from_repo_root() -> None:
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
    assert payload["patch"] == "L15.1"
    assert payload["readback_status"] == "PASS"
    assert payload["readback_ok"] is True
    assert payload["execution_mode"] == "readback_only"
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["selenium_required"] is False
    assert payload["send_or_submit_performed"] is False
