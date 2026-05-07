from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_attachment_verifier import (
    BLOCKED_ATTACHMENT_AMBIGUOUS,
    BLOCKED_ATTACHMENT_NOT_FOUND,
    BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING,
    BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED,
    BLOCKED_UPLOAD_NOT_ATTEMPTED,
    LIVE_CONFIRM_TEXT,
    PASS_ATTACHMENT_CONFIRMED_NO_SEND,
    PASS_ATTACHMENT_VERIFICATION_WAITING,
    basename_hash,
    build_attachment_candidate,
    verify_attachment_no_send,
    write_attachment_verification_evidence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _report(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "PatchOps operator report\n=======================\nfinal result      : PASS\nSafety flags\n------------\n",
        encoding="utf-8",
    )
    return path


def test_attachment_verifier_blocks_without_prior_upload_attempt(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    descriptor = build_attachment_candidate(basename="operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=False,
        attachment_descriptors=[descriptor],
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_UPLOAD_NOT_ATTEMPTED
    assert evidence.attachment_confirmed is False
    assert evidence.chatgpt_submit_performed is False
    assert evidence.send_allowed is False


def test_attachment_verifier_confirms_exact_stable_basename_no_send(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_candidate(basename="operator_report.txt")],
    )

    assert evidence.ok is True
    assert evidence.result == PASS_ATTACHMENT_CONFIRMED_NO_SEND
    assert evidence.expected_basename == "operator_report.txt"
    assert evidence.expected_basename_sha256 == basename_hash("operator_report.txt")
    assert evidence.candidate_count == 1
    assert evidence.matching_candidate_count == 1
    assert evidence.selected_attachment is not None
    assert evidence.selected_attachment["basename"] == "operator_report.txt"
    assert evidence.selected_attachment["selected"] is True
    assert evidence.attachment_confirmed is True
    assert evidence.attachment_stable is True
    assert evidence.file_upload_attempted is True
    assert evidence.chatgpt_submit_performed is False
    assert evidence.send_allowed is False
    assert evidence.raw_conversation_text_logged is False
    assert evidence.safety_flags["attachment_confirmed"] is True
    assert evidence.safety_flags["send_allowed"] is False
    assert evidence.safety_flags["selenium_used"] is False
    assert evidence.safety_flags["webdriver_used"] is False
    assert evidence.safety_flags["browser_dom_automation_used"] is False
    assert str(report.resolve()) not in json.dumps(evidence.to_payload())


def test_attachment_verifier_waits_when_descriptor_not_stable(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_candidate(basename="operator_report.txt", stable=False, progress_visible=True)],
    )

    assert evidence.ok is False
    assert evidence.result == PASS_ATTACHMENT_VERIFICATION_WAITING
    assert evidence.attachment_confirmed is False
    assert evidence.chatgpt_submit_performed is False


def test_attachment_verifier_blocks_when_no_candidates(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[],
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_ATTACHMENT_NOT_FOUND
    assert evidence.candidate_count == 0


def test_attachment_verifier_blocks_ambiguous_duplicates(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[
            build_attachment_candidate(basename="operator_report.txt", source="candidate_a"),
            build_attachment_candidate(basename="operator_report.txt", source="candidate_b"),
        ],
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_ATTACHMENT_AMBIGUOUS
    assert evidence.matching_candidate_count == 2
    assert evidence.attachment_confirmed is False


def test_attachment_verifier_ignores_wrong_basename(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_candidate(basename="wrong_report.txt")],
    )

    assert evidence.ok is False
    assert evidence.result == PASS_ATTACHMENT_VERIFICATION_WAITING
    assert evidence.matching_candidate_count == 0
    assert evidence.attachment_confirmed is False


def test_live_attachment_verification_requires_confirmation(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        live_browser=True,
        confirm_live_browser_text="wrong",
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING
    assert LIVE_CONFIRM_TEXT in evidence.reason
    assert evidence.live_browser_used is False
    assert evidence.attachment_confirmed is False


def test_live_attachment_verification_is_explicitly_unsupported_this_patch(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        live_browser=True,
        confirm_live_browser_text=LIVE_CONFIRM_TEXT,
    )

    assert evidence.ok is False
    assert evidence.result == BLOCKED_LIVE_ATTACHMENT_VERIFICATION_UNSUPPORTED
    assert evidence.live_browser_used is False
    assert evidence.chatgpt_submit_performed is False


def test_write_attachment_verification_evidence_roundtrip(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence = verify_attachment_no_send(
        canonical_report_path=report,
        upload_attempted_before_verification=True,
        attachment_descriptors=[build_attachment_candidate(basename="operator_report.txt")],
    )
    output = write_attachment_verification_evidence(evidence, tmp_path / "attachment" / "evidence.json")

    payload_text = output.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert payload["result"] == PASS_ATTACHMENT_CONFIRMED_NO_SEND
    assert payload["attachment_confirmed"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_allowed"] is False
    assert str(report.resolve()) not in payload_text


def test_attachment_verifier_script_mock_success(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    evidence_path = tmp_path / "attachment.json"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_verify_attachment_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--upload-attempted-before-verification",
            "--mock-attachment",
            "operator_report.txt|true|true|true|false|false",
            "--evidence-path",
            str(evidence_path),
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
    assert payload["result"] == PASS_ATTACHMENT_CONFIRMED_NO_SEND
    assert payload["attachment_confirmed"] is True
    assert payload["chatgpt_submit_performed"] is False
    assert payload["send_allowed"] is False
    assert str(report.resolve()) not in result.stdout

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["result"] == PASS_ATTACHMENT_CONFIRMED_NO_SEND


def test_attachment_verifier_script_blocks_without_upload_attempt(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_verify_attachment_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--mock-attachment",
            "operator_report.txt|true|true|true|false|false",
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
    assert payload["result"] == BLOCKED_UPLOAD_NOT_ATTEMPTED
    assert payload["attachment_confirmed"] is False


def test_attachment_verifier_script_live_without_confirmation_blocks(tmp_path: Path) -> None:
    report = _report(tmp_path / "operator_report.txt")
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_verify_attachment_no_send.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--canonical-report",
            str(report),
            "--upload-attempted-before-verification",
            "--live-browser",
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
    assert payload["result"] == BLOCKED_ATTACHMENT_VERIFICATION_CONFIRMATION_MISSING
    assert payload["live_browser_used"] is False
    assert payload["attachment_confirmed"] is False


def test_chrome_attachment_verifier_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_attachment_verifier_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_attachment_verifier.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_verify_attachment_no_send.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text