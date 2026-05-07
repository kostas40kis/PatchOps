from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.edge_status_target import (
    BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH,
    BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING,
    BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH,
    BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED,
    BLOCKED_EDGE_STATUS_TARGET_NOT_READY,
    BLOCKED_EDGE_STATUS_TARGET_URL_INVALID,
    BLOCKED_SEND_RISK,
    CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT,
    PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY,
    extract_status_target,
    load_status_target_payload,
    run_edge_status_target_preflight,
    write_preflight_evidence,
)


def edge_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "status_chat": {
            "browser_lane": "edge",
            "target_url": "https://chatgpt.com/c/example-edge-target",
            "target_url_sha256": "abc123",
            "enabled": True,
        }
    }
    payload.update(overrides)
    return payload


def run_ready(**overrides: object):
    values = {
        "status_target_payload": edge_payload(),
        "live_browser": True,
        "confirmation_text": CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT,
        "provider": "fake-ready",
    }
    values.update(overrides)
    return run_edge_status_target_preflight(**values)  # type: ignore[arg-type]


def test_edge_status_target_fake_ready_passes_and_never_sends() -> None:
    result = run_ready()

    assert result.ok is True
    assert result.result_label == PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY
    assert result.browser_lane == "edge"
    assert result.status_chat_configured is True
    assert result.edge_target_ready is True
    assert result.edge_target_focused is True
    assert result.composer_candidate_count == 1
    assert result.required_next_gate == "edge_status_message_send_gate"
    assert result.browser_action_performed is True
    assert result.chatgpt_submit_performed is False
    assert result.operator_report_uploaded is False
    assert result.status_message_posted is False
    assert result.send_button_pressed is False
    assert result.raw_conversation_text_available is False
    assert result.selenium_used is False
    assert result.webdriver_used is False
    assert result.browser_dom_automation_used is False
    assert result.cloudflare_bypass_attempted is False
    assert result.captcha_bypass_attempted is False
    assert result.safety.file_upload_attempted is False
    assert result.safety.conversation_text_logged is False
    assert result.safety.random_page_click_performed is False


def test_missing_payload_blocks() -> None:
    result = run_edge_status_target_preflight(
        status_target_payload=None,
        live_browser=True,
        confirmation_text=CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT,
        provider="fake-ready",
    )

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING
    assert result.browser_action_performed is False


def test_browser_lane_must_be_edge() -> None:
    result = run_ready(status_target_payload=edge_payload(status_chat={"browser_lane": "chrome", "target_url": "https://chatgpt.com/c/example", "enabled": True}))

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH
    assert result.browser_lane == "chrome"
    assert result.edge_target_focused is False


def test_status_chat_must_be_configured() -> None:
    result = run_ready(status_target_payload=edge_payload(status_chat={"browser_lane": "edge", "target_url": "https://chatgpt.com/c/example", "enabled": False}))

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING
    assert result.edge_target_focused is False


def test_target_url_must_be_chatgpt_conversation_url() -> None:
    result = run_ready(status_target_payload=edge_payload(status_chat={"browser_lane": "edge", "target_url": "http://example.com/nope", "enabled": True}))

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_URL_INVALID
    assert result.edge_target_focused is False


def test_hash_only_target_is_accepted() -> None:
    result = run_ready(status_target_payload={"status_chat": {"browser_lane": "edge", "target_url_sha256": "hash-only", "enabled": True}})

    assert result.ok is True
    assert result.result_label == PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY
    assert result.status_chat_url_hash_or_redacted == "hash-only"


def test_live_browser_flag_is_required() -> None:
    result = run_ready(live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_SEND_RISK
    assert result.edge_target_focused is False
    assert result.chatgpt_submit_performed is False


def test_confirmation_is_required() -> None:
    result = run_ready(confirmation_text=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED
    assert result.edge_target_focused is False


def test_confirmation_mismatch_blocks() -> None:
    result = run_ready(confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH
    assert result.confirmation_matched is False
    assert result.edge_target_focused is False


def test_no_target_blocks() -> None:
    result = run_ready(provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.matching_target_count == 0
    assert result.chatgpt_submit_performed is False


def test_ambiguous_target_blocks() -> None:
    result = run_ready(provider="fake-ambiguous-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.matching_target_count == 2
    assert result.send_button_pressed is False


def test_no_composer_blocks() -> None:
    result = run_ready(provider="fake-no-composer")

    assert result.ok is False
    assert result.result_label == BLOCKED_EDGE_STATUS_TARGET_NOT_READY
    assert result.edge_target_focused is True
    assert result.composer_candidate_count == 0
    assert result.chatgpt_submit_performed is False


def test_extract_status_target_from_validation_payload() -> None:
    target = extract_status_target(
        {
            "ok": True,
            "result_label": "PASS_UPLOADER_STATUS_TARGET_CONFIG_VALIDATED",
            "browser_lane": "edge",
            "status_chat_configured": True,
            "status_chat_url_hash_or_redacted": "https://chatgpt.com/c/<redacted>#sha256:abc",
        }
    )

    assert target["browser_lane"] == "edge"
    assert target["status_chat_configured"] is True
    assert target["target_url_sha256"] == "https://chatgpt.com/c/<redacted>#sha256:abc"


def test_load_status_target_payload_prefers_explicit_path(tmp_path: Path) -> None:
    path = tmp_path / "edge_target.json"
    path.write_text(json.dumps(edge_payload()), encoding="utf-8")

    payload = load_status_target_payload(path)

    assert payload is not None
    assert payload["status_chat"]["browser_lane"] == "edge"  # type: ignore[index]


def test_write_preflight_evidence_redacts_title_and_records_no_send(tmp_path: Path) -> None:
    result = run_ready()
    json_path = tmp_path / "edge_preflight.json"
    txt_path = tmp_path / "edge_preflight.txt"

    write_preflight_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    assert json_path.exists()
    assert txt_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY
    assert payload["selected_target_title_hash"] is not None
    assert "Microsoft Edge" not in json_path.read_text(encoding="utf-8")
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

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY" in text
    assert "browser_lane: edge" in text
    assert "chatgpt_submit_performed: false" in text
    assert "browser_dom_automation_used: false" in text