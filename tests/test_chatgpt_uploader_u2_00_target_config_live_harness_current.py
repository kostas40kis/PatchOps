from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader.config import (
    ChatGptCopilotTargetConfig,
    read_target_config,
    redact_target_url,
    target_url_sha256,
    write_target_config,
)
from patchops.chatgpt_uploader.evidence import DEFAULT_SAFETY_FLAGS, UploaderEvidence, write_evidence_pair


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_target_config_roundtrip_and_hash(tmp_path: Path) -> None:
    config_path = tmp_path / "target.json"

    written = write_target_config(
        config_path,
        target_url=TARGET_URL,
        source_patch="test_patch",
    )
    loaded = read_target_config(config_path)

    assert loaded == written
    assert loaded.browser == "msedge"
    assert loaded.mode == "operator_set"
    assert loaded.allow_real_edge_default is True
    assert loaded.allow_upload_default is False
    assert loaded.allow_send_default is False
    assert loaded.target_url_sha256 == target_url_sha256(TARGET_URL)

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["target_url"] == TARGET_URL
    assert payload["target_url_sha256"] == target_url_sha256(TARGET_URL)


def test_target_url_redaction_does_not_log_full_conversation_id() -> None:
    redacted = redact_target_url(TARGET_URL)

    assert redacted.startswith("https://chatgpt.com/")
    assert "69f8530a" in redacted
    assert "b34eaa36070d" not in redacted
    assert TARGET_URL not in redacted


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "http://chatgpt.com/g/example/c/abc",
        "https://example.com/g/example/c/abc",
    ],
)
def test_target_config_rejects_invalid_urls(bad_url: str) -> None:
    with pytest.raises(ValueError):
        ChatGptCopilotTargetConfig(target_url=bad_url)


def test_target_config_rejects_hash_mismatch() -> None:
    with pytest.raises(ValueError, match="target_url_sha256"):
        ChatGptCopilotTargetConfig(target_url=TARGET_URL, target_url_sha256="not-the-real-hash")


def test_evidence_pair_writes_json_and_txt_without_upload_or_send(tmp_path: Path) -> None:
    config = ChatGptCopilotTargetConfig(target_url=TARGET_URL, source_patch="test_patch")
    evidence = UploaderEvidence.start("u2_00_test", run_id="u2_00_test_evidence")
    evidence.attach_config(config, tmp_path / "target.json")
    evidence.set_detail("unit_test", True)
    evidence.finish("PASS_UNIT")

    json_path, txt_path = write_evidence_pair(evidence, tmp_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    text = txt_path.read_text(encoding="utf-8")

    assert payload["result"] == "PASS_UNIT"
    assert payload["target"]["target_url_sha256"] == target_url_sha256(TARGET_URL)
    assert payload["safety_flags"] == DEFAULT_SAFETY_FLAGS
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False
    assert "file_upload_attempted : false" in text
    assert "chatgpt_submit_performed : false" in text


def test_operator_scripts_config_only_smoke(tmp_path: Path) -> None:
    config_path = tmp_path / "chatgpt_copilot_target.json"
    evidence_dir = tmp_path / "evidence"

    set_result = subprocess.run(
        [
            sys.executable,
            "scripts/set_chatgpt_copilot_target.py",
            "--target-url",
            TARGET_URL,
            "--config-path",
            str(config_path),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert set_result.returncode == 0, set_result.stderr
    assert config_path.exists()

    preflight_result = subprocess.run(
        [
            sys.executable,
            "scripts/run_uploader_edge_preflight.py",
            "--config-path",
            str(config_path),
            "--evidence-dir",
            str(evidence_dir),
            "--config-only",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert preflight_result.returncode == 0, preflight_result.stderr
    assert "PASS_CONFIG_ONLY" in preflight_result.stdout

    evidence_files = list(evidence_dir.glob("*.json"))
    assert evidence_files
    payload = json.loads(evidence_files[0].read_text(encoding="utf-8"))
    assert payload["result"] == "PASS_CONFIG_ONLY"
    assert payload["safety_flags"]["selenium_used"] is False
    assert payload["safety_flags"]["webdriver_used"] is False
    assert payload["safety_flags"]["browser_dom_automation_used"] is False
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False


def test_u2_00_scripts_do_not_import_selenium_or_webdriver() -> None:
    script_paths = [
        PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py",
        PROJECT_ROOT / "scripts" / "run_uploader_edge_preflight.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "config.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "evidence.py",
    ]

    for path in script_paths:
        text = path.read_text(encoding="utf-8").lower()
        assert "import selenium" not in text
        assert "from selenium" not in text
        assert "webdriver.edge" not in text
        assert "webdriver.chrome" not in text