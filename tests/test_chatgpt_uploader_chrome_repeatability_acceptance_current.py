from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.chatgpt_uploader.chrome_repeatability_acceptance import (
    BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS,
    BLOCKED_ACCEPTANCE_INVALID_BUNDLE,
    BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS,
    BLOCKED_ACCEPTANCE_SUBMIT_DETECTED,
    BLOCKED_ACCEPTANCE_TOO_FEW_PASSES,
    PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND,
    collect_bundle_paths,
    evaluate_bundle_payload,
    evaluate_repeatability_acceptance,
    load_bundle_attempt,
    load_bundle_attempts,
    write_acceptance_json,
    write_acceptance_marker,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _bundle(**overrides):
    payload = {
        "ok": True,
        "result": "PASS_EVIDENCE_BUNDLE_VALIDATED",
        "write_result": "PASS_EVIDENCE_BUNDLE_SUMMARY_WRITTEN",
        "flow_result": "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT",
        "attachment_confirmed": True,
        "send_gate_ready": True,
        "submit_adapter_ready": True,
        "submit_action_requested": False,
        "submit_action_performed": False,
        "chatgpt_submit_performed": False,
        "live_browser_used": False,
        "forbidden_true_flags": [],
        "safety_flags": {
            "selenium_used": False,
            "webdriver_used": False,
            "browser_dom_automation_used": False,
            "cloudflare_bypass_attempted": False,
            "captcha_bypass_attempted": False,
            "conversation_text_logged": False,
            "raw_conversation_text_logged": False,
            "random_page_click_performed": False,
        },
    }
    payload.update(overrides)
    return payload


def _write_bundle(path: Path, **overrides) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_bundle(**overrides), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_evaluate_bundle_payload_accepts_valid_no_send_attempt() -> None:
    attempt = evaluate_bundle_payload(_bundle(), index=1, evidence_basename="bundle_1.json", evidence_sha256="hash")

    assert attempt.ok is True
    assert attempt.status == "PASS_ATTEMPT_ACCEPTED_NO_SEND"
    assert attempt.flow_result == "PASS_CHROME_UPLOAD_FLOW_READY_NO_SUBMIT"
    assert attempt.attachment_confirmed is True
    assert attempt.send_gate_ready is True
    assert attempt.submit_adapter_ready is True
    assert attempt.chatgpt_submit_performed is False
    assert attempt.forbidden_true_flags == []


def test_evaluate_bundle_payload_blocks_submit_detected() -> None:
    attempt = evaluate_bundle_payload(_bundle(chatgpt_submit_performed=True), index=1)

    assert attempt.ok is False
    assert attempt.status == "FAIL_ATTEMPT_SUBMIT_DETECTED"
    assert attempt.chatgpt_submit_performed is True


def test_evaluate_bundle_payload_blocks_forbidden_flag() -> None:
    payload = _bundle()
    payload["safety_flags"]["selenium_used"] = True
    attempt = evaluate_bundle_payload(payload, index=1)

    assert attempt.ok is False
    assert attempt.status == "FAIL_ATTEMPT_FORBIDDEN_FLAGS"
    assert "selenium_used" in attempt.forbidden_true_flags


def test_repeatability_accepts_four_of_five_no_send_attempts() -> None:
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(4)]
    attempts.append(evaluate_bundle_payload(_bundle(attachment_confirmed=False), index=5))

    acceptance = evaluate_repeatability_acceptance(attempts)

    assert acceptance.ok is True
    assert acceptance.result == PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
    assert acceptance.attempt_count == 5
    assert acceptance.pass_count == 4
    assert acceptance.failed_attempt_count == 1
    assert acceptance.attachment_verified is True
    assert acceptance.chatgpt_submit_performed is False
    assert acceptance.selenium_used is False
    assert acceptance.webdriver_used is False
    assert acceptance.browser_dom_automation_used is False
    assert any("PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND" in line for line in acceptance.summary_lines)


def test_repeatability_blocks_too_few_attempts() -> None:
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(4)]
    acceptance = evaluate_repeatability_acceptance(attempts)

    assert acceptance.ok is False
    assert acceptance.result == BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS
    assert acceptance.pass_count == 4


def test_repeatability_blocks_too_few_passes() -> None:
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(3)]
    attempts.extend(evaluate_bundle_payload(_bundle(attachment_confirmed=False), index=index + 4) for index in range(2))
    acceptance = evaluate_repeatability_acceptance(attempts)

    assert acceptance.ok is False
    assert acceptance.result == BLOCKED_ACCEPTANCE_TOO_FEW_PASSES
    assert acceptance.pass_count == 3


