from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_1qj_success_payload_uses_launch_policy_object(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config

    config_path = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence"
    write_config(ChatGPTUploaderConfig.create("https://chatgpt.com/", mode="operator_set"), config_path)

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
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS_CONFIG_ONLY" in result.stdout
    assert "LAUNCH_ALLOWED: false" in result.stdout
    assert "LAUNCH_POLICY: no_real_edge" in result.stdout
    assert "LAUNCH_POLICY_REASON: operator_set_mode_is_focus_only" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_CONFIG_ONLY"
    assert payload["result_label"] == "PASS_CONFIG_ONLY"
    assert payload["launch_policy"]["allow_launch"] is False
    assert payload["launch_policy"]["allow_open_configured_url"] is False
    assert payload["launch_policy"]["reason"] == "operator_set_mode_is_focus_only"
    assert payload["events"][0]["event"] == "config_loaded"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False


def test_u2_1qj_missing_config_payload_has_config_load_failed_event(tmp_path: Path) -> None:
    missing_config = tmp_path / "missing" / "target.json"
    evidence_dir = tmp_path / "evidence_missing"

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(missing_config),
            "--evidence-dir",
            str(evidence_dir),
            "--no-real-edge",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: FAIL_OR_BLOCKED" in result.stdout
    assert "LAUNCH_POLICY: no_real_edge" in result.stdout
    assert "LAUNCH_POLICY_REASON: operator_set_mode_is_focus_only" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL_OR_BLOCKED"
    assert payload["result_label"] == "FAIL_OR_BLOCKED"
    assert payload["events"][0]["event"] == "config_load_failed"
    assert payload["launch_policy"]["allow_launch"] is False
    assert payload["launch_policy"]["allow_open_configured_url"] is False
    assert payload["launch_policy"]["reason"] == "operator_set_mode_is_focus_only"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
