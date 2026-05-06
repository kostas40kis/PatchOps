from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_1qh_preflight_prints_legacy_evidence_lines_for_success(tmp_path: Path) -> None:
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
    assert "JSON_EVIDENCE:" in result.stdout
    assert "TXT_EVIDENCE:" in result.stdout
    assert "LAUNCH_ALLOWED: false" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    evidence = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert evidence["status"] == "PASS_CONFIG_ONLY"
    assert evidence["launch_allowed"] is False
    assert evidence["file_upload_attempted"] is False
    assert evidence["chatgpt_submit_performed"] is False


def test_u2_1qh_preflight_prints_legacy_evidence_lines_for_missing_config(tmp_path: Path) -> None:
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
    assert "JSON_EVIDENCE:" in result.stdout
    assert "TXT_EVIDENCE:" in result.stdout
    assert "LAUNCH_ALLOWED: false" in result.stdout
    assert "FILE_UPLOAD_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    evidence = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert evidence["status"] == "FAIL_OR_BLOCKED"
    assert evidence["result"] == "FAIL_OR_BLOCKED_MISSING_TARGET_CONFIG"
    assert evidence["launch_allowed"] is False
    assert evidence["file_upload_attempted"] is False
    assert evidence["chatgpt_submit_performed"] is False