def test_repeatability_blocks_forbidden_flags_before_pass_count() -> None:
    payload = _bundle()
    payload["safety_flags"]["webdriver_used"] = True
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(4)]
    attempts.append(evaluate_bundle_payload(payload, index=5))
    acceptance = evaluate_repeatability_acceptance(attempts)

    assert acceptance.ok is False
    assert acceptance.result == BLOCKED_ACCEPTANCE_FORBIDDEN_FLAGS
    assert "webdriver_used" in acceptance.forbidden_true_flags


def test_repeatability_blocks_submit_detected() -> None:
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(4)]
    attempts.append(evaluate_bundle_payload(_bundle(submit_action_performed=True, chatgpt_submit_performed=True), index=5))
    acceptance = evaluate_repeatability_acceptance(attempts)

    assert acceptance.ok is False
    assert acceptance.result == BLOCKED_ACCEPTANCE_SUBMIT_DETECTED
    assert acceptance.chatgpt_submit_detected is True


def test_load_bundle_attempt_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{bad", encoding="utf-8")
    attempt = load_bundle_attempt(path, index=1)
    acceptance = evaluate_repeatability_acceptance([attempt] + [evaluate_bundle_payload(_bundle(), index=i) for i in range(2, 6)])

    assert attempt.ok is False
    assert attempt.status == "FAIL_ATTEMPT_INVALID_JSON"
    assert acceptance.result == BLOCKED_ACCEPTANCE_INVALID_BUNDLE


def test_collect_bundle_paths_from_explicit_and_dir(tmp_path: Path) -> None:
    explicit = _write_bundle(tmp_path / "a.json")
    directory_item = _write_bundle(tmp_path / "bundles" / "b.json")
    paths = collect_bundle_paths(explicit_paths=[explicit], evidence_dir=tmp_path / "bundles")

    assert explicit.resolve() in paths
    assert directory_item.resolve() in paths
    assert len(paths) == 2


def test_write_acceptance_outputs(tmp_path: Path) -> None:
    attempts = [evaluate_bundle_payload(_bundle(), index=index + 1) for index in range(5)]
    acceptance = evaluate_repeatability_acceptance(attempts)
    json_path = write_acceptance_json(acceptance, tmp_path / "acceptance" / "accepted.json")
    marker_path = write_acceptance_marker(acceptance, tmp_path / "acceptance" / "marker.md")

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    marker = marker_path.read_text(encoding="utf-8")
    assert payload["result"] == PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
    assert "Chrome upload repeatability acceptance marker" in marker
    assert "chatgpt_submit_performed:false" in marker
    assert "webdriver_used:false" in marker


def test_acceptance_gate_script_passes_with_five_bundle_files(tmp_path: Path) -> None:
    paths = [_write_bundle(tmp_path / f"bundle_{index}.json") for index in range(5)]
    acceptance_json = tmp_path / "accepted.json"
    marker = tmp_path / "accepted.md"
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_repeatability_acceptance_gate.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            *sum((["--evidence-bundle", str(path)] for path in paths), []),
            "--acceptance-json",
            str(acceptance_json),
            "--acceptance-marker",
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
    assert payload["result"] == PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
    assert payload["attempt_count"] == 5
    assert payload["pass_count"] == 5
    assert payload["chatgpt_submit_performed"] is False
    assert acceptance_json.exists()
    assert marker.exists()


def test_acceptance_gate_script_blocks_too_few(tmp_path: Path) -> None:
    paths = [_write_bundle(tmp_path / f"bundle_{index}.json") for index in range(4)]
    script = PROJECT_ROOT / "scripts" / "run_uploader_chrome_repeatability_acceptance_gate.py"
    result = subprocess.run(
        [sys.executable, str(script), *sum((["--evidence-bundle", str(path)] for path in paths), []), "--json"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["result"] == BLOCKED_ACCEPTANCE_NOT_ENOUGH_ATTEMPTS
    assert payload["chatgpt_submit_performed"] is False


def test_acceptance_marker_doc_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "chatgpt_uploader_chrome_live_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8").lower()
    assert "pass_chrome_upload_accepted_no_send" in text
    assert "chrome-specific" in text
    assert "no-send" in text
    assert "all-browser abstraction" in text
    assert "selenium" in text
    assert "webdriver" in text
    assert "conversation_text_logged:false" in text


def test_chrome_repeatability_acceptance_does_not_create_generic_browser_abstractions() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]
    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_repeatability_acceptance_code_does_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "chrome_repeatability_acceptance.py",
        PROJECT_ROOT / "scripts" / "run_uploader_chrome_repeatability_acceptance_gate.py",
    ]
    forbidden = ["import selenium", "from selenium", "selenium.", "webdriver.chrome", "webdriver.edge", "chromedriver", "playwright"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text