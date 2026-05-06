from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_u2_1qg_config_payload_include_target_url_false(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config

    target = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
    cfg = ChatGPTUploaderConfig.create(target)
    hidden = cfg.to_payload(include_target_url=False)

    assert "target_url" not in hidden
    assert hidden["target_url_redacted"]
    assert hidden["target_url_sha256"]
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in json.dumps(hidden)

    path = tmp_path / "target.json"
    assert write_config(cfg, path) == path.resolve()


def test_u2_1qg_target_setter_hash_line_and_preflight_aliases(tmp_path: Path) -> None:
    config_path = tmp_path / "target.json"
    evidence_dir = tmp_path / "evidence"
    setter = PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"
    preflight = PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"

    set_result = subprocess.run(
        [
            sys.executable,
            str(setter),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            "https://chatgpt.com",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert set_result.returncode == 0, set_result.stderr
    assert "TARGET_CONFIG_WRITTEN:" in set_result.stdout
    assert "TARGET_URL_REDACTED: https://chatgpt.com/" in set_result.stdout
    assert "TARGET_URL_SHA256:" in set_result.stdout

    preflight_result = subprocess.run(
        [
            sys.executable,
            str(preflight),
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
    assert preflight_result.returncode == 0, preflight_result.stderr
    assert "PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS_CONFIG_ONLY" in preflight_result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in preflight_result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in preflight_result.stdout
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in preflight_result.stdout


def test_u2_1qg_preflight_missing_config_reports_fail_or_blocked(tmp_path: Path) -> None:
    missing_config = tmp_path / "missing" / "target.json"
    evidence_dir = tmp_path / "evidence_missing"
    preflight = PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py"

    result = subprocess.run(
        [
            sys.executable,
            str(preflight),
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
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert list(evidence_dir.glob("*.json"))
    assert list(evidence_dir.glob("*.txt"))
