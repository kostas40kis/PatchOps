from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_downstream_ready_contract import (
    BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON,
    BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING,
    BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED,
    BLOCKED_DOWNSTREAM_READY_UNSAFE,
    BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND,
    EXPECTED_CONSUMED_KIND,
    PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED,
    PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN,
    READY_CONTRACT_KIND,
    forbidden_flags,
    load_and_validate_consumed,
    validate_consumed_payload,
    write_ready_contract,
    write_ready_contract_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _consumed(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER",
        "write_result": "PASS_CHROME_ACCEPTANCE_HANDOFF_READER_WRITTEN",
        "schema_version": "1",
        "consumed_kind": "chrome_uploader_acceptance_consumed_no_browser",
        "expected_browser": "chrome",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_handoff_sha256": "handoff-hash",
        "source_acceptance_basename": "accepted.json",
        "source_acceptance_sha256": "accepted-hash",
        "handoff_kind": "chrome_uploader_acceptance_no_send",
        "acceptance_result": "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND",
        "acceptance_ok": True,
        "attempt_count": 5,
        "min_attempts": 5,
        "pass_count": 5,
        "min_passes": 4,
        "no_send_verified": True,
        "attachment_verified": True,
        "downstream_contract_accepted": True,
        "downstream_contract_consumer": "patchops_downstream_orchestrator",
        "downstream_contract_no_send_only": True,
        "raw_conversation_text_available": False,
        "browser_opened_by_reader": False,
        "no_browser_action_performed": True,
        "chatgpt_submit_performed": False,
        "forbidden_true_flags": [],
        "next_step_contract": {
            "contract": "chrome_uploader_acceptance_consumed_no_browser",
            "accepted": True,
            "browser_lane": "chrome",
            "read_only_consumer": True,
            "browser_action_performed": False,
            "chatgpt_submit_performed": False,
            "no_send_verified": True,
            "raw_conversation_text_available": False,
            "safe_for_downstream_planning": True,
        },
    }
    payload.update(overrides)
    return payload


def test_validate_consumed_payload_accepts_ready_contract() -> None:
    contract = validate_consumed_payload(_consumed(), source_consumed_basename="consumed.json", source_consumed_sha256="hash")

    assert contract.ok is True
    assert contract.result == PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED
    assert contract.ready_contract_kind == READY_CONTRACT_KIND
    assert contract.consumed_kind == EXPECTED_CONSUMED_KIND
    assert contract.expected_browser == "chrome"
    assert contract.acceptance_result == "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND"
    assert contract.no_send_verified is True
    assert contract.attachment_verified is True
    assert contract.downstream_contract_accepted is True
    assert contract.safe_for_downstream_planning is True
    assert contract.read_only_contract is True
    assert contract.browser_action_performed is False
    assert contract.chatgpt_submit_performed is False
    assert contract.raw_conversation_text_available is False
    assert contract.forbidden_true_flags == []
    assert "plan_downstream_orchestration" in contract.allowed_next_actions
    assert "send_chatgpt_message" in contract.forbidden_next_actions


def test_validate_consumed_payload_blocks_unsupported_kind() -> None:
    contract = validate_consumed_payload(_consumed(consumed_kind="edge_consumed"))

    assert contract.ok is False
    assert contract.result == BLOCKED_DOWNSTREAM_READY_UNSUPPORTED_KIND


def test_validate_consumed_payload_blocks_not_accepted() -> None:
    contract = validate_consumed_payload(_consumed(ok=False, no_send_verified=False))

    assert contract.ok is False
    assert contract.result == BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED
    assert contract.safe_for_downstream_planning is False


def test_validate_consumed_payload_blocks_missing_read_only_field() -> None:
    contract = validate_consumed_payload(_consumed(no_browser_action_performed=False))

    assert contract.ok is False
    assert contract.result == BLOCKED_DOWNSTREAM_READY_NOT_ACCEPTED
    assert "no_browser_action_performed" in contract.reason


def test_validate_consumed_payload_blocks_forbidden_flags_and_raw_text() -> None:
    unsafe = validate_consumed_payload(_consumed(webdriver_used=True))
    assert unsafe.ok is False
    assert unsafe.result == BLOCKED_DOWNSTREAM_READY_UNSAFE
    assert "webdriver_used" in unsafe.forbidden_true_flags

    raw = _consumed()
    raw["next_step_contract"]["raw_conversation_text_available"] = True
    raw_contract = validate_consumed_payload(raw)
    assert raw_contract.ok is False
    assert raw_contract.result == BLOCKED_DOWNSTREAM_READY_UNSAFE
    assert "raw_conversation_text_available" in raw_contract.forbidden_true_flags


def test_forbidden_flags_reads_next_step_contract_actions() -> None:
    payload = _consumed()
    payload["next_step_contract"]["browser_action_performed"] = True

    assert "browser_action_performed" in forbidden_flags(payload)


def test_load_and_validate_consumed_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_consumed(tmp_path / "missing.json")
    assert missing.result == BLOCKED_DOWNSTREAM_READY_CONSUMED_MISSING
    assert missing.read_only_contract is True

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_consumed(bad)
    assert invalid.result == BLOCKED_DOWNSTREAM_READY_CONSUMED_INVALID_JSON
    assert invalid.source_consumed_sha256
    assert invalid.browser_action_performed is False


def test_write_ready_contract_and_marker(tmp_path: Path) -> None:
    contract = validate_consumed_payload(_consumed(), source_consumed_basename="consumed.json", source_consumed_sha256="hash")
    ready_path = write_ready_contract(contract, tmp_path / "handoff" / "latest_uploader_ready_contract.json")
    marker_path = write_ready_contract_marker(contract, tmp_path / "handoff" / "ready.txt")

    payload = json.loads(ready_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED
    assert payload["write_result"] == PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN
    assert payload["ready_contract_kind"] == READY_CONTRACT_KIND
    assert payload["safe_for_downstream_planning"] is True
    assert payload["browser_action_performed"] is False
    assert "safe_for_downstream_planning:true" in marker
    assert "browser_action_performed:false" in marker
    assert "raw_conversation_text_logged:false" in marker


def test_downstream_ready_contract_script_consumes_file(tmp_path: Path) -> None:
    consumed = tmp_path / "latest_uploader_acceptance_consumed.json"
    consumed.write_text(json.dumps(_consumed(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ready = tmp_path / "latest_uploader_ready_contract.json"
    marker = tmp_path / "ready.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_downstream_ready_contract.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--consumed-json",
            str(consumed),
            "--ready-contract-json",
            str(ready),
            "--ready-contract-marker",
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
    assert payload["result"] == PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED
    assert payload["safe_for_downstream_planning"] is True
    assert payload["browser_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False
    saved = json.loads(ready.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN
    assert marker.exists()


def test_downstream_ready_contract_script_blocks_unsafe_consumed(tmp_path: Path) -> None:
    consumed = tmp_path / "latest_uploader_acceptance_consumed.json"
    consumed.write_text(json.dumps(_consumed(selenium_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    ready = tmp_path / "ready.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_downstream_ready_contract.py"

    result = subprocess.run(
        [sys.executable, str(script), "--consumed-json", str(consumed), "--ready-contract-json", str(ready), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_DOWNSTREAM_READY_UNSAFE
    assert "selenium_used" in payload["forbidden_true_flags"]
    saved = json.loads(ready.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_DOWNSTREAM_READY_UNSAFE


def test_downstream_ready_contract_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_downstream_ready_contract.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_downstream_ready_contract_validated" in text
    assert "latest_uploader_acceptance_consumed.json" in text
    assert "latest_uploader_ready_contract.json" in text
    assert "chrome_uploader_downstream_ready_contract" in text
    assert "safe_for_downstream_planning: true" in text
    assert "browser_action_performed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_downstream_ready_contract_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_downstream_ready_contract_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_downstream_ready_contract.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_downstream_ready_contract.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text