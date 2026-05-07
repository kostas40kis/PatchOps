from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_live_no_send_executor_manual_probe_contract import (
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND,
    CONFIRMATION_TEXT,
    CONTRACT_KIND,
    FUTURE_EXECUTOR_COMMAND_TEMPLATE,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN,
    forbidden_flags,
    load_and_validate_executor_dry_run,
    validate_executor_dry_run_payload,
    write_manual_probe_contract,
    write_manual_probe_contract_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _dry_run(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED",
        "write_result": "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN",
        "schema_version": "1",
        "dry_run_kind": "chrome_uploader_live_no_send_executor_dry_run",
        "expected_browser": "chrome",
        "source_plan_basename": "latest_uploader_live_no_send_executor_plan.json",
        "source_plan_sha256": "plan-hash",
        "source_contract_basename": "latest_uploader_live_no_send_preflight_contract.json",
        "source_packet_basename": "latest_uploader_live_instruction_packet.json",
        "source_boundary_basename": "latest_uploader_live_action_boundary.json",
        "source_ready_basename": "latest_uploader_ready_contract.json",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "plan_kind": "chrome_uploader_live_no_send_executor_plan",
        "plan_result": "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED",
        "dry_run_ready": True,
        "executor_plan_ready": True,
        "no_send_verified": True,
        "attachment_verified": True,
        "safe_for_downstream_planning": True,
        "human_supervision_required": True,
        "human_must_confirm_visible_chrome": True,
        "human_must_verify_no_send": True,
        "dry_run_performs_browser_action": False,
        "dry_run_performs_chatgpt_submit": False,
        "dry_run_reads_conversation_text": False,
        "executor_dry_run_performed_live_action": False,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "send_allowed": False,
        "raw_conversation_text_available": False,
        "dry_run_checklist": [
            "operator_confirms_existing_chrome_visible",
            "operator_confirms_target_conversation_already_open",
        ],
        "stop_conditions": ["visible_chrome_target_missing", "send_button_focus_or_submit_risk"],
        "forbidden_actions": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
        "allowed_next_script": "scripts/run_uploader_chrome_live_no_send_executor.py",
        "forbidden_true_flags": [],
    }
    payload.update(overrides)
    return payload


def test_validate_executor_dry_run_payload_writes_manual_probe_contract() -> None:
    contract = validate_executor_dry_run_payload(_dry_run(), source_dry_run_basename="dry_run.json", source_dry_run_sha256="hash")

    assert contract.ok is True
    assert contract.result == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED
    assert contract.contract_kind == CONTRACT_KIND
    assert contract.expected_browser == "chrome"
    assert contract.manual_probe_contract_ready is True
    assert contract.dry_run_ready is True
    assert contract.executor_plan_ready is True
    assert contract.no_send_verified is True
    assert contract.attachment_verified is True
    assert contract.safe_for_downstream_planning is True
    assert contract.explicit_confirmation_required is True
    assert contract.confirmation_text == CONFIRMATION_TEXT
    assert contract.manual_probe_contract_performs_browser_action is False
    assert contract.manual_probe_contract_performs_chatgpt_submit is False
    assert contract.manual_probe_contract_reads_conversation_text is False
    assert contract.manual_probe_contract_performed_live_action is False
    assert contract.browser_action_performed is False
    assert contract.chatgpt_submit_performed is False
    assert contract.send_allowed is False
    assert contract.raw_conversation_text_available is False
    assert "operator_confirms_chatgpt_composer_visible" in contract.human_visible_preflight_checklist
    assert FUTURE_EXECUTOR_COMMAND_TEMPLATE == contract.future_executor_command_template
    assert "--stop-before-send" in contract.future_executor_command_template


def test_validate_executor_dry_run_payload_blocks_unsupported_kind() -> None:
    contract = validate_executor_dry_run_payload(_dry_run(dry_run_kind="edge_dry_run"))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSUPPORTED_KIND
    assert contract.manual_probe_contract_ready is False


def test_validate_executor_dry_run_payload_blocks_not_ready() -> None:
    contract = validate_executor_dry_run_payload(_dry_run(ok=False, dry_run_ready=False, no_send_verified=False))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY
    assert "dry_run_ready" in contract.reason
    assert contract.browser_action_performed is False


def test_validate_executor_dry_run_payload_blocks_wrong_next_script() -> None:
    contract = validate_executor_dry_run_payload(_dry_run(allowed_next_script="scripts/run_uploader_edge.py"))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_NOT_READY
    assert "allowed_next_script" in contract.reason


def test_validate_executor_dry_run_payload_blocks_unsafe_flags() -> None:
    contract = validate_executor_dry_run_payload(_dry_run(browser_action_performed=True))

    assert contract.ok is False
    assert contract.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE
    assert "browser_action_performed" in contract.forbidden_true_flags
    assert contract.manual_probe_contract_performs_browser_action is False

    manual_flag = validate_executor_dry_run_payload(_dry_run(manual_probe_contract_performs_chatgpt_submit=True))
    assert manual_flag.ok is False
    assert manual_flag.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE
    assert "manual_probe_contract_performs_chatgpt_submit" in manual_flag.forbidden_true_flags


def test_forbidden_flags_reads_safety_flags() -> None:
    payload = _dry_run()
    payload["safety_flags"] = {"webdriver_used": True}

    assert "webdriver_used" in forbidden_flags(payload)


def test_load_and_validate_executor_dry_run_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_executor_dry_run(tmp_path / "missing.json")
    assert missing.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_MISSING
    assert missing.browser_action_performed is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_executor_dry_run(bad)
    assert invalid.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_DRY_RUN_INVALID_JSON
    assert invalid.source_dry_run_sha256
    assert invalid.browser_action_performed is False


def test_write_manual_probe_contract_and_marker(tmp_path: Path) -> None:
    contract = validate_executor_dry_run_payload(_dry_run(), source_dry_run_basename="dry_run.json", source_dry_run_sha256="hash")
    contract_path = write_manual_probe_contract(contract, tmp_path / "handoff" / "latest_uploader_live_no_send_executor_manual_probe_contract.json")
    marker_path = write_manual_probe_contract_marker(contract, tmp_path / "handoff" / "manual_probe.txt")

    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED
    assert payload["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN
    assert payload["contract_kind"] == CONTRACT_KIND
    assert payload["manual_probe_contract_ready"] is True
    assert payload["manual_probe_contract_performs_browser_action"] is False
    assert "manual_probe_contract_ready:true" in marker
    assert "manual_probe_contract_performs_browser_action:false" in marker
    assert "raw_conversation_text_logged:false" in marker
    assert "PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE" in marker


def test_manual_probe_contract_script_writes_contract(tmp_path: Path) -> None:
    dry_run = tmp_path / "latest_uploader_live_no_send_executor_dry_run.json"
    dry_run.write_text(json.dumps(_dry_run(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract = tmp_path / "latest_uploader_live_no_send_executor_manual_probe_contract.json"
    marker = tmp_path / "manual_probe.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_manual_probe_contract.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--dry-run-json",
            str(dry_run),
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
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED
    assert payload["manual_probe_contract_ready"] is True
    assert payload["manual_probe_contract_performs_browser_action"] is False
    assert payload["manual_probe_contract_performs_chatgpt_submit"] is False
    assert payload["send_allowed"] is False
    assert payload["future_executor_command_template"] == FUTURE_EXECUTOR_COMMAND_TEMPLATE
    saved = json.loads(contract.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_WRITTEN
    assert marker.exists()


def test_manual_probe_contract_script_blocks_unsafe_dry_run(tmp_path: Path) -> None:
    dry_run = tmp_path / "latest_uploader_live_no_send_executor_dry_run.json"
    dry_run.write_text(json.dumps(_dry_run(webdriver_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contract = tmp_path / "manual_probe.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_manual_probe_contract.py"

    result = subprocess.run(
        [sys.executable, str(script), "--dry-run-json", str(dry_run), "--contract-json", str(contract), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]
    saved = json.loads(contract.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_UNSAFE


def test_manual_probe_contract_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_no_send_executor_manual_probe_contract.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_live_no_send_executor_manual_probe_contract_validated" in text
    assert "latest_uploader_live_no_send_executor_dry_run.json" in text
    assert "latest_uploader_live_no_send_executor_manual_probe_contract.json" in text
    assert "chrome_uploader_live_no_send_executor_manual_probe_contract" in text
    assert "manual_probe_contract_ready: true" in text
    assert "manual_probe_contract_performs_browser_action: false" in text
    assert "patchops_confirm_chrome_live_no_send_executor_manual_probe" in text
    assert "--stop-before-send" in text
    assert "send_allowed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_manual_probe_contract_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_manual_probe_contract_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_live_no_send_executor_manual_probe_contract.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_manual_probe_contract.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text