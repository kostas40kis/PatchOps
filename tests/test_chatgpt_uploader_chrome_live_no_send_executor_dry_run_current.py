from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_live_no_send_executor_dry_run import (
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE,
    BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND,
    DRY_RUN_KIND,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED,
    PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN,
    forbidden_flags,
    load_and_validate_executor_plan,
    validate_executor_plan_payload,
    write_executor_dry_run,
    write_executor_dry_run_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _plan(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED",
        "write_result": "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_WRITTEN",
        "schema_version": "1",
        "plan_kind": "chrome_uploader_live_no_send_executor_plan",
        "expected_browser": "chrome",
        "source_contract_basename": "latest_uploader_live_no_send_preflight_contract.json",
        "source_contract_sha256": "contract-hash",
        "source_packet_basename": "latest_uploader_live_instruction_packet.json",
        "source_boundary_basename": "latest_uploader_live_action_boundary.json",
        "source_ready_basename": "latest_uploader_ready_contract.json",
        "source_consumed_basename": "latest_uploader_acceptance_consumed.json",
        "source_handoff_basename": "latest_uploader_acceptance.json",
        "source_acceptance_basename": "accepted.json",
        "contract_kind": "chrome_uploader_live_no_send_preflight_contract",
        "contract_result": "PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED",
        "packet_kind": "chrome_uploader_live_instruction_packet_no_action",
        "packet_result": "PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED",
        "boundary_kind": "chrome_uploader_explicit_live_action_boundary",
        "boundary_result": "PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED",
        "executor_plan_ready": True,
        "no_send_verified": True,
        "attachment_verified": True,
        "safe_for_downstream_planning": True,
        "human_supervision_required": True,
        "human_must_confirm_visible_chrome": True,
        "human_must_verify_no_send": True,
        "executor_plan_performs_browser_action": False,
        "executor_plan_performs_chatgpt_submit": False,
        "executor_plan_reads_conversation_text": False,
        "browser_action_performed": False,
        "chatgpt_submit_performed": False,
        "send_allowed": False,
        "raw_conversation_text_available": False,
        "required_visible_state": ["visible_existing_chrome_window", "correct_target_conversation_already_open"],
        "execution_steps": ["confirm_visible_existing_chrome_window", "future_executor_stop_before_send"],
        "executor_stop_conditions": ["visible_chrome_target_missing", "send_button_focus_or_submit_risk"],
        "forbidden_actions": ["send_chatgpt_message", "read_conversation_text", "use_webdriver"],
        "allowed_next_script": "scripts/run_uploader_chrome_live_no_send_executor.py",
        "forbidden_true_flags": [],
    }
    payload.update(overrides)
    return payload


def test_validate_executor_plan_payload_writes_dry_run_no_action() -> None:
    dry_run = validate_executor_plan_payload(_plan(), source_plan_basename="plan.json", source_plan_sha256="hash")

    assert dry_run.ok is True
    assert dry_run.result == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED
    assert dry_run.dry_run_kind == DRY_RUN_KIND
    assert dry_run.expected_browser == "chrome"
    assert dry_run.plan_kind == "chrome_uploader_live_no_send_executor_plan"
    assert dry_run.plan_result == "PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED"
    assert dry_run.dry_run_ready is True
    assert dry_run.executor_plan_ready is True
    assert dry_run.no_send_verified is True
    assert dry_run.attachment_verified is True
    assert dry_run.safe_for_downstream_planning is True
    assert dry_run.human_supervision_required is True
    assert dry_run.dry_run_performs_browser_action is False
    assert dry_run.dry_run_performs_chatgpt_submit is False
    assert dry_run.dry_run_reads_conversation_text is False
    assert dry_run.executor_dry_run_performed_live_action is False
    assert dry_run.browser_action_performed is False
    assert dry_run.chatgpt_submit_performed is False
    assert dry_run.send_allowed is False
    assert dry_run.raw_conversation_text_available is False
    assert "operator_confirms_existing_chrome_visible" in dry_run.dry_run_checklist
    assert "future_executor_stop_before_send" in dry_run.execution_steps
    assert "any_request_to_press_send" in dry_run.stop_conditions
    assert dry_run.allowed_next_script == "scripts/run_uploader_chrome_live_no_send_executor.py"


def test_validate_executor_plan_payload_blocks_unsupported_kind() -> None:
    dry_run = validate_executor_plan_payload(_plan(plan_kind="edge_executor_plan"))

    assert dry_run.ok is False
    assert dry_run.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSUPPORTED_KIND
    assert dry_run.dry_run_ready is False


def test_validate_executor_plan_payload_blocks_not_ready() -> None:
    dry_run = validate_executor_plan_payload(_plan(ok=False, executor_plan_ready=False, no_send_verified=False))

    assert dry_run.ok is False
    assert dry_run.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY
    assert "executor_plan_ready" in dry_run.reason
    assert dry_run.dry_run_ready is False
    assert dry_run.browser_action_performed is False


def test_validate_executor_plan_payload_blocks_wrong_next_script() -> None:
    dry_run = validate_executor_plan_payload(_plan(allowed_next_script="scripts/run_uploader_edge.py"))

    assert dry_run.ok is False
    assert dry_run.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_NOT_READY
    assert "allowed_next_script" in dry_run.reason


def test_validate_executor_plan_payload_blocks_unsafe_flags() -> None:
    dry_run = validate_executor_plan_payload(_plan(browser_action_performed=True))

    assert dry_run.ok is False
    assert dry_run.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE
    assert "browser_action_performed" in dry_run.forbidden_true_flags
    assert dry_run.dry_run_performs_browser_action is False

    dry_run_flag = validate_executor_plan_payload(_plan(dry_run_performs_chatgpt_submit=True))
    assert dry_run_flag.ok is False
    assert dry_run_flag.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE
    assert "dry_run_performs_chatgpt_submit" in dry_run_flag.forbidden_true_flags


def test_forbidden_flags_reads_safety_flags() -> None:
    payload = _plan()
    payload["safety_flags"] = {"webdriver_used": True}

    assert "webdriver_used" in forbidden_flags(payload)


def test_load_and_validate_executor_plan_missing_and_invalid(tmp_path: Path) -> None:
    missing = load_and_validate_executor_plan(tmp_path / "missing.json")
    assert missing.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_MISSING
    assert missing.browser_action_performed is False

    bad = tmp_path / "bad.json"
    bad.write_text("{bad", encoding="utf-8")
    invalid = load_and_validate_executor_plan(bad)
    assert invalid.result == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_PLAN_INVALID_JSON
    assert invalid.source_plan_sha256
    assert invalid.browser_action_performed is False


def test_write_executor_dry_run_and_marker(tmp_path: Path) -> None:
    dry_run = validate_executor_plan_payload(_plan(), source_plan_basename="plan.json", source_plan_sha256="hash")
    dry_run_path = write_executor_dry_run(dry_run, tmp_path / "handoff" / "latest_uploader_live_no_send_executor_dry_run.json")
    marker_path = write_executor_dry_run_marker(dry_run, tmp_path / "handoff" / "dry_run.txt")

    payload = json.loads(dry_run_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED
    assert payload["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN
    assert payload["dry_run_kind"] == DRY_RUN_KIND
    assert payload["dry_run_ready"] is True
    assert payload["dry_run_performs_browser_action"] is False
    assert "dry_run_ready:true" in marker
    assert "dry_run_performs_browser_action:false" in marker
    assert "executor_dry_run_performed_live_action:false" in marker
    assert "raw_conversation_text_logged:false" in marker


def test_executor_dry_run_script_writes_dry_run(tmp_path: Path) -> None:
    plan = tmp_path / "latest_uploader_live_no_send_executor_plan.json"
    plan.write_text(json.dumps(_plan(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    dry_run = tmp_path / "latest_uploader_live_no_send_executor_dry_run.json"
    marker = tmp_path / "dry_run.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_dry_run.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--plan-json",
            str(plan),
            "--dry-run-json",
            str(dry_run),
            "--dry-run-marker",
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
    assert payload["result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED
    assert payload["dry_run_ready"] is True
    assert payload["dry_run_performs_browser_action"] is False
    assert payload["dry_run_performs_chatgpt_submit"] is False
    assert payload["send_allowed"] is False
    saved = json.loads(dry_run.read_text(encoding="utf-8"))
    assert saved["write_result"] == PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_WRITTEN
    assert marker.exists()


def test_executor_dry_run_script_blocks_unsafe_plan(tmp_path: Path) -> None:
    plan = tmp_path / "latest_uploader_live_no_send_executor_plan.json"
    plan.write_text(json.dumps(_plan(webdriver_used=True), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    dry_run = tmp_path / "dry_run.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_dry_run.py"

    result = subprocess.run(
        [sys.executable, str(script), "--plan-json", str(plan), "--dry-run-json", str(dry_run), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]
    saved = json.loads(dry_run.read_text(encoding="utf-8"))
    assert saved["write_result"] == BLOCKED_LIVE_NO_SEND_EXECUTOR_DRY_RUN_UNSAFE


def test_executor_dry_run_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_no_send_executor_dry_run.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_live_no_send_executor_dry_run_validated" in text
    assert "latest_uploader_live_no_send_executor_plan.json" in text
    assert "latest_uploader_live_no_send_executor_dry_run.json" in text
    assert "chrome_uploader_live_no_send_executor_dry_run" in text
    assert "dry_run_ready: true" in text
    assert "dry_run_performs_browser_action: false" in text
    assert "executor_dry_run_performed_live_action: false" in text
    assert "send_allowed: false" in text
    assert "webdriver" in text
    assert "raw_conversation_text_logged" in text


def test_chrome_executor_dry_run_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_executor_dry_run_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_live_no_send_executor_dry_run.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_live_no_send_executor_dry_run.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text