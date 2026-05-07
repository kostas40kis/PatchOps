from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_self_report_desktop_filename_upload_no_send import sha256_file, sha256_text
from patchops.chatgpt_uploader.chrome_self_report_upload_button_desktop_filename_no_send import (
    BLOCKED_CHROME_UPLOAD_BUTTON_ATTACHMENT_NOT_VERIFIED,
    BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_UPLOAD_BUTTON_CONTROL_NOT_FOUND,
    BLOCKED_CHROME_UPLOAD_BUTTON_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_ENTER_FAILED,
    BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_NOT_OPENED,
    BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_NOT_ON_DESKTOP,
    CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND,
    PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND,
    run_upload_button_desktop_filename_no_send,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_desktop_report(tmp_path: Path) -> tuple[Path, Path]:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_button_desktop_filename_self_report.txt"
    report.write_text("pseudo patch upload-button desktop filename self report\n", encoding="utf-8")
    return desktop, report


def ready_config() -> dict[str, object]:
    return {
        "status_chat": {
            "enabled": True,
            "browser_lane": "chrome",
            "target_url": TARGET_URL,
            "target_url_sha256": sha256_text(TARGET_URL),
        }
    }


def run_ready(report: Path, desktop: Path, **overrides: object):
    values = {
        "config_payload": ready_config(),
        "config_path": report.parent / "uploader_status_target_config.json",
        "provider": "fake-ready",
        "live_browser": True,
        "confirmation_text": CONFIRM_CHROME_UPLOAD_BUTTON_DESKTOP_FILENAME_NO_SEND,
        "self_report_path": str(report),
        "expected_self_report_sha256": sha256_file(report),
        "desktop_dir": str(desktop),
    }
    values.update(overrides)
    return run_upload_button_desktop_filename_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_upload_button_desktop_filename_attach_no_send(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND
    assert result.selected_action == "upload_self_report_upload_button_desktop_filename_no_send"
    assert result.desktop_directory == str(desktop)
    assert result.self_report_filename == report.name
    assert result.browser_lane == "chrome"
    assert result.live_browser is True
    assert result.stop_before_send is True
    assert result.safe_focus_click_performed is True
    assert result.upload_button_clicked is True
    assert result.upload_button_candidate_count == 1
    assert result.slash_key_pressed is False
    assert result.upload_command_enter_pressed is False
    assert result.picker_opened is True
    assert result.filename_written is True
    assert result.full_path_written_to_picker is False
    assert result.open_button_clicked is False
    assert result.picker_enter_pressed is True
    assert result.enter_key_pressed_in_chat_composer is False
    assert result.enter_key_pressed_in_picker is True
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


def test_blocks_when_report_not_on_desktop(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = tmp_path / "not_desktop_report.txt"
    report.write_text("x\n", encoding="utf-8")
    result = run_ready(report, desktop)
    assert result.result_label == BLOCKED_CHROME_UPLOAD_BUTTON_REPORT_NOT_ON_DESKTOP
    assert result.browser_action_performed is False


def test_confirmation_and_live_browser_required(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    assert run_ready(report, desktop, confirmation_text=None).result_label == BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_REQUIRED
    assert run_ready(report, desktop, confirmation_text="WRONG").result_label == BLOCKED_CHROME_UPLOAD_BUTTON_CONFIRMATION_MISMATCH
    assert run_ready(report, desktop, live_browser=False).result_label == BLOCKED_CHROME_UPLOAD_BUTTON_LIVE_BROWSER_REQUIRED


def test_fake_button_and_picker_failures(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    assert run_ready(report, desktop, provider="fake-no-button").result_label == BLOCKED_CHROME_UPLOAD_BUTTON_CONTROL_NOT_FOUND
    assert run_ready(report, desktop, provider="fake-no-picker").result_label == BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_NOT_OPENED
    assert run_ready(report, desktop, provider="fake-enter-failed").result_label == BLOCKED_CHROME_UPLOAD_BUTTON_PICKER_ENTER_FAILED
    assert run_ready(report, desktop, provider="fake-not-verified").result_label == BLOCKED_CHROME_UPLOAD_BUTTON_ATTACHMENT_NOT_VERIFIED


def test_write_upload_button_desktop_filename_evidence(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)
    json_path = tmp_path / "upload_button.json"
    txt_path = tmp_path / "upload_button.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND
    assert payload["upload_button_clicked"] is True
    assert payload["slash_key_pressed"] is False
    assert payload["filename_written"] is True
    assert payload["full_path_written_to_picker"] is False
    assert payload["open_button_clicked"] is False
    assert payload["picker_enter_pressed"] is True
    assert payload["enter_key_pressed_in_chat_composer"] is False
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert TARGET_URL not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND" in text
    assert "upload_button_clicked: true" in text
    assert "slash_key_pressed: false" in text
    assert "filename_written: true" in text
    assert "picker_enter_pressed: true" in text
    assert "send_button_pressed: false" in text


def test_source_contract_uses_upload_button_not_command_shortcut() -> None:
    source = Path("patchops/chatgpt_uploader/chrome_self_report_upload_button_desktop_filename_no_send.py").read_text(encoding="utf-8")

    assert "click_upload_button" in source
    assert "edit.set_edit_text(report_path.name)" in source
    assert 'send_keys("/"' not in source
    assert 'send_keys("{TAB}"' not in source
    assert "button.click_input" not in source