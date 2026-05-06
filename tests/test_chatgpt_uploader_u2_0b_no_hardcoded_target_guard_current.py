from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config
from patchops.chatgpt_uploader.preflight_policy import decide_launch_permission

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/11111111-2222-3333-4444-555555555555"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_operator_set_blocks_launch_even_when_launch_flag_requested() -> None:
    decision = decide_launch_permission(
        target_mode="operator_set",
        allow_launch_target_requested=True,
        allow_open_configured_url_requested=True,
    )
    assert decision.allow_launch is False
    assert decision.reason == "operator_set_mode_is_focus_only"


def test_launch_target_requires_second_explicit_open_url_gate() -> None:
    blocked = decide_launch_permission(
        target_mode="launch_target",
        allow_launch_target_requested=True,
        allow_open_configured_url_requested=False,
    )
    assert blocked.allow_launch is False
    assert blocked.reason == "opening_configured_url_requires_explicit_allow_open_configured_url"

    allowed = decide_launch_permission(
        target_mode="launch_target",
        allow_launch_target_requested=True,
        allow_open_configured_url_requested=True,
    )
    assert allowed.allow_launch is True
    assert allowed.reason == "launch_target_explicitly_allowed"


def test_preflight_config_only_records_launch_policy_without_opening(tmp_path) -> None:
    config_path = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence"
    write_config(ChatGPTUploaderConfig.create(TARGET_URL, mode="operator_set"), config_path)

    result = subprocess.run(
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
            "--allow-launch-target",
            "--allow-open-configured-url",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS_CONFIG_ONLY" in result.stdout
    assert "LAUNCH_ALLOWED: false" in result.stdout
    assert "LAUNCH_POLICY_REASON: operator_set_mode_is_focus_only" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["launch_policy"]["allow_launch"] is False
    assert payload["launch_policy"]["reason"] == "operator_set_mode_is_focus_only"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert payload["safety_flags"]["selenium_used"] is False
    assert payload["safety_flags"]["webdriver_used"] is False


def test_show_target_never_prints_raw_url(tmp_path) -> None:
    config_path = tmp_path / "target.json"
    write_config(ChatGPTUploaderConfig.create(TARGET_URL, mode="operator_set"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "show_chatgpt_copilot_target.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "TARGET_CONFIG_STATUS: OK" in result.stdout
    assert "RAW_TARGET_URL_PRINTED: false" in result.stdout
    assert TARGET_URL not in result.stdout
    assert "11111111-2222-3333-4444-555555555555" not in result.stdout
