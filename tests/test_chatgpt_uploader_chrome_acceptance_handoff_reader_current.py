from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_acceptance_handoff_reader import (
    BLOCKED_HANDOFF_READER_INVALID_JSON,
    BLOCKED_HANDOFF_READER_MISSING,
    BLOCKED_HANDOFF_READER_NOT_ACCEPTED,
    BLOCKED_HANDOFF_READER_UNSAFE,
    BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND,
    CONSUMED_KIND,
    EXPECTED_HANDOFF_KIND,
    PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER,
    PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN,
    forbidden_flags,
    load_and_validate_handoff,
    validate_handoff_payload,
    write_consumed_handoff,
    write_consumed_handoff_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _handoff(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_ACCEPTANCE_HANDOFF_VALIDATED",
        "write_result": "PASS_CHROME_ACCEPTANCE_HANDOFF_WRITTEN",
        "schema_version": "1",
        "handoff_kind": "chrome_uploader_acceptance_no_send",
        "expected_browser": "chrome",
        "source_acceptance_basename": "accepted.json",
        "source_acceptance_sha256": "acceptance-hash",
        "acceptance_result": "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND",
        "acceptance_ok": True,
        "attempt_count": 5,
        "min_attempts": 5,
        "pass_count": 5,
        "min_passes": 4,
        "failed_attempt_count": 0,
        "no_send_verified": True,
        "chrome_executable_found": True,
        "chrome_target_ready": True,
        "canonical_report_found": True,
        "picker_opened": True,
        "exact_path_written": True,
        "file_upload_attempted": True,
        "attachment_verified": True,
        "chatgpt_submit_performed": False,
        "forbidden_true_flags": [],
        "downstream_contract": {
            "contract": "chrome_uploader_acceptance_no_send",
            "consumer": "patchops_downstream_orchestrator",
            "accepted": True,
            "browser_lane": "chrome",
            "no_send_only": True,
            "raw_conversation_text_available": False,
            "conversation_text_logged": False,
        },
    }
    payload.update(overrides)
    return payload


def test_validate_handoff_payload_accepts_read_only_contract() -> None:
    result = validate_handoff_payload(_handoff(), source_handoff_basename="latest.json", source_handoff_sha256="hash")

    assert result.ok is True
    assert result.result == PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER
    assert result.consumed_kind == CONSUMED_KIND
    assert result.handoff_kind == EXPECTED_HANDOFF_KIND
    assert result.expected_browser == "chrome"
    assert result.acceptance_result == "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
    assert result.no_send_verified is True
    assert result.attachment_verified is True
    assert result.downstream_contract_accepted is True
    assert result.downstream_contract_no_send_only is True
    assert result.raw_conversation_text_available is False
    assert result.browser_opened_by_reader is False
    assert result.no_browser_action_performed is True
    assert result.chatgpt_submit_performed is False
    assert result.forbidden_true_flags == []
    assert result.next_step_contract["safe_for_downstream_planning"] is True


def test_validate_handoff_payload_blocks_unsupported_kind() -> None:
    result = validate_handoff_payload(_handoff(handoff_kind="edge_uploader_acceptance_no_send"))

    assert result.ok is False
    assert result.result == BLOCKED_HANDOFF_READER_UNSUPPORTED_KIND


def test_validate_handoff_payload_blocks_not_accepted() -> None:
    result = validate_handoff_payload(_handoff(ok=False, no_send_verified=False))

    assert result.ok is False
    assert result.result == BLOCKED_HANDOFF_READER_NOT_ACCEPTED
    assert result.no_browser_action_performed is True


def test_validate_handoff_payload_blocks_missing_required_true_field() -> None:
    result = validate_handoff_payload(_handoff(picker_opened=False))

    assert result.ok is False
    assert result.result == BLOCKED_HANDOFF_READER_NOT_ACCEPTED
    assert "picker_opened" in result.reason


def test_validate_handoff_payload_blocks_submit_or_forbidden_flags() -> None:
    submit = validate_handoff_payload(_handoff(chatgpt_submit_performed=True))
    assert submit.ok is False
    assert submit.result == BLOCKED_HANDOFF_READER_UNSAFE
    assert "chatgpt_submit_performed" in submit.forbidden_true_flags

    unsafe = validate_handoff_payload(_handoff(webdriver_used=True))
    assert unsafe.ok is False
    assert unsafe.result == BLOCKED_HANDOFF_READER_UNSAFE
    assert "webdriver_used" in unsafe.forbidden_true_flags


def test_forbidden_flags_reads_downstream_contract_raw_text() -> None:
    payload = _handoff()
    payload["downstream_contract"]["raw_conversation_text_available"] = True

    assert "raw_conversation_text_available" in forbidden_flags(payload)


def test_load_and_validate_handoff_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_handoff(tmp_path / "missing.json")
    assert missing.result == BLOCKED_HANDOFF_READER_MISSING
    assert missing.no_browser_action_performed is True

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_handoff(bad)
    assert invalid.result == BLOCKED_HANDOFF_READER_INVALID_JSON
    assert invalid.source_handoff_sha256
    assert invalid.no_browser_action_performed is True


def test_write_consumed_handoff_and_marker(tmp_path: Path) -> None:
    result = validate_handoff_payload(_handoff(), source_handoff_basename="latest.json", source_handoff_sha256="hash")
    consumed = write_consumed_handoff(result, tmp_path / "handoff" / "latest_uploader_acceptance_consumed.json")
    marker = write_consumed_handoff_marker(result, tmp_path / "handoff" / "marker.txt")

    payload = json.loads(consumed.read_text(encoding="utf-8"))
    marker_text = marker.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER
    assert payload["write_result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN
    assert payload["consumed_kind"] == CONSUMED_KIND
    assert payload["browser_opened_by_reader"] is False
    assert payload["no_browser_action_performed"] is True
    assert "browser_opened_by_reader:false" in marker_text
    assert "raw_conversation_text_logged:false" in marker_text


def test_handoff_reader_script_consumes_file(tmp_path: Path) -> None:
    handoff = tmp_path / "latest_uploader_acceptance.json"
    handoff.write_text(json.dumps(_handoff(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    consumed = tmp_path / "latest_uploader_acceptance_consumed.json"
    marker = tmp_path / "consumed.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff_reader.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--handoff-json",
            str(handoff),
            "--consumed-json",
            str(consumed),
            "--consumed-marker",
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
    assert payload["result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER
    assert payload["browser_opened_by_reader"] is False
    assert payload["no_browser_action_performed"] is True
    assert payload["chatgpt_submit_performed"] is False
    saved = json.loads(consumed.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN
    assert marker.exists()


def test_handoff_reader_script_blocks_unsafe_handoff(tmp_path: Path) -> None:
    handoff = tmp_path / "latest_uploader_acceptance.json"
    handoff.write_text(json.dumps(_handoff(selenium_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    consumed = tmp_path / "consumed.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff_reader.py"

    result = subprocess.run(
        [sys.executable, str(script), "--handoff-json", str(handoff), "--consumed-json", str(consumed), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_HANDOFF_READER_UNSAFE
    assert "selenium_used" in payload["forbidden_true_flags"]
    saved = json.loads(consumed.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_HANDOFF_READER_UNSAFE


def test_handoff_reader_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_acceptance_handoff_reader.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_acceptance_handoff_consumed_no_browser" in text
    assert "latest_uploader_acceptance.json" in text
    assert "latest_uploader_acceptance_consumed.json" in text
    assert "chrome_uploader_acceptance_consumed_no_browser" in text
    assert "no_browser_action_performed: true" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_handoff_reader_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_handoff_reader_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_acceptance_handoff_reader.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_acceptance_handoff_reader.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text