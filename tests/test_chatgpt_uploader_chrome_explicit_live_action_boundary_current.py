from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_explicit_live_action_boundary import (
    BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED,
    BLOCKED_LIVE_BOUNDARY_NOT_READY,
    BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON,
    BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING,
    BLOCKED_LIVE_BOUNDARY_UNSAFE,
    BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND,
    BOUNDARY_KIND,
    PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED,
    PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN,
    REQUIRED_CONFIRMATION_TEXT,
    forbidden_flags,
    load_and_validate_ready_contract,
    validate_ready_contract_payload,
    write_live_action_boundary,
    write_live_action_boundary_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _ready(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED",
        "write_result": "PASS_CHROME_DOWNSTREAM_READY_CONTRACT_WRITTEN",
        "schema_version": "1",
        "ready_contract_kind": "chrome_uploader_downstream_ready_contract",
        "expected_browser": "chrome",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_consumed_sha256": "consumed-hash",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "consumed_result": "PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER",
        "acceptance_result": "PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND",
        "no_send_verified": True,
        "attachment_verified": True,
        "downstream_contract_accepted": True,
        "safe_for_downstream_planning": True,
        "read_only_contract": True,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "raw_conversation_text_available": False,
        "forbidden_true_flags": [],
        "allowed_next_actions": ["read_acceptance_summary", "plan_downstream_orchestration"],
        "forbidden_next_actions": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
    }
    payload.update(overrides)
    return payload


def test_ready_contract_without_confirmation_writes_safe_blocked_boundary() -> None:
    boundary = validate_ready_contract_payload(_ready())

    assert boundary.ok is False
    assert boundary.result == BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED
    assert boundary.boundary_kind == BOUNDARY_KIND
    assert boundary.confirmation_required is True
    assert boundary.required_confirmation_text == REQUIRED_CONFIRMATION_TEXT
    assert boundary.boundary_confirmed is False
    assert boundary.live_action_allowed is False
    assert boundary.send_allowed is False
    assert boundary.browser_action_performed is False
    assert boundary.chatgpt_submit_performed is False
    assert boundary.raw_conversation_text_available is False
    assert "send_chatgpt_message" in boundary.always_forbidden


def test_ready_contract_with_confirmation_allows_future_live_boundary_only() -> None:
    boundary = validate_ready_contract_payload(_ready(), confirmation_text=REQUIRED_CONFIRMATION_TEXT)

    assert boundary.ok is True
    assert boundary.result == PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED
    assert boundary.boundary_confirmed is True
    assert boundary.live_action_allowed is True
    assert boundary.send_allowed is False
    assert boundary.browser_action_performed is False
    assert boundary.chatgpt_submit_performed is False
    assert boundary.raw_conversation_text_available is False
    assert "focus_existing_chrome_window" in boundary.allowed_with_confirmation
    assert "send_chatgpt_message" in boundary.always_forbidden


def test_ready_contract_blocks_unsupported_kind() -> None:
    boundary = validate_ready_contract_payload(_ready(ready_contract_kind="edge_ready_contract"), confirmation_text=REQUIRED_CONFIRMATION_TEXT)

    assert boundary.ok is False
    assert boundary.result == BLOCKED_LIVE_BOUNDARY_UNSUPPORTED_KIND
    assert boundary.live_action_allowed is False


def test_ready_contract_blocks_not_ready() -> None:
    boundary = validate_ready_contract_payload(_ready(ok=False, safe_for_downstream_planning=False), confirmation_text=REQUIRED_CONFIRMATION_TEXT)

    assert boundary.ok is False
    assert boundary.result == BLOCKED_LIVE_BOUNDARY_NOT_READY
    assert boundary.live_action_allowed is False
    assert "safe_for_downstream_planning" in boundary.reason


def test_ready_contract_blocks_forbidden_flags() -> None:
    boundary = validate_ready_contract_payload(_ready(webdriver_used=True), confirmation_text=REQUIRED_CONFIRMATION_TEXT)

    assert boundary.ok is False
    assert boundary.result == BLOCKED_LIVE_BOUNDARY_UNSAFE
    assert "webdriver_used" in boundary.forbidden_true_flags
    assert boundary.live_action_allowed is False


def test_forbidden_flags_reads_top_level_flags() -> None:
    payload = _ready(raw_conversation_text_available=True)

    assert "raw_conversation_text_available" in forbidden_flags(payload)


def test_load_and_validate_ready_contract_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_ready_contract(tmp_path / "missing.json", confirmation_text=REQUIRED_CONFIRMATION_TEXT)
    assert missing.result == BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_MISSING
    assert missing.live_action_allowed is False
    assert missing.browser_action_performed is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_ready_contract(bad, confirmation_text=REQUIRED_CONFIRMATION_TEXT)
    assert invalid.result == BLOCKED_LIVE_BOUNDARY_READY_CONTRACT_INVALID_JSON
    assert invalid.source_ready_sha256
    assert invalid.live_action_allowed is False


def test_write_boundary_and_marker(tmp_path: Path) -> None:
    boundary = validate_ready_contract_payload(_ready(), source_ready_basename="ready.json", source_ready_sha256="hash", confirmation_text=REQUIRED_CONFIRMATION_TEXT)
    boundary_path = write_live_action_boundary(boundary, tmp_path / "handoff" / "latest_uploader_live_action_boundary.json")
    marker_path = write_live_action_boundary_marker(boundary, tmp_path / "handoff" / "boundary.txt")

    payload = json.loads(boundary_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED
    assert payload["write_result"] == PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN
    assert payload["boundary_kind"] == BOUNDARY_KIND
    assert payload["live_action_allowed"] is True
    assert payload["browser_action_performed"] is False
    assert "live_action_allowed:true" in marker
    assert "chatgpt_submit_performed:false" in marker
    assert "raw_conversation_text_logged:false" in marker


def test_live_action_boundary_script_blocks_without_confirmation(tmp_path: Path) -> None:
    ready = tmp_path / "latest_uploader_ready_contract.json"
    ready.write_text(json.dumps(_ready(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    boundary = tmp_path / "boundary.json"
    marker = tmp_path / "boundary.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_explicit_live_action_boundary.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--ready-contract-json",
            str(ready),
            "--boundary-json",
            str(boundary),
            "--boundary-marker",
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
    assert payload["result"] == BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED
    assert payload["live_action_allowed"] is False
    assert payload["browser_action_performed"] is False
    saved = json.loads(boundary.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED
    assert marker.exists()


def test_live_action_boundary_script_validates_with_confirmation(tmp_path: Path) -> None:
    ready = tmp_path / "latest_uploader_ready_contract.json"
    ready.write_text(json.dumps(_ready(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    boundary = tmp_path / "boundary.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_explicit_live_action_boundary.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--ready-contract-json",
            str(ready),
            "--boundary-json",
            str(boundary),
            "--confirm-live-action-text",
            REQUIRED_CONFIRMATION_TEXT,
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
    assert payload["result"] == PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED
    assert payload["boundary_confirmed"] is True
    assert payload["live_action_allowed"] is True
    assert payload["send_allowed"] is False
    assert payload["browser_action_performed"] is False
    saved = json.loads(boundary.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_WRITTEN


def test_live_action_boundary_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_explicit_live_action_boundary.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_explicit_live_action_boundary_validated" in text
    assert "blocked_live_boundary_confirmation_required" in text
    assert "patchops_confirm_chrome_live_no_send_action" in text
    assert "latest_uploader_ready_contract.json" in text
    assert "latest_uploader_live_action_boundary.json" in text
    assert "send_allowed: false" in text
    assert "browser_action_performed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_live_action_boundary_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_live_action_boundary_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_explicit_live_action_boundary.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_explicit_live_action_boundary.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text