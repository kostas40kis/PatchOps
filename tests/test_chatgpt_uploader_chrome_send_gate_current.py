from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_attachment_verifier import (
    PASS_ATTACHMENT_CONFIRMED_NO_SEND,
    build_attachment_candidate,
    verify_attachment_no_send,
    write_attachment_verification_evidence,
)
from patchops.chatgpt_uploader.chrome_send_gate import (
    BLOCKED_ATTACHMENT_NOT_CONFIRMED,
    BLOCKED_SEND_ACTION_NOT_IMPLEMENTED,
    BLOCKED_SEND_CONFIRMATION_MISSING,
    LIVE_CONFIRM_TEXT,
    PASS_SEND_READY_NO_SUBMIT,
    evaluate_send_gate_no_submit,
    write_send_gate_decision,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PatchOps operator report\n=======================\nfinal result      : PASS\nSafety flags\n------------\n",
        encoding="utf-8",
    )
    return path


def _attachment_evidence(report: Path):
    return verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_candidate(basename=report.name)],
    )


def test_send_gate_ready_no_submit_after_confirmed_attachment(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment = _attachment_evidence(report)
    decision = evaluate_send_gate_no_submit(canonical_report_path=report, attachment_evidence=attachment)

    assert attachment.result == PASS_ATTACHMENT_CONFIRMED_NO_SEND
    assert decision.ok is True
    assert decision.result == PASS_SEND_READY_NO_SUBMIT
    assert decision.attachment_confirmed is True
    assert decision.expected_basename == "operator_report.txt"
    assert decision.expected_basename_sha256 == attachment.expected_basename_sha256
    assert decision.submit_action_allowed is False
    assert decision.send_button_pressed is False
    assert decision.chatgpt_submit_performed is False
    assert decision.raw_conversation_text_logged is False
    assert decision.conversation_text_logged is False
    assert decision.safety_flags["attachment_confirmed"] is True
    assert decision.safety_flags["send_allowed"] is False
    assert decision.safety_flags["selenium_used"] is False
    assert decision.safety_flags["webdriver_used"] is False
    assert decision.safety_flags["browser_dom_automation_used"] is False
    assert str(report.resolve()) not in json.dumps(decision.to_payload())


def test_send_gate_blocks_when_attachment_not_confirmed(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment_payload = {
        "result": "PASS_ATTACHMENT_VERIFICATION_WAITING",
        "attachment_confirmed": False,
        "expected_basename": report.name,
    }
    decision = evaluate_send_gate_no_submit(canonical_report_path=report, attachment_evidence=attachment_payload)

    assert decision.ok is False
    assert decision.result == BLOCKED_ATTACHMENT_NOT_CONFIRMED
    assert decision.chatgpt_submit_performed is False
    assert decision.send_button_pressed is False


def test_send_gate_blocks_hash_mismatch(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment = _attachment_evidence(report).to_payload()
    attachment["expected_basename"] = "wrong.txt"
    attachment["expected_basename_sha256"] = "bad-hash"
    decision = evaluate_send_gate_no_submit(canonical_report_path=report, attachment_evidence=attachment)

    assert decision.ok is False
    assert decision.result == BLOCKED_ATTACHMENT_NOT_CONFIRMED
    assert "basename hash" in decision.reason
    assert decision.chatgpt_submit_performed is False


def test_send_gate_live_mode_requires_confirmation_even_though_no_submit(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment = _attachment_evidence(report)
    decision = evaluate_send_gate_no_submit(
        canonical_report_path=report,
        attachment_evidence=attachment,
        live_browser=True,
        confirm_live_browser_text="wrong",
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_SEND_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in decision.reason
    assert decision.live_browser_used is False
    assert decision.chatgpt_submit_performed is False


def test_send_gate_blocks_allow_submit_because_submit_not_implemented(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment = _attachment_evidence(report)
    decision = evaluate_send_gate_no_submit(
        canonical_report_path=report,
        attachment_evidence=attachment,
        allow_submit=True,
    )

    assert decision.ok is False
    assert decision.result == BLOCKED_SEND_ACTION_NOT_IMPLEMENTED
    assert decision.submit_action_allowed is False
    assert decision.chatgpt_submit_performed is False


def test_write_send_gate_decision_roundtrip(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    decision = evaluate_send_gate_no_submit(canonical_report_path=report, attachment_evidence=_attachment_evidence(report))
    output = write_send_gate_decision(decision, tmp_path / "send_gate" / "decision.json")

    payload_text = output.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert payload["result"] == PASS_SEND_READY_NO_SUBMIT
    assert payload["attachment_confirmed"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_button_pressed"] is False
    assert str(report.resolve()) not in payload_text


def test_send_gate_script_accepts_attachment_evidence_file(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment_path = tmp_path / "attachment.json"
    write_attachment_verification_evidence(_attachment_evidence(report), attachment_path)
    decision_path = tmp_path / "decision.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_send_gate_no_submit.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--attachment-evidence",
            str(attachment_path),
            "--decision-path",
            str(decision_path),
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
    assert payload["result"] == PASS_SEND_READY_NO_SUBMIT
    assert payload["attachment_confirmed"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_button_pressed"] is False
    assert str(report.resolve()) not in result.stdout

    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["result"] == PASS_SEND_READY_NO_SUBMIT


def test_send_gate_script_blocks_allow_submit(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    attachment_path = tmp_path / "attachment.json"
    write_attachment_verification_evidence(_attachment_evidence(report), attachment_path)
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_send_gate_no_submit.py"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--attachment-evidence",
            str(attachment_path),
            "--allow-submit",
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
    assert payload["result"] == BLOCKED_SEND_ACTION_NOT_IMPLEMENTED
    assert payload["chatgpt_submit_performed"] is False


def test_send_gate_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_send_gate_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_send_gate.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_send_gate_no_submit.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text