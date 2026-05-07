from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_self_report_desktop_filename_upload_no_send import (
    BLOCKED_CHROME_DESKTOP_FILENAME_ATTACHMENT_NOT_VERIFIED,
    BLOCKED_CHROME_DESKTOP_FILENAME_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_DESKTOP_FILENAME_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_ENTER_FAILED,
    BLOCKED_CHROME_DESKTOP_FILENAME_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_AMBIGUOUS,
    BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_NOT_OPENED,
    BLOCKED_CHROME_DESKTOP_FILENAME_REPORT_HASH_MISMATCH,
    BLOCKED_CHROME_DESKTOP_FILENAME_REPORT_NOT_ON_DESKTOP,
    BLOCKED_CHROME_DESKTOP_FILENAME_TARGET_NOT_READY,
    BLOCKED_CHROME_DESKTOP_FILENAME_WRITE_FAILED,
    CONFIRM_CHROME_DESKTOP_FILENAME_SELF_REPORT_UPLOAD_NO_SEND,
    PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND,
    run_desktop_filename_upload_no_send,
    sha256_file,
    sha256_text,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_desktop_report(tmp_path: Path) -> tuple[Path, Path]:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_no_send_repair_10_desktop_filename_enter_self_report.txt"
    report.write_text("pseudo patch desktop filename self report\n", encoding="utf-8")
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
        "confirmation_text": CONFIRM_CHROME_DESKTOP_FILENAME_SELF_REPORT_UPLOAD_NO_SEND,
        "self_report_path": str(report),
        "expected_self_report_sha256": sha256_file(report),
        "desktop_dir": str(desktop),
    }
    values.update(overrides)
    return run_desktop_filename_upload_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_desktop_filename_enter_attach_no_send(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND
    assert result.selected_action == "upload_self_report_desktop_filename_enter_no_send"
    assert result.desktop_directory == str(desktop)
    assert result.self_report_filename == report.name
    assert result.browser_lane == "chrome"
    assert result.live_browser is True
    assert result.stop_before_send is True
    assert result.safe_focus_click_performed is True
    assert result.slash_key_pressed is True
    assert result.upload_command_enter_pressed is True
    assert result.picker_opened is True
    assert result.picker_count == 1
    assert result.filename_written is True
    assert result.full_path_written_to_picker is False
    assert result.open_button_clicked is False
    assert result.picker_enter_pressed is True
    assert result.enter_key_pressed_in_chat_composer is False
    assert result.enter_key_pressed_in_picker is True
    assert result.attachment_verified is True
    assert result.before_attachment_count == 0
    assert result.after_attachment_count == 1
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
    assert result.safety.random_page_click_performed is False


def test_report_must_be_on_desktop(tmp_path: Path) -> None:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = tmp_path / "not_desktop_report.txt"
    report.write_text("x\n", encoding="utf-8")
    result = run_ready(report, desktop)
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_REPORT_NOT_ON_DESKTOP
    assert result.browser_action_performed is False


def test_confirmation_required(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, confirmation_text=None)
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_CONFIRMATION_REQUIRED
    assert result.browser_action_performed is False


def test_confirmation_must_match(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, confirmation_text="WRONG")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_CONFIRMATION_MISMATCH
    assert result.browser_action_performed is False


def test_live_browser_required(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, live_browser=False)
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_LIVE_BROWSER_REQUIRED
    assert result.browser_action_performed is False


def test_report_hash_must_match(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, expected_self_report_sha256="wrong")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_REPORT_HASH_MISMATCH
    assert result.browser_action_performed is False


def test_fake_target_missing(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-no-target")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_TARGET_NOT_READY
    assert result.file_upload_attempted is False


def test_fake_no_picker(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-no-picker")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_NOT_OPENED
    assert result.slash_key_pressed is True
    assert result.upload_command_enter_pressed is True
    assert result.file_upload_attempted is False


def test_fake_ambiguous_picker(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-ambiguous-picker")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_AMBIGUOUS
    assert result.picker_count == 2
    assert result.filename_written is False


def test_fake_write_failed(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-write-failed")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_WRITE_FAILED
    assert result.picker_enter_pressed is False


def test_fake_enter_failed(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-enter-failed")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_ENTER_FAILED
    assert result.filename_written is True
    assert result.picker_enter_pressed is False


def test_fake_not_verified(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop, provider="fake-not-verified")
    assert result.result_label == BLOCKED_CHROME_DESKTOP_FILENAME_ATTACHMENT_NOT_VERIFIED
    assert result.filename_written is True
    assert result.picker_enter_pressed is True
    assert result.attachment_verified is False
    assert result.send_button_pressed is False


def test_write_desktop_filename_evidence(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)
    json_path = tmp_path / "desktop_filename.json"
    txt_path = tmp_path / "desktop_filename.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND
    assert payload["desktop_directory"] == str(desktop)
    assert payload["self_report_filename"] == report.name
    assert payload["filename_written"] is True
    assert payload["full_path_written_to_picker"] is False
    assert payload["open_button_clicked"] is False
    assert payload["picker_enter_pressed"] is True
    assert payload["enter_key_pressed_in_chat_composer"] is False
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert payload["raw_conversation_text_available"] is False
    assert TARGET_URL not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND" in text
    assert "filename_written: true" in text
    assert "picker_enter_pressed: true" in text
    assert "send_button_pressed: false" in text


def test_module_uses_filename_only_not_full_path_or_open_button() -> None:
    source = Path("patchops/chatgpt_uploader/chrome_self_report_desktop_filename_upload_no_send.py").read_text(encoding="utf-8")

    assert 'edit.set_edit_text(report_path.name)' in source
    assert 'keyboard.send_keys("/", pause=0.05)' in source
    assert 'keyboard.send_keys("{ENTER}", pause=0.05)' in source
    assert "button.click_input" not in source
    assert "full_path_written_to_picker=True" not in source
    assert "{TAB}" not in source

