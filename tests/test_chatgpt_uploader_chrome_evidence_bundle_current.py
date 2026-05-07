from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_evidence_bundle import (
    BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON,
    BLOCKED_EVIDENCE_BUNDLE_MISSING,
    BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT,
    BLOCKED_EVIDENCE_BUNDLE_UNSAFE,
    PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN,
    PASS_EVIDENCE_BUNDLE_VALIDATED,
    load_and_validate_flow_evidence,
    validate_flow_evidence_payload,
    write_evidence_bundle,
    write_evidence_summary_text,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _flow_payload(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT",
        "expected_browser": "chrome",
        "attachment_confirmed": True,
        "send_gate_ready": True,
        "submit_adapter_ready": True,
        "submit_action_requested": False,
        "submit_action_performed": False,
        "chatgpt_submit_performed": False,
        "send_button_pressed": False,
        "raw_conversation_text_logged": False,
        "conversation_text_logged": False,
        "live_browser_used": False,
        "canonical_report_basename": "operator_report.txt",
        "canonical_report_path_hash": "abc123",
        "safety_flags": {
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "cloudflare_bypass_attempted": False,
            "captcha_bypass_attempted": False,
            "conversation_text_logged": False,
            "raw_conversation_text_logged": False,
            "random_page_click_performed": False,
            "orchestrator_used": True,
        },
    }
    payload.update(overrides)
    return payload


def test_validate_flow_evidence_payload_accepts_ready_no_submit() -> None:
    bundle = validate_flow_evidence_payload(_flow_payload(), evidence_basename="flow.json", evidence_path_hash="hash")

    assert bundle.ok is True
    assert bundle.result == PASS_EVIDENCE_BUNDLE_VALIDATED
    assert bundle.flow_result == "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT"
    assert bundle.attachment_confirmed is True
    assert bundle.send_gate_ready is True
    assert bundle.submit_adapter_ready is True
    assert bundle.submit_action_performed is False
    assert bundle.chatgpt_submit_performed is False
    assert bundle.raw_conversation_text_logged is False
    assert bundle.conversation_text_logged is False
    assert bundle.forbidden_true_flags == []
    assert any("selenium_used:false" in line for line in bundle.summary_lines)


def test_validate_flow_evidence_payload_accepts_submit_performed_with_safe_flags() -> None:
    bundle = validate_flow_evidence_payload(
        _flow_payload(
            result="PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED",
            submit_action_requested=True,
            submit_action_performed=True,
            chatgpt_submit_performed=True,
        )
    )

    assert bundle.ok is True
    assert bundle.result == PASS_EVIDENCE_BUNDLE_VALIDATED
    assert bundle.submit_action_requested is True
    assert bundle.submit_action_performed is True
    assert bundle.chatgpt_submit_performed is True


def test_validate_flow_evidence_payload_blocks_forbidden_true_safety_flag() -> None:
    payload = _flow_payload()
    payload["safety_flags"]["selenium_used"] = True
    bundle = validate_flow_evidence_payload(payload)

    assert bundle.ok is False
    assert bundle.result == BLOCKED_EVIDENCE_BUNDLE_UNSAFE
    assert "selenium_used" in bundle.forbidden_true_flags


def test_validate_flow_evidence_payload_blocks_raw_conversation_logging() -> None:
    payload = _flow_payload(raw_conversation_text_logged=True)
    bundle = validate_flow_evidence_payload(payload)

    assert bundle.ok is False
    assert bundle.result == BLOCKED_EVIDENCE_BUNDLE_UNSAFE
    assert "raw_conversation_text_logged" in bundle.forbidden_true_flags


def test_validate_flow_evidence_payload_blocks_unrecognized_result() -> None:
    bundle = validate_flow_evidence_payload(_flow_payload(result="PASS_UNKNOWN"))

    assert bundle.ok is False
    assert bundle.result == BLOCKED_EVIDENCE_BUNDLE_UNRECOGNIZED_RESULT


def test_load_and_validate_flow_evidence_missing_file(tmp_path: Path) -> None:
    bundle = load_and_validate_flow_evidence(tmp_path / "missing.json")

    assert bundle.ok is False
    assert bundle.result == BLOCKED_EVIDENCE_BUNDLE_MISSING


def test_load_and_validate_flow_evidence_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{bad-json", encoding="utf-8")
    bundle = load_and_validate_flow_evidence(path)

    assert bundle.ok is False
    assert bundle.result == BLOCKED_EVIDENCE_BUNDLE_INVALID_JSON
    assert bundle.evidence_basename == "bad.json"
    assert bundle.evidence_path_hash


def test_write_evidence_bundle_and_summary_text(tmp_path: Path) -> None:
    bundle = validate_flow_evidence_payload(_flow_payload(), evidence_basename="flow.json", evidence_path_hash="hash")
    bundle_path = write_evidence_bundle(bundle, tmp_path / "bundle" / "bundle.json")
    summary_path = write_evidence_summary_text(bundle, tmp_path / "bundle" / "summary.txt")

    bundle_payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle_payload["result"] == PASS_EVIDENCE_BUNDLE_VALIDATED
    assert bundle_payload["write_result"] == PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN

    summary_text = summary_path.read_text(encoding="utf-8")
    assert "Chrome upload flow evidence summary" in summary_text
    assert "raw_conversation_text_logged:false" in summary_text
    assert "webdriver_used:false" in summary_text


def test_evidence_bundle_script_validates_flow_file(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow.json"
    flow_path.write_text(json.dumps(_flow_payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bundle_path = tmp_path / "bundle.json"
    summary_path = tmp_path / "summary.txt"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_evidence_bundle.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--flow-evidence",
            str(flow_path),
            "--bundle-json",
            str(bundle_path),
            "--summary-txt",
            str(summary_path),
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
    assert payload["result"] == PASS_EVIDENCE_BUNDLE_VALIDATED
    assert payload["forbidden_true_flags"] == []
    assert bundle_path.exists()
    assert summary_path.exists()
    assert "Chrome upload flow evidence summary" in summary_path.read_text(encoding="utf-8")


def test_evidence_bundle_script_blocks_unsafe_flow_file(tmp_path: Path) -> None:
    payload = _flow_payload()
    payload["safety_flags"]["webdriver_used"] = True
    flow_path = tmp_path / "flow.json"
    flow_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_evidence_bundle.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--flow-evidence",
            str(flow_path),
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
    assert payload["result"] == BLOCKED_EVIDENCE_BUNDLE_UNSAFE
    assert "webdriver_used" in payload["forbidden_true_flags"]


def test_chrome_evidence_bundle_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_evidence_bundle_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_evidence_bundle.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_evidence_bundle.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text