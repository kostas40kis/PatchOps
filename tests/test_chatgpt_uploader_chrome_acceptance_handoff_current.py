from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_acceptance_handoff import (
    BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON,
    BLOCKED_ACCEPTANCE_HANDOFF_MISSING,
    BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE,
    BLOCKED_ACCEPTANCE_NOT_PASSED,
    HANDOFF_KIND,
    PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED,
    PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN,
    forbidden_flags,
    load_and_validate_acceptance,
    validate_acceptance_payload,
    write_acceptance_handoff,
    write_acceptance_handoff_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _acceptance(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND",
        "expected_browser": "chrome",
        "attempt_count": 5,
        "min_attempts": 5,
        "pass_count": 5,
        "min_passes": 4,
        "failed_attempt_count": 0,
        "forbidden_true_flags": [],
        "chatgpt_submit_detected": False,
        "chrome_executable_found": True,
        "chrome_target_ready": True,
        "canonical_report_found": True,
        "picker_opened": True,
        "exact_path_written": True,
        "file_upload_attempted": True,
        "attachment_verified": True,
        "chatgpt_submit_performed": False,
        "selenium_used": False,
        "webdriver_used": False,
        "browser_dom_automation_used": False,
        "cloudflare_bypass_attempted": False,
        "captcha_bypass_attempted": False,
        "conversation_text_logged": False,
        "raw_conversation_text_logged": False,
        "random_page_click_performed": False,
        "attempts": [],
    }
    payload.update(overrides)
    return payload


def test_validate_acceptance_payload_accepts_passed_no_send_contract() -> None:
    handoff = validate_acceptance_payload(_acceptance(), source_acceptance_basename="accepted.json", source_acceptance_sha256="hash")

    assert handoff.ok is True
    assert handoff.result == PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED
    assert handoff.handoff_kind == HANDOFF_KIND
    assert handoff.expected_browser == "chrome"
    assert handoff.acceptance_result == "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
    assert handoff.attempt_count == 5
    assert handoff.pass_count == 5
    assert handoff.no_send_verified is True
    assert handoff.attachment_verified is True
    assert handoff.chatgpt_submit_performed is False
    assert handoff.forbidden_true_flags == []
    assert handoff.downstream_contract["accepted"] is True
    assert handoff.downstream_contract["raw_conversation_text_available"] is False


def test_validate_acceptance_payload_blocks_not_passed() -> None:
    handoff = validate_acceptance_payload(_acceptance(ok=False, result="BLOCKED_ACCEPTANCE_TOO_FEW_PASSES"))

    assert handoff.ok is False
    assert handoff.result == BLOCKED_ACCEPTANCE_NOT_PASSED
    assert handoff.no_send_verified is False


def test_validate_acceptance_payload_blocks_missing_required_readiness_field() -> None:
    handoff = validate_acceptance_payload(_acceptance(picker_opened=False))

    assert handoff.ok is False
    assert handoff.result == BLOCKED_ACCEPTANCE_NOT_PASSED
    assert "picker_opened" in handoff.reason


def test_validate_acceptance_payload_blocks_submit_detected() -> None:
    handoff = validate_acceptance_payload(_acceptance(chatgpt_submit_performed=True, chatgpt_submit_detected=True))

    assert handoff.ok is False
    assert handoff.result == BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE
    assert handoff.no_send_verified is False
    assert handoff.chatgpt_submit_performed is True


def test_validate_acceptance_payload_blocks_forbidden_flag_from_top_level() -> None:
    handoff = validate_acceptance_payload(_acceptance(webdriver_used=True))

    assert handoff.ok is False
    assert handoff.result == BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE
    assert "webdriver_used" in handoff.forbidden_true_flags


def test_forbidden_flags_reads_attempt_flags() -> None:
    payload = _acceptance(attempts=[{"forbidden_true_flags": ["selenium_used"]}])

    assert forbidden_flags(payload) == ["selenium_used"]


def test_load_and_validate_acceptance_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_acceptance(tmp_path / "missing.json")
    assert missing.result == BLOCKED_ACCEPTANCE_HANDOFF_MISSING

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_acceptance(bad)
    assert invalid.result == BLOCKED_ACCEPTANCE_HANDOFF_INVALID_JSON
    assert invalid.source_acceptance_sha256


def test_write_handoff_and_marker_roundtrip(tmp_path: Path) -> None:
    handoff = validate_acceptance_payload(_acceptance(), source_acceptance_basename="accepted.json", source_acceptance_sha256="hash")
    handoff_path = write_acceptance_handoff(handoff, tmp_path / "handoff" / "latest_uploader_acceptance.json")
    marker_path = write_acceptance_handoff_marker(handoff, tmp_path / "handoff" / "marker.txt")

    payload = json.loads(handoff_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED
    assert payload["write_result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN
    assert payload["handoff_kind"] == HANDOFF_KIND
    assert payload["no_send_verified"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert "chatgpt_submit_performed:false" in marker
    assert "webdriver_used:false" in marker


def test_acceptance_handoff_script_writes_default_style_handoff(tmp_path: Path) -> None:
    acceptance = tmp_path / "accepted.json"
    acceptance.write_text(json.dumps(_acceptance(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    handoff = tmp_path / "latest_uploader_acceptance.json"
    marker = tmp_path / "handoff.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--acceptance-json",
            str(acceptance),
            "--handoff-json",
            str(handoff),
            "--handoff-marker",
            str(marker),
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
    assert payload["result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED
    assert payload["no_send_verified"] is True
    assert payload["chatgpt_submit_performed"] is False

    saved = json.loads(handoff.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN
    assert saved["downstream_contract"]["accepted"] is True
    assert marker.exists()


def test_acceptance_handoff_script_blocks_unsafe_acceptance(tmp_path: Path) -> None:
    acceptance = tmp_path / "accepted.json"
    acceptance.write_text(json.dumps(_acceptance(selenium_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    handoff = tmp_path / "handoff.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff.py"

    result = subprocess.run(
        [sys.executable, str(script), "--acceptance-json", str(acceptance), "--handoff-json", str(handoff), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE
    assert "selenium_used" in payload["forbidden_true_flags"]
    saved = json.loads(handoff.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_ACCEPTANCE_HANDOFF_UNSAFE


def test_acceptance_handoff_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_acceptance_handoff.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "chrome acceptance handoff" in text
    assert "chrome-only" in text
    assert "no-send" in text
    assert "latest_uploader_acceptance.json" in text
    assert "pass_chrome_upload_accepted_no_send" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_acceptance_handoff_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_acceptance_handoff_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_acceptance_handoff.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text