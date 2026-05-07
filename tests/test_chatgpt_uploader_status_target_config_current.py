from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.status_target_config import (
    BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED,
    BLOCKED_STATUS_TARGET_CONFIG_MISSING,
    BLOCKED_STATUS_TARGET_URL_INVALID,
    PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED,
    REJECTED_BROWSER_LANES,
    example_config_payload,
    sha256_text,
    validate_status_target_config_path,
    validate_status_target_config_payload,
    write_example_config,
    write_validation_evidence,
)


def valid_payload(browser_lane: str = "chrome", target_url: str = "https://chatgpt.com/c/abc123") -> dict[str, object]:
    return {
        "status_chat": {
            "browser_lane": browser_lane,
            "target_url": target_url,
            "target_url_sha256": sha256_text(target_url),
            "enabled": True,
        }
    }


def test_valid_chrome_status_target_config_passes() -> None:
    validation = validate_status_target_config_payload(valid_payload("chrome"))

    assert validation.ok is True
    assert validation.result_label == PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED
    assert validation.browser_lane == "chrome"
    assert validation.enabled is True
    assert validation.target_url_hash == sha256_text("https://chatgpt.com/c/abc123")
    assert validation.redacted_target_display == "https://chatgpt.com/c/<redacted>"
    assert validation.browser_action_performed is False
    assert validation.chatgpt_submit_performed is False
    assert validation.operator_report_uploaded is False
    assert validation.status_message_posted is False
    assert validation.send_button_pressed is False
    assert validation.raw_conversation_text_available is False
    assert validation.selenium_used is False
    assert validation.webdriver_used is False
    assert validation.browser_dom_automation_used is False
    assert validation.cloudflare_bypass_attempted is False
    assert validation.captcha_bypass_attempted is False


def test_valid_edge_status_target_config_passes() -> None:
    validation = validate_status_target_config_payload(valid_payload("edge"))

    assert validation.ok is True
    assert validation.result_label == PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED
    assert validation.browser_lane == "edge"


def test_rejected_browser_lanes_block() -> None:
    for browser_lane in REJECTED_BROWSER_LANES:
        payload = valid_payload(browser_lane)
        validation = validate_status_target_config_payload(payload)

        assert validation.ok is False
        assert validation.result_label == BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED
        assert validation.browser_lane == browser_lane


def test_unknown_browser_lane_blocks() -> None:
    validation = validate_status_target_config_payload(valid_payload("internet-explorer"))

    assert validation.ok is False
    assert validation.result_label == BLOCKED_STATUS_TARGET_BROWSER_UNSUPPORTED
    assert validation.browser_lane == "internet-explorer"


def test_missing_status_chat_blocks_as_config_missing() -> None:
    validation = validate_status_target_config_payload({})

    assert validation.ok is False
    assert validation.result_label == BLOCKED_STATUS_TARGET_CONFIG_MISSING
    assert validation.browser_lane is None


def test_invalid_target_url_blocks() -> None:
    validation = validate_status_target_config_payload(
        {
            "status_chat": {
                "browser_lane": "chrome",
                "target_url": "http://example.com/not-chatgpt",
                "enabled": True,
            }
        }
    )

    assert validation.ok is False
    assert validation.result_label == BLOCKED_STATUS_TARGET_URL_INVALID


def test_target_url_hash_mismatch_blocks() -> None:
    validation = validate_status_target_config_payload(
        {
            "status_chat": {
                "browser_lane": "chrome",
                "target_url": "https://chatgpt.com/c/abc123",
                "target_url_sha256": "wrong-hash",
                "enabled": True,
            }
        }
    )

    assert validation.ok is False
    assert validation.result_label == BLOCKED_STATUS_TARGET_URL_INVALID
    assert "abc123" not in (validation.redacted_target_display or "")


def test_validate_status_target_config_path_and_write_evidence(tmp_path: Path) -> None:
    config_path = tmp_path / "uploader_status_target_config.json"
    json_output = tmp_path / "validation.json"
    txt_output = tmp_path / "validation.txt"
    config_path.write_text(json.dumps(valid_payload("chrome")), encoding="utf-8")

    validation = validate_status_target_config_path(config_path)
    write_validation_evidence(validation, json_output_path=json_output, txt_output_path=txt_output)

    assert validation.ok is True
    assert validation.config_path == str(config_path)
    assert validation.config_sha256 is not None
    assert json_output.exists()
    assert txt_output.exists()

    payload = json.loads(json_output.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED
    assert payload["browser_lane"] == "chrome"
    assert payload["browser_action_performed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["status_message_posted"] is False
    assert payload["send_button_pressed"] is False
    assert payload["raw_conversation_text_available"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False
    assert payload["cloudflare_bypass_attempted"] is False
    assert payload["captcha_bypass_attempted"] is False

    text = txt_output.read_text(encoding="utf-8")
    assert "result_label: PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED" in text
    assert "browser_lane: chrome" in text
    assert "chatgpt_submit_performed: false" in text
    assert "browser_dom_automation_used: false" in text


def test_missing_config_path_blocks(tmp_path: Path) -> None:
    validation = validate_status_target_config_path(tmp_path / "missing.json")

    assert validation.ok is False
    assert validation.result_label == BLOCKED_STATUS_TARGET_CONFIG_MISSING


def test_write_example_config_creates_valid_shape(tmp_path: Path) -> None:
    path = tmp_path / "example.json"
    write_example_config(path)

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload == example_config_payload()

    validation = validate_status_target_config_payload(payload)
    assert validation.ok is True
    assert validation.browser_lane == "chrome"