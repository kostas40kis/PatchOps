from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_live_no_send_preflight_contract import (
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE,
    BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND,
    CONTRACT_KIND,
    PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN,
    forbidden_flags,
    load_and_validate_instruction_packet,
    validate_instruction_packet_payload,
    write_preflight_contract,
    write_preflight_contract_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _packet(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED",
        "write_result": "PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN",
        "schema_version": "1",
        "packet_kind": "chrome_uploader_live_instruction_packet_no_action",
        "expected_browser": "chrome",
        "source_boundary_basename": "latest_uploader_live_action_boundary.json",
        "source_boundary_sha256": "boundary-hash",
        "source_ready_basename": "latest_uploader_ready_contract.json",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "boundary_kind": "chrome_uploader_explicit_live_action_boundary",
        "boundary_result": "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED",
        "boundary_confirmed": True,
        "live_action_allowed_by_boundary": True,
        "packet_performs_browser_action": False,
        "packet_performs_chatgpt_submit": False,
        "packet_reads_conversation_text": False,
        "send_allowed": False,
        "no_send_verified": True,
        "attachment_verified": True,
        "safe_for_downstream_planning": True,
        "human_must_confirm_visible_chrome": True,
        "human_must_verify_no_send": True,
        "instructions": ["Use Chrome only."],
        "stop_conditions": ["visible_chrome_target_missing", "cloudflare_or_captcha_detected", "send_button_focus_or_submit_risk"],
        "allowed_next_scripts": ["scripts/run_uploader_chrome_live_no_send_preflight.py"],
        "allowed_actions_with_human_confirmation": ["focus_existing_chrome_window", "verify_attachment_chip_no_send"],
        "always_forbidden": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
        "forbidden_true_flags": [],
    }
    payload.update(overrides)
    return payload


def test_validate_instruction_packet_payload_writes_preflight_contract() -> None:
    contract = validate_instruction_packet_payload(_packet(), source_packet_basename="packet.json", source_packet_sha256="hash")

    assert contract.ok is True
    assert contract.result == PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED
    assert contract.contract_kind == CONTRACT_KIND
    assert contract.expected_browser == "chrome"
    assert contract.packet_kind == "chrome_uploader_live_instruction_packet_no_action"
    assert contract.packet_result == "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED"
    assert contract.boundary_kind == "chrome_uploader_explicit_live_action_boundary"
    assert contract.boundary_result == "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED"
    assert contract.preflight_contract_ready is True
    assert contract.no_send_verified is True
    assert contract.attachment_verified is True
    assert contract.packet_performs_browser_action is False
    assert contract.packet_performs_chatgpt_submit is False
    assert contract.packet_reads_conversation_text is False
    assert contract.browser_action_performed is False
    assert contract.chatgpt_submit_performed is False
    assert contract.send_allowed is False
    assert contract.raw_conversation_text_available is False
    assert "visible_existing_chrome_window" in contract.required_visible_state
    assert "open_file_picker_with_human_visible_target" in contract.permitted_future_actions
    assert "send_chatgpt_message" in contract.forbidden_actions
    assert "cloudflare_or_captcha_detected" in contract.stop_conditions
    assert contract.allowed_next_script == "scripts/run_uploader_chrome_live_no_send_executor.py"


def test_validate_instruction_packet_payload_blocks_unsupported_kind() -> None:
    contract = validate_instruction_packet_payload(_packet(packet_kind="edge_packet"))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSUPPORTED_KIND
    assert contract.preflight_contract_ready is False


def test_validate_instruction_packet_payload_blocks_not_ready() -> None:
    contract = validate_instruction_packet_payload(_packet(ok=False, boundary_confirmed=False, live_action_allowed_by_boundary=False))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_NOT_READY
    assert "boundary_confirmed" in contract.reason
    assert contract.preflight_contract_ready is False
    assert contract.browser_action_performed is False


def test_validate_instruction_packet_payload_blocks_unsafe_flags() -> None:
    contract = validate_instruction_packet_payload(_packet(packet_performs_browser_action=True))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE
    assert "packet_performs_browser_action" in contract.forbidden_true_flags
    assert contract.browser_action_performed is False

    raw = validate_instruction_packet_payload(_packet(raw_conversation_text_available=True))
    assert raw.ok is False
    assert raw.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE
    assert "raw_conversation_text_available" in raw.forbidden_true_flags


def test_forbidden_flags_reads_safety_flags() -> None:
    payload = _packet()
    payload["safety_flags"] = {"webdriver_used": True}

    assert "webdriver_used" in forbidden_flags(payload)


def test_load_and_validate_instruction_packet_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_instruction_packet(tmp_path / "missing.json")
    assert missing.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_MISSING
    assert missing.browser_action_performed is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_instruction_packet(bad)
    assert invalid.result == BLOCKED_LIVE_NO_SEND_PREFLIGHT_PACKET_INVALID_JSON
    assert invalid.source_packet_sha256
    assert invalid.browser_action_performed is False


def test_write_preflight_contract_and_marker(tmp_path: Path) -> None:
    contract = validate_instruction_packet_payload(_packet(), source_packet_basename="packet.json", source_packet_sha256="hash")
    contract_path = write_preflight_contract(contract, tmp_path / "handoff" / "latest_uploader_live_no_send_preflight_contract.json")
    marker_path = write_preflight_contract_marker(contract, tmp_path / "handoff" / "contract.txt")

    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED
    assert payload["write_result"] == PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN
    assert payload["contract_kind"] == CONTRACT_KIND
    assert payload["preflight_contract_ready"] is True
    assert payload["browser_action_performed"] is False
    assert "preflight_contract_ready:true" in marker
    assert "packet_performs_browser_action:false" in marker
    assert "raw_conversation_text_logged:false" in marker


def test_preflight_contract_script_writes_contract(tmp_path: Path) -> None:
    packet = tmp_path / "latest_uploader_live_instruction_packet.json"
    packet.write_text(json.dumps(_packet(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract = tmp_path / "latest_uploader_live_no_send_preflight_contract.json"
    marker = tmp_path / "contract.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_preflight_contract.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--packet-json",
            str(packet),
            "--contract-json",
            str(contract),
            "--contract-marker",
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
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED
    assert payload["preflight_contract_ready"] is True
    assert payload["browser_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_allowed"] is False
    saved = json.loads(contract.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN
    assert marker.exists()


def test_preflight_contract_script_blocks_unsafe_packet(tmp_path: Path) -> None:
    packet = tmp_path / "latest_uploader_live_instruction_packet.json"
    packet.write_text(json.dumps(_packet(webdriver_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract = tmp_path / "contract.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_preflight_contract.py"

    result = subprocess.run(
        [sys.executable, str(script), "--packet-json", str(packet), "--contract-json", str(contract), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]
    saved = json.loads(contract.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_NO_SEND_PREFLIGHT_UNSAFE


def test_preflight_contract_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_no_send_preflight_contract.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_live_no_send_preflight_contract_validated" in text
    assert "latest_uploader_live_instruction_packet.json" in text
    assert "latest_uploader_live_no_send_preflight_contract.json" in text
    assert "chrome_uploader_live_no_send_preflight_contract" in text
    assert "preflight_contract_ready: true" in text
    assert "browser_action_performed: false" in text
    assert "send_allowed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_preflight_contract_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_preflight_contract_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_live_no_send_preflight_contract.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_preflight_contract.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text