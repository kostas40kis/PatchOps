from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_target import (
    BLOCKED_TARGET_CONFIG_INVALID,
    BLOCKED_TARGET_CONFIG_MISSING,
    BLOCKED_UNSUPPORTED_BROWSER,
    PASS_CHROME_TARGET_CONFIG_VALIDATED,
    build_chrome_target_evidence,
    probe_chrome_target_config,
    read_chrome_target_config,
    redact_target_url,
    target_url_sha256,
    write_chrome_target_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def _write_config(path: Path, *, target_url: str = TARGET_URL, browser: str = "chrome") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "target_url": target_url,
                "browser": browser,
                "upload_mode": "file_picker_no_send",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_read_chrome_target_config_accepts_chrome_only(tmp_path: Path) -> None:
    path = _write_config(tmp_path / "target.json")
    config = read_chrome_target_config(path)

    assert config.target_url == TARGET_URL
    assert config.browser == "chrome"
    assert config.upload_mode == "file_picker_no_send"


def test_probe_valid_config_returns_redacted_hash_evidence(tmp_path: Path) -> None:
    path = _write_config(tmp_path / "target.json")
    evidence = probe_chrome_target_config(path)

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_TARGET_CONFIG_VALIDATED
    assert evidence.expected_browser == "chrome"
    assert evidence.browser == "chrome"
    assert evidence.target_url_hash == target_url_sha256(TARGET_URL)
    assert evidence.target_url_hash != TARGET_URL
    assert evidence.redacted_target_display is not None
    assert "chatgpt.com" in evidence.redacted_target_display
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in evidence.redacted_target_display
    assert evidence.raw_conversation_text_logged is False
    assert evidence.file_upload_attempted is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False
    assert evidence.safety_flags["live_browser_used"] is False
    assert evidence.safety_flags["browser_launched"] is False


def test_probe_missing_config_returns_blocked_missing(tmp_path: Path) -> None:
    evidence = probe_chrome_target_config(tmp_path / "missing.json")

    assert evidence.ok is False
    assert evidence.result == BLOCKED_TARGET_CONFIG_MISSING
    assert evidence.expected_browser == "chrome"
    assert evidence.target_url_hash is None
    assert evidence.redacted_target_display is None
    assert evidence.raw_conversation_text_logged is False


def test_probe_invalid_json_returns_blocked_invalid(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")

    evidence = probe_chrome_target_config(path)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_TARGET_CONFIG_INVALID
    assert evidence.error
    assert evidence.raw_conversation_text_logged is False


def test_probe_rejects_non_chrome_browser(tmp_path: Path) -> None:
    for browser in ["edge", "msedge", "firefox", "any", "auto", "all"]:
        path = _write_config(tmp_path / f"{browser}.json", browser=browser)
        evidence = probe_chrome_target_config(path)
        assert evidence.ok is False
        assert evidence.result == BLOCKED_UNSUPPORTED_BROWSER
        assert evidence.expected_browser == "chrome"
        assert evidence.raw_conversation_text_logged is False


def test_probe_rejects_non_chatgpt_target(tmp_path: Path) -> None:
    path = _write_config(tmp_path / "wrong-host.json", target_url="https://example.com/c/demo")
    evidence = probe_chrome_target_config(path)

    assert evidence.ok is False
    assert evidence.result == BLOCKED_TARGET_CONFIG_INVALID
    assert "chatgpt.com" in (evidence.error or "")


def test_redaction_and_hash_helpers_do_not_expose_raw_url() -> None:
    redacted = redact_target_url(TARGET_URL)
    digest = target_url_sha256(TARGET_URL)

    assert redacted != TARGET_URL
    assert "chatgpt.com" in redacted
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in redacted
    assert digest != TARGET_URL
    assert len(digest) == 64


def test_write_chrome_target_evidence_roundtrip(tmp_path: Path) -> None:
    path = _write_config(tmp_path / "target.json")
    evidence = probe_chrome_target_config(path)
    output_path = write_chrome_target_evidence(evidence, tmp_path / "evidence" / "target_evidence.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["result"] == PASS_CHROME_TARGET_CONFIG_VALIDATED
    assert payload["expected_browser"] == "chrome"
    assert payload["browser"] == "chrome"
    assert payload["target_url_hash"] == target_url_sha256(TARGET_URL)
    assert payload["raw_conversation_text_logged"] is False
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False


def test_build_chrome_target_evidence_has_required_fields(tmp_path: Path) -> None:
    config = read_chrome_target_config(_write_config(tmp_path / "target.json"))
    evidence = build_chrome_target_evidence(config, target_config_path=tmp_path / "target.json")
    payload = evidence.to_payload()

    assert payload["result"] == PASS_CHROME_TARGET_CONFIG_VALIDATED
    assert payload["expected_browser"] == "chrome"
    assert payload["target_url_hash"]
    assert payload["redacted_target_display"]
    assert payload["raw_conversation_text_logged"] is False


def test_doctor_script_outputs_json_and_evidence(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path / "target.json")
    evidence_path = tmp_path / "evidence.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_target_config_doctor.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--evidence-path",
            str(evidence_path),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == PASS_CHROME_TARGET_CONFIG_VALIDATED
    assert payload["expected_browser"] == "chrome"
    assert payload["browser"] == "chrome"
    assert payload["raw_conversation_text_logged"] is False
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["target_url_hash"] == target_url_sha256(TARGET_URL)
    assert TARGET_URL not in result.stdout

    evidence_payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence_payload["result"] == PASS_CHROME_TARGET_CONFIG_VALIDATED
    assert TARGET_URL not in evidence_path.read_text(encoding="utf-8")


def test_doctor_script_returns_zero_for_blocked_missing(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_target_config_doctor.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(tmp_path / "missing.json"),
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_TARGET_CONFIG_MISSING
    assert payload["ok"] is False
    assert payload["raw_conversation_text_logged"] is False


def test_doctor_script_text_output_has_required_safety_lines(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path / "target.json")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_target_config_doctor.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "RESULT: PASS_CHROME_TARGET_CONFIG_VALIDATED" in result.stdout
    assert "EXPECTED_BROWSER: chrome" in result.stdout
    assert "raw_conversation_text_logged:false" in result.stdout
    assert "file_upload_attempted:false" in result.stdout
    assert "chatgpt_submit_performed:false" in result.stdout
    assert "selenium_used:false" in result.stdout
    assert "webdriver_used:false" in result.stdout
    assert "browser_dom_automation_used:false" in result.stdout
    assert TARGET_URL not in result.stdout


def test_chrome_target_patch_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]

    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_target_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_target.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_target_config_doctor.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "pywinauto", "playwright"]

    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text