from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_self_report_keyboard_upload_no_send import (
    BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED,
    BLOCKED_CHROME_KEYBOARD_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_KEYBOARD_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_KEYBOARD_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_KEYBOARD_PASTE_FAILED,
    BLOCKED_CHROME_KEYBOARD_ATTACHMENT_NOT_VERIFIED,
    BLOCKED_CHROME_KEYBOARD_REPORT_HASH_MISMATCH,
    BLOCKED_CHROME_KEYBOARD_REPORT_MISSING,
    BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY,
    CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND,
    PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND,
    scan_edge_keyboard_shortcuts,
    run_keyboard_upload_no_send,
    sha256_file,
    sha256_text,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_report(tmp_path: Path) -> Path:
    report = tmp_path / "pseudo_self_report_keyboard_upload_no_send_report.txt"
    report.write_text("pseudo patch keyboard self report\n", encoding="utf-8")
    return report


def ready_config() -> dict[str, object]:
    return {
        "status_chat": {
            "enabled": True,
            "browser_lane": "chrome",
            "target_url": TARGET_URL,
            "target_url_sha256": sha256_text(TARGET_URL),
        }
    }


def run_ready(report: Path, **overrides: object):
    values = {
        "config_payload": ready_config(),
        "config_path": report.parent / "uploader_status_target_config.json",
        "provider": "fake-ready",
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_KEYBOARD_SELF_REPORT_UPLOAD_NO_SEND,
        "self_report_path": str(report),
        "expected_self_report_sha256": sha256_file(report),
        "repo_root": report.parent,
    }
    values.update(overrides)
    return run_keyboard_upload_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_keyboard_attach_no_send(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND
    assert result.selected_action == "upload_self_report_keyboard_no_send"
    assert result.browser_lane == "chrome"
    assert result.live_browser is True
    assert result.stop_before_send is True
    assert result.confirmation_matched is True
    assert result.file_clipboard_written is True
    assert result.ctrl_v_pressed is True
    assert result.keyboard_shortcuts_used == ("CTRL+V",)
    assert result.forbidden_keyboard_shortcuts_used == ()
    assert result.enter_key_pressed is False
    assert result.file_picker_used is False
    assert result.file_path_written is False
    assert result.open_button_clicked is False
    assert result.attachment_verified is True
    assert result.operator_report_attached_to_composer is True
    assert result.file_upload_attempted is True
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


def test_confirmation_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text=None)
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_CONFIRMATION_REQUIRED
    assert result.browser_action_performed is False


def test_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_CONFIRMATION_MISMATCH
    assert result.browser_action_performed is False


def test_live_browser_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_LIVE_BROWSER_REQUIRED
    assert result.browser_action_performed is False


def test_report_path_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, self_report_path=None, expected_self_report_sha256=None)
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_REPORT_MISSING


def test_report_hash_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_self_report_sha256="wrong")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_REPORT_HASH_MISMATCH
    assert result.browser_action_performed is False


def test_fake_no_target_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-target")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_TARGET_NOT_READY
    assert result.ctrl_v_pressed is False
    assert result.send_button_pressed is False


def test_fake_clipboard_failure_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-clipboard-failed")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED
    assert result.file_clipboard_written is False
    assert result.ctrl_v_pressed is False


def test_fake_paste_failure_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-paste-failed")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_PASTE_FAILED
    assert result.file_clipboard_written is True
    assert result.ctrl_v_pressed is False


def test_fake_not_verified_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-not-verified")
    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_KEYBOARD_ATTACHMENT_NOT_VERIFIED
    assert result.file_clipboard_written is True
    assert result.ctrl_v_pressed is True
    assert result.attachment_verified is False
    assert result.enter_key_pressed is False
    assert result.send_button_pressed is False


def test_edge_keyboard_scan_redacts_source_and_reports_tokens(tmp_path: Path) -> None:
    edge_file = tmp_path / "patchops" / "chatgpt_uploader" / "edge_report_uploader.py"
    edge_file.parent.mkdir(parents=True)
    edge_file.write_text("keyboard.send_keys('^v')\n# clipboard paste\n", encoding="utf-8")

    scan = scan_edge_keyboard_shortcuts(tmp_path)
    assert scan["found"]["ctrl_v"] is True
    assert scan["found"]["clipboard"] is True
    assert scan["safe_shortcuts_reused"] == ["CTRL+V"]
    assert "CTRL+U" in scan["forbidden_shortcuts_not_used"]


def test_write_keyboard_evidence(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "keyboard_upload.json"
    txt_path = tmp_path / "keyboard_upload.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND
    assert payload["keyboard_shortcuts_used"] == ["CTRL+V"]
    assert payload["forbidden_keyboard_shortcuts_used"] == []
    assert payload["file_clipboard_written"] is True
    assert payload["ctrl_v_pressed"] is True
    assert payload["enter_key_pressed"] is False
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["file_picker_used"] is False
    assert TARGET_URL not in json_path.read_text(encoding="utf-8")
    assert "Google Chrome" not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND" in text
    assert "keyboard_shortcuts_used: CTRL+V" in text
    assert "enter_key_pressed: false" in text
    assert "send_button_pressed: false" in text

def test_cf_hdrop_payload_is_utf16_file_list(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.chrome_self_report_keyboard_upload_no_send import build_cf_hdrop_payload

    report = make_report(tmp_path)
    payload = build_cf_hdrop_payload(report)

    assert payload[:4] == (20).to_bytes(4, "little")
    assert str(report.resolve()).encode("utf-16le") in payload
    assert payload.endswith(b"\x00\x00\x00\x00")

def test_keyboard_pass_requires_strict_visible_after_paste_contract() -> None:
    source = Path("patchops/chatgpt_uploader/chrome_self_report_keyboard_upload_no_send.py").read_text(encoding="utf-8")

    assert "_visible_attachment_matches" in source
    assert "_attachment_verified_after_paste" in source
    assert "before_matches = self._visible_attachment_matches" in source
    assert "new visible lower-composer attachment was not verified" in source