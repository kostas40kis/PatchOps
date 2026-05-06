from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.edge_target import SAFE_EDGE_PREFLIGHT_CAPABILITIES

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def test_scripts_config_then_config_only_preflight(tmp_path) -> None:
    config_path = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence"

    set_result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            TARGET_URL,
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert set_result.returncode == 0, set_result.stderr
    assert config_path.exists()
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in set_result.stdout
    assert "TARGET_URL_SHA256:" in set_result.stdout

    preflight_result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--evidence-dir",
            str(evidence_dir),
            "--no-real-edge",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert preflight_result.returncode == 0, preflight_result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS_CONFIG_ONLY" in preflight_result.stdout
    json_line = next(line for line in preflight_result.stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    evidence_path = Path(json_line.split(":", 1)[1].strip())
    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_CONFIG_ONLY"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert payload["safety_flags"]["selenium_used"] is False
    assert payload["safety_flags"]["webdriver_used"] is False


def test_edge_preflight_capability_constants_stay_safe() -> None:
    assert SAFE_EDGE_PREFLIGHT_CAPABILITIES["selenium_used"] is False
    assert SAFE_EDGE_PREFLIGHT_CAPABILITIES["webdriver_used"] is False
    assert SAFE_EDGE_PREFLIGHT_CAPABILITIES["browser_dom_automation_used"] is False
    assert SAFE_EDGE_PREFLIGHT_CAPABILITIES["file_upload_attempted"] is False
    assert SAFE_EDGE_PREFLIGHT_CAPABILITIES["chatgpt_submit_performed"] is False
