from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _json_evidence_path(stdout: str) -> Path:
    line = next(line for line in stdout.splitlines() if line.startswith("JSON_EVIDENCE:"))
    return Path(line.split(":", 1)[1].strip())


def test_u2_7a_existing_target_probe_from_titles_contract() -> None:
    from patchops.chatgpt_uploader.existing_target_probe import probe_existing_target_from_titles

    result = probe_existing_target_from_titles(
        ["Settings - Microsoft Edge", "ChatGPT - Microsoft Edge"],
        target_url="https://chatgpt.com/g/demo/c/abc123def456",
        focused=True,
    )
    payload = result.to_payload()

    assert payload["existing_target_probe_attempted"] is True
    assert payload["existing_target_found"] is True
    assert payload["existing_target_focused"] is True
    assert payload["launch_skipped_existing_target"] is True
    assert payload["normal_edge_launch_attempted"] is False
    assert payload["conversation_text_logged"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["title_hashes"]
    assert "ChatGPT - Microsoft Edge" not in json.dumps(payload)


def test_u2_7a_script_simulated_existing_target_skips_launch_no_send(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config

    config_path = tmp_path / "target.json"
    report_path = tmp_path / "report.txt"
    evidence_dir = tmp_path / "evidence"
    report_path.write_text("report body\n", encoding="utf-8")
    write_config(ChatGPTUploaderConfig.create("https://chatgpt.com/"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_existing_target_preferred_live.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--report-path",
            str(report_path),
            "--evidence-dir",
            str(evidence_dir),
            "--simulate-existing-target-found",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "EXISTING_TARGET_PROBE_ATTEMPTED: true" in result.stdout
    assert "EXISTING_TARGET_FOUND: true" in result.stdout
    assert "LAUNCH_SKIPPED_EXISTING_TARGET: true" in result.stdout
    assert "NORMAL_EDGE_LAUNCH_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["existing_target_found"] is True
    assert payload["normal_edge_launch_attempted"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["conversation_text_logged"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False


def test_u2_7a_script_blocks_without_target_and_launch_disabled(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, write_config

    config_path = tmp_path / "target.json"
    report_path = tmp_path / "report.txt"
    evidence_dir = tmp_path / "evidence"
    report_path.write_text("report body\n", encoding="utf-8")
    write_config(ChatGPTUploaderConfig.create("https://chatgpt.com/"), config_path)

    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_uploader_existing_target_preferred_live.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--report-path",
            str(report_path),
            "--evidence-dir",
            str(evidence_dir),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "EXISTING_TARGET_PROBE_ATTEMPTED: true" in result.stdout
    assert "NORMAL_EDGE_LAUNCH_ATTEMPTED: false" in result.stdout
    assert "CHATGPT_SUBMIT_PERFORMED: false" in result.stdout

    payload = json.loads(_json_evidence_path(result.stdout).read_text(encoding="utf-8"))
    assert payload["normal_edge_launch_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["conversation_text_logged"] is False
