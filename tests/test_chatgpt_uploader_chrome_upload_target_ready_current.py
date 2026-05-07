from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_upload_target_ready import (
    BLOCKED_CHROME_UPLOAD_AMBIGUOUS_TARGET,
    BLOCKED_CHROME_UPLOAD_ATTACHMENT_CONTROL_NOT_FOUND,
    BLOCKED_CHROME_UPLOAD_TARGET_BROWSER_MISMATCH,
    BLOCKED_CHROME_UPLOAD_TARGET_CONFIG_MISSING,
    BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_UPLOAD_TARGET_NOT_READY,
    BLOCKED_CHROME_UPLOAD_TARGET_URL_INVALID,
    BLOCKED_SEND_RISK,
    CONFIRM_CHROME_UPLOAD_TARGET_READY,
    PASS_CHROME_UPLOAD_TARGET_READY,
    extract_status_target,
    run_chrome_upload_target_ready,
    sha256_text,
    valid_chatgpt_status_url,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def ready_config() -> dict[str, object]:
    return {
        "status_chat": {
            "enabled": True,
            "browser_lane": "chrome",
            "target_url": TARGET_URL,
            "target_url_sha256": sha256_text(TARGET_URL),
        }
    }


def run_ready(**overrides: object):
    values = {
        "config_payload": ready_config(),
        "provider": "fake-ready",
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_UPLOAD_TARGET_READY,
    }
    values.update(overrides)
    return run_chrome_upload_target_ready(**values)  # type: ignore[arg-type]


def test_config_extracts_supplied_chrome_target_url() -> None:
    target = extract_status_target(ready_config())

    assert target.enabled is True
    assert target.browser_lane == "chrome"
    assert target.target_url == TARGET_URL
    assert target.target_url_sha256 == sha256_text(TARGET_URL)


def test_chatgpt_gizmo_conversation_url_is_valid() -> None:
    assert valid_chatgpt_status_url(TARGET_URL) is True
    assert valid_chatgpt_status_url("https://chatgpt.com/c/abc123") is True
    assert valid_chatgpt_status_url("http://chatgpt.com/c/abc123") is False
    assert valid_chatgpt_status_url("https://example.com/c/abc123") is False
    assert valid_chatgpt_status_url("https://chatgpt.com/g/demo") is False


def test_fake_ready_passes_without_upload_or_send() -> None:
    result = run_ready()

    assert result.ok is True
    assert result.result_label == PASS_CHROME_UPLOAD_TARGET_READY
    assert result.selected_action == "upload_operator_report"
    assert result.browser_lane == "chrome"
    assert result.status_chat_configured is True
    assert result.status_chat_url_hash_or_redacted == f"sha256:{sha256_text(TARGET_URL)}"
    assert result.target_url_sha256 == sha256_text(TARGET_URL)
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.attachment_control_found is True
    assert result.attachment_candidate_count == 1
    assert result.browser_action_performed is True
    assert result.file_upload_attempted is False
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_missing_config_blocks() -> None:
    result = run_chrome_upload_target_ready(
        config_payload={},
        provider="fake-ready",
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_UPLOAD_TARGET_READY,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_CONFIG_MISSING


def test_browser_lane_must_be_chrome() -> None:
    payload = ready_config()
    payload["status_chat"]["browser_lane"] = "edge"  # type: ignore[index]

    result = run_chrome_upload_target_ready(
        config_payload=payload,
        provider="fake-ready",
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_UPLOAD_TARGET_READY,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_BROWSER_MISMATCH


def test_target_url_must_be_valid() -> None:
    payload = ready_config()
    payload["status_chat"]["target_url"] = "https://example.com/not-chatgpt"  # type: ignore[index]
    payload["status_chat"]["target_url_sha256"] = sha256_text("https://example.com/not-chatgpt")  # type: ignore[index]

    result = run_chrome_upload_target_ready(
        config_payload=payload,
        provider="fake-ready",
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_UPLOAD_TARGET_READY,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_URL_INVALID


def test_target_hash_must_match_url() -> None:
    payload = ready_config()
    payload["status_chat"]["target_url_sha256"] = "wrong"  # type: ignore[index]

    result = run_chrome_upload_target_ready(
        config_payload=payload,
        provider="fake-ready",
        live_browser=True,
        confirmation_text=CONFIRM_CHROME_UPLOAD_TARGET_READY,
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_URL_INVALID


def test_live_browser_flag_is_required() -> None:
    result = run_ready(live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.browser_action_performed is False


def test_confirmation_is_required() -> None:
    result = run_ready(confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_REQUIRED
    assert result.browser_action_performed is False


def test_confirmation_must_match() -> None:
    result = run_ready(confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_MISMATCH
    assert result.browser_action_performed is False


def test_no_target_blocks() -> None:
    result = run_ready(provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_TARGET_NOT_READY
    assert result.matching_target_count == 0


def test_ambiguous_target_blocks() -> None:
    result = run_ready(provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_AMBIGUOUS_TARGET
    assert result.matching_target_count == 2


def test_attachment_control_required() -> None:
    result = run_ready(provider="fake-no-attachment-control")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_UPLOAD_ATTACHMENT_CONTROL_NOT_FOUND
    assert result.chrome_target_focused is True
    assert result.attachment_candidate_count == 0
    assert result.file_upload_attempted is False
    assert result.send_button_pressed is False


def test_write_evidence_redacts_url_and_title(tmp_path: Path) -> None:
    result = run_ready()
    json_path = tmp_path / "target_ready.json"
    txt_path = tmp_path / "target_ready.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_UPLOAD_TARGET_READY
    assert payload["status_chat_url_hash_or_redacted"] == f"sha256:{sha256_text(TARGET_URL)}"
    assert TARGET_URL not in json_path.read_text(encoding="utf-8")
    assert "Google Chrome" not in json_path.read_text(encoding="utf-8")
    assert payload["selected_target_title_hash"] is not None
    assert payload["file_upload_attempted"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_UPLOAD_TARGET_READY" in text
    assert TARGET_URL not in text
    assert "browser_dom_automation_used: false" in text