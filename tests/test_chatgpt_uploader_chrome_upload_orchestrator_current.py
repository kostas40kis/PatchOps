from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_upload_orchestrator import (
    BLOCKED_UPLOAD_FLOW_ATTACHMENT,
    BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION,
    PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT,
    PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED,
    build_attachment_descriptor,
    run_chrome_upload_flow,
    write_chrome_upload_flow_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PatchOps operator report\n=======================\nfinal result      : PASS\nSafety flags\n------------\n",
        encoding="utf-8",
    )
    return path


def test_upload_flow_ready_no_submit(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = run_chrome_upload_flow(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_descriptor(basename=report.name)],
    )

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT
    assert evidence.attachment_confirmed is True
    assert evidence.send_gate_ready is True
    assert evidence.submit_adapter_ready is True
    assert evidence.submit_action_requested is False
    assert evidence.submit_action_performed is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.send_button_pressed is False
    assert evidence.raw_conversation_text_logged is False
    assert evidence.conversation_text_logged is False
    assert evidence.safety_flags["orchestrator_used"] is True
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False
    assert str(report.resolve()) not in json.dumps(evidence.to_payload())


def test_upload_flow_mock_submit_success(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = run_chrome_upload_flow(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_descriptor(basename=report.name)],
        submit_action_requested=True,
        mock_submit_success=True,
    )

    assert evidence.ok is True
    assert evidence.result == PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED
    assert evidence.submit_action_requested is True
    assert evidence.submit_action_performed is True
    assert evidence.chatgpt_submit_performed is True
    assert evidence.send_button_pressed is False
    assert evidence.safety_flags["chatgpt_submit_performed"] is True


def test_upload_flow_blocks_at_attachment_without_attempt(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = run_chrome_upload_flow(
        canonical_report_path=report,
        upload_attempted_before_verification=False,
        attachment_descriptors=[build_attachment_descriptor(basename=report.name)],
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_UPLOAD_FLOW_ATTACHMENT
    assert evidence.attachment_confirmed is False
    assert evidence.send_gate_ready is False
    assert evidence.submit_adapter_ready is False
    assert evidence.chatgpt_submit_performed is False


def test_upload_flow_blocks_submit_action_without_mock_or_live_confirmation(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = run_chrome_upload_flow(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_descriptor(basename=report.name)],
        submit_action_requested=True,
        mock_submit_success=False,
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_UPLOAD_FLOW_SUBMIT_ACTION
    assert evidence.submit_action_requested is True
    assert evidence.submit_action_performed is False
    assert evidence.chatgpt_submit_performed is False


def test_write_upload_flow_evidence_roundtrip(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = run_chrome_upload_flow(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_descriptor(basename=report.name)],
    )
    output = write_chrome_upload_flow_evidence(evidence, tmp_path / "flow" / "evidence.json")

    payload_text = output.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert payload["result"] == PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT
    assert payload["send_gate_ready"] is True
    assert payload["submit_adapter_ready"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert str(report.resolve()) not in payload_text


def test_upload_flow_script_ready_no_submit(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    flow_path = tmp_path / "flow.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_upload_flow.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--upload-attempted-before-verification",
            "--mock-attachment",
            "operator_report.txt|true|true|true|false|false",
            "--flow-evidence-path",
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
    assert payload["result"] == PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT
    assert payload["attachment_confirmed"] is True
    assert payload["send_gate_ready"] is True
    assert payload["submit_adapter_ready"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert str(report.resolve()) not in result.stdout

    saved = json.loads(flow_path.read_text(encoding="utf-8"))
    assert saved["result"] == PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT


def test_upload_flow_script_mock_submit_success(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_upload_flow.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--upload-attempted-before-verification",
            "--mock-attachment",
            "operator_report.txt|true|true|true|false|false",
            "--submit-action-requested",
            "--mock-submit-success",
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
    assert payload["result"] == PASS_CHROME_UPLOAD_FLOW_SUBMIT_MOCKED
    assert payload["submit_action_performed"] is True
    assert payload["chatgpt_submit_performed"] is True
    assert payload["send_button_pressed"] is False


def test_chrome_upload_orchestrator_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_upload_orchestrator_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_upload_orchestrator.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_upload_flow.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text