from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_live_instruction_packet import (
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON,
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING,
    BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED,
    BLOCKED_LIVE_INSTRUCTION_UNSAFE,
    BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND,
    PACKET_KIND,
    PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED,
    PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN,
    forbidden_flags,
    load_and_validate_boundary,
    validate_boundary_payload,
    write_instruction_packet,
    write_instruction_packet_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _boundary(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED",
        "write_result": "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN",
        "schema_version": "1",
        "boundary_kind": "chrome_uploader_explicit_live_action_boundary",
        "expected_browser": "chrome",
        "source_ready_basename": "latest_uploader_ready_contract.json",
        "source_ready_sha256": "ready-hash",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "ready_contract_kind": "chrome_uploader_downstream_ready_contract",
        "ready_result": "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED",
        "no_send_verified": True,
        "attachment_verified": True,
        "safe_for_downstream_planning": True,
        "read_only_source_contract": True,
        "confirmation_required": True,
        "required_confirmation_text": "PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_ACTION",
        "confirmation_supplied": True,
        "boundary_confirmed": True,
        "live_action_allowed": True,
        "send_allowed": False,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "raw_conversation_text_available": False,
        "forbidden_true_flags": [],
        "allowed_with_confirmation": ["focus_existing_chrome_window", "verify_attachment_chip_no_send"],
        "always_forbidden": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
    }
    payload.update(overrides)
    return payload


def test_validate_boundary_payload_writes_instruction_packet_no_action() -> None:
    packet = validate_boundary_payload(_boundary(), source_boundary_basename="boundary.json", source_boundary_sha256="hash")

    assert packet.ok is True
    assert packet.result == PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED
    assert packet.packet_kind == PACKET_KIND
    assert packet.expected_browser == "chrome"
    assert packet.boundary_confirmed is True
    assert packet.live_action_allowed_by_boundary is True
    assert packet.packet_performs_browser_action is False
    assert packet.packet_performs_chatgpt_submit is False
    assert packet.packet_reads_conversation_text is False
    assert packet.send_allowed is False
    assert packet.no_send_verified is True
    assert packet.attachment_verified is True
    assert packet.human_must_confirm_visible_chrome is True
    assert packet.human_must_verify_no_send is True
    assert "focus_existing_chrome_window" in packet.allowed_actions_with_human_confirmation
    assert "send_chatgpt_message" in packet.always_forbidden
    assert "cloudflare_or_captcha_detected" in packet.stop_conditions
    assert packet.forbidden_true_flags == []


def test_validate_boundary_payload_blocks_unconfirmed_boundary() -> None:
    packet = validate_boundary_payload(_boundary(ok=False, result="BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED", boundary_confirmed=False, live_action_allowed=False))

    assert packet.ok is False
    assert packet.result == BLOCKED_LIVE_INSTRUCTION_BOUNDARY_NOT_CONFIRMED
    assert packet.live_action_allowed_by_boundary is False
    assert packet.packet_performs_browser_action is False
    assert packet.instructions == []


def test_validate_boundary_payload_blocks_unsupported_kind() -> None:
    packet = validate_boundary_payload(_boundary(boundary_kind="edge_live_boundary"))

    assert packet.ok is False
    assert packet.result == BLOCKED_LIVE_INSTRUCTION_UNSUPPORTED_KIND


def test_validate_boundary_payload_blocks_unsafe_flags() -> None:
    packet = validate_boundary_payload(_boundary(browser_action_performed=True))

    assert packet.ok is False
    assert packet.result == BLOCKED_LIVE_INSTRUCTION_UNSAFE
    assert "browser_action_performed" in packet.forbidden_true_flags

    webdriver_packet = validate_boundary_payload(_boundary(webdriver_used=True))
    assert webdriver_packet.ok is False
    assert webdriver_packet.result == BLOCKED_LIVE_INSTRUCTION_UNSAFE
    assert "webdriver_used" in webdriver_packet.forbidden_true_flags


def test_forbidden_flags_reads_top_level_and_safety_flags() -> None:
    payload = _boundary()
    payload["safety_flags"] = {"raw_conversation_text_logged": True}

    assert "raw_conversation_text_logged" in forbidden_flags(payload)


def test_load_and_validate_boundary_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_boundary(tmp_path / "missing.json")
    assert missing.result == BLOCKED_LIVE_INSTRUCTION_BOUNDARY_MISSING
    assert missing.packet_performs_browser_action is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_boundary(bad)
    assert invalid.result == BLOCKED_LIVE_INSTRUCTION_BOUNDARY_INVALID_JSON
    assert invalid.source_boundary_sha256
    assert invalid.packet_performs_browser_action is False


def test_write_instruction_packet_and_marker(tmp_path: Path) -> None:
    packet = validate_boundary_payload(_boundary(), source_boundary_basename="boundary.json", source_boundary_sha256="hash")
    packet_path = write_instruction_packet(packet, tmp_path / "handoff" / "latest_uploader_live_instruction_packet.json")
    marker_path = write_instruction_packet_marker(packet, tmp_path / "handoff" / "packet.txt")

    payload = json.loads(packet_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED
    assert payload["write_result"] == PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN
    assert payload["packet_kind"] == PACKET_KIND
    assert payload["packet_performs_browser_action"] is False
    assert payload["packet_performs_chatgpt_submit"] is False
    assert "packet_performs_browser_action:false" in marker
    assert "packet_reads_conversation_text:false" in marker
    assert "cloudflare_or_captcha_detected" in marker


def test_live_instruction_packet_script_writes_packet(tmp_path: Path) -> None:
    boundary = tmp_path / "latest_uploader_live_action_boundary.json"
    boundary.write_text(json.dumps(_boundary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet = tmp_path / "latest_uploader_live_instruction_packet.json"
    marker = tmp_path / "packet.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_instruction_packet.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--boundary-json",
            str(boundary),
            "--packet-json",
            str(packet),
            "--packet-marker",
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
    assert payload["result"] == PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED
    assert payload["packet_performs_browser_action"] is False
    assert payload["packet_performs_chatgpt_submit"] is False
    assert payload["send_allowed"] is False
    saved = json.loads(packet.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_LIVE_INSTRUCTION_PACKET_WRITTEN
    assert marker.exists()


def test_live_instruction_packet_script_blocks_unsafe_boundary(tmp_path: Path) -> None:
    boundary = tmp_path / "latest_uploader_live_action_boundary.json"
    boundary.write_text(json.dumps(_boundary(webdriver_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet = tmp_path / "packet.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_instruction_packet.py"

    result = subprocess.run(
        [sys.executable, str(script), "--boundary-json", str(boundary), "--packet-json", str(packet), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_LIVE_INSTRUCTION_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]
    saved = json.loads(packet.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_INSTRUCTION_UNSAFE


def test_live_instruction_packet_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_instruction_packet.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_live_instruction_packet_validated" in text
    assert "latest_uploader_live_action_boundary.json" in text
    assert "latest_uploader_live_instruction_packet.json" in text
    assert "chrome_uploader_live_instruction_packet_no_action" in text
    assert "packet_performs_browser_action: false" in text
    assert "packet_performs_chatgpt_submit: false" in text
    assert "send_allowed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_live_instruction_packet_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_live_instruction_packet_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_live_instruction_packet.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_instruction_packet.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text