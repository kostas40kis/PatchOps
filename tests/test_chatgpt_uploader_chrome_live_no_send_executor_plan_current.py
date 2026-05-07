from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_live_no_send_executor_plan import (
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND,
    PLAN_KIND,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN,
    forbidden_flags,
    load_and_validate_preflight_contract,
    validate_preflight_contract_payload,
    write_executor_plan,
    write_executor_plan_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _contract(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED",
        "write_result": "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_WRITTEN",
        "schema_version": "1",
        "contract_kind": "chrome_uploader_live_no_send_preflight_contract",
        "expected_browser": "chrome",
        "source_packet_basename": "latest_uploader_live_instruction_packet.json",
        "source_packet_sha256": "packet-hash",
        "source_boundary_basename": "latest_uploader_live_action_boundary.json",
        "source_ready_basename": "latest_uploader_ready_contract.json",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "packet_kind": "chrome_uploader_live_instruction_packet_no_action",
        "packet_result": "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED",
        "boundary_kind": "chrome_uploader_explicit_live_action_boundary",
        "boundary_result": "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED",
        "preflight_contract_ready": True,
        "no_send_verified": True,
        "attachment_verified": True,
        "safe_for_downstream_planning": True,
        "packet_performs_browser_action": False,
        "packet_performs_chatgpt_submit": False,
        "packet_reads_conversation_text": False,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "send_allowed": False,
        "raw_conversation_text_available": False,
        "human_must_confirm_visible_chrome": True,
        "human_must_verify_no_send": True,
        "required_visible_state": ["visible_existing_chrome_window", "correct_target_conversation_already_open"],
        "permitted_future_actions": ["focus_existing_chrome_window", "verify_attachment_chip_no_send"],
        "forbidden_actions": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
        "stop_conditions": ["visible_chrome_target_missing", "cloudflare_or_captcha_detected"],
        "allowed_next_script": "scripts/run_uploader_chrome_live_no_send_executor.py",
        "forbidden_true_flags": [],
    }
    payload.update(overrides)
    return payload


def test_validate_preflight_contract_payload_writes_executor_plan_no_action() -> None:
    plan = validate_preflight_contract_payload(_contract(), source_contract_basename="contract.json", source_contract_sha256="hash")

    assert plan.ok is True
    assert plan.result == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED
    assert plan.plan_kind == PLAN_KIND
    assert plan.expected_browser == "chrome"
    assert plan.contract_kind == "chrome_uploader_live_no_send_preflight_contract"
    assert plan.contract_result == "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED"
    assert plan.executor_plan_ready is True
    assert plan.no_send_verified is True
    assert plan.attachment_verified is True
    assert plan.safe_for_downstream_planning is True
    assert plan.human_supervision_required is True
    assert plan.executor_plan_performs_browser_action is False
    assert plan.executor_plan_performs_chatgpt_submit is False
    assert plan.executor_plan_reads_conversation_text is False
    assert plan.browser_action_performed is False
    assert plan.chatgpt_submit_performed is False
    assert plan.send_allowed is False
    assert plan.raw_conversation_text_available is False
    assert "confirm_visible_existing_chrome_window" in plan.execution_steps
    assert "future_executor_stop_before_send" in plan.execution_steps
    assert "any_request_to_press_send" in plan.executor_stop_conditions
    assert plan.allowed_next_script == "scripts/run_uploader_chrome_live_no_send_executor.py"


def test_validate_preflight_contract_payload_blocks_unsupported_kind() -> None:
    plan = validate_preflight_contract_payload(_contract(contract_kind="edge_preflight_contract"))

    assert plan.ok is False
    assert plan.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSUPPORTED_KIND
    assert plan.executor_plan_ready is False


def test_validate_preflight_contract_payload_blocks_not_ready() -> None:
    plan = validate_preflight_contract_payload(_contract(ok=False, preflight_contract_ready=False, no_send_verified=False))

    assert plan.ok is False
    assert plan.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_NOT_READY
    assert "preflight_contract_ready" in plan.reason
    assert plan.executor_plan_ready is False
    assert plan.browser_action_performed is False


def test_validate_preflight_contract_payload_blocks_unsafe_flags() -> None:
    plan = validate_preflight_contract_payload(_contract(browser_action_performed=True))

    assert plan.ok is False
    assert plan.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE
    assert "browser_action_performed" in plan.forbidden_true_flags
    assert plan.executor_plan_performs_browser_action is False

    executor_flag = validate_preflight_contract_payload(_contract(executor_plan_performs_chatgpt_submit=True))
    assert executor_flag.ok is False
    assert executor_flag.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE
    assert "executor_plan_performs_chatgpt_submit" in executor_flag.forbidden_true_flags


def test_forbidden_flags_reads_safety_flags() -> None:
    payload = _contract()
    payload["safety_flags"] = {"webdriver_used": True}

    assert "webdriver_used" in forbidden_flags(payload)


def test_load_and_validate_preflight_contract_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_preflight_contract(tmp_path / "missing.json")
    assert missing.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_MISSING
    assert missing.browser_action_performed is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_preflight_contract(bad)
    assert invalid.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_CONTRACT_INVALID_JSON
    assert invalid.source_contract_sha256
    assert invalid.browser_action_performed is False


def test_write_executor_plan_and_marker(tmp_path: Path) -> None:
    plan = validate_preflight_contract_payload(_contract(), source_contract_basename="contract.json", source_contract_sha256="hash")
    plan_path = write_executor_plan(plan, tmp_path / "handoff" / "latest_uploader_live_no_send_executor_plan.json")
    marker_path = write_executor_plan_marker(plan, tmp_path / "handoff" / "plan.txt")

    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED
    assert payload["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN
    assert payload["plan_kind"] == PLAN_KIND
    assert payload["executor_plan_ready"] is True
    assert payload["executor_plan_performs_browser_action"] is False
    assert "executor_plan_ready:true" in marker
    assert "executor_plan_performs_browser_action:false" in marker
    assert "raw_conversation_text_logged:false" in marker


def test_executor_plan_script_writes_plan(tmp_path: Path) -> None:
    contract = tmp_path / "latest_uploader_live_no_send_preflight_contract.json"
    contract.write_text(json.dumps(_contract(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = tmp_path / "latest_uploader_live_no_send_executor_plan.json"
    marker = tmp_path / "plan.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_plan.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--contract-json",
            str(contract),
            "--plan-json",
            str(plan),
            "--plan-marker",
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
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED
    assert payload["executor_plan_ready"] is True
    assert payload["executor_plan_performs_browser_action"] is False
    assert payload["executor_plan_performs_chatgpt_submit"] is False
    assert payload["send_allowed"] is False
    saved = json.loads(plan.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN
    assert marker.exists()


def test_executor_plan_script_blocks_unsafe_contract(tmp_path: Path) -> None:
    contract = tmp_path / "latest_uploader_live_no_send_preflight_contract.json"
    contract.write_text(json.dumps(_contract(webdriver_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    plan = tmp_path / "plan.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_plan.py"

    result = subprocess.run(
        [sys.executable, str(script), "--contract-json", str(contract), "--plan-json", str(plan), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]
    saved = json.loads(plan.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_PLAN_UNSAFE


def test_executor_plan_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_no_send_executor_plan.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_live_no_send_executor_plan_validated" in text
    assert "latest_uploader_live_no_send_preflight_contract.json" in text
    assert "latest_uploader_live_no_send_executor_plan.json" in text
    assert "chrome_uploader_live_no_send_executor_plan" in text
    assert "executor_plan_ready: true" in text
    assert "executor_plan_performs_browser_action: false" in text
    assert "send_allowed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_executor_plan_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_executor_plan_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_live_no_send_executor_plan.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_plan.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text