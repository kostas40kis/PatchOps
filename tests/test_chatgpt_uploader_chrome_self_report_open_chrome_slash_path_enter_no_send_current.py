from __future__ import annotations

import json
from pathlib import Path

from patchops.chatgpt_uploader.chrome_self_report_open_chrome_slash_path_enter_no_send import (
    BLOCKED_CHROME_OPEN_SLASH_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_OPEN_SLASH_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_OPEN_SLASH_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_OPEN_SLASH_PATH_PASTE_FAILED,
    BLOCKED_CHROME_OPEN_SLASH_PICKER_ENTER_FAILED,
    BLOCKED_CHROME_OPEN_SLASH_PICKER_NOT_OPENED,
    BLOCKED_CHROME_OPEN_SLASH_REPORT_NOT_ON_DESKTOP,
    CONFIRM_CHROME_OPEN_SLASH_PATH_ENTER_NO_SEND,
    PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND,
    run_open_chrome_slash_path_enter_no_send,
    sha256_file,
    sha256_text,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_desktop_report(tmp_path: Path) -> tuple[Path, Path]:
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_no_send_repair_12_open_chrome_slash_path_enter_self_report.txt"
    report.write_text("pseudo patch open chrome slash full path enter self report\n", encoding="utf-8")
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
        "confirmation_text": CONFIRM_CHROME_OPEN_SLASH_PATH_ENTER_NO_SEND,
        "self_report_path": str(report),
        "expected_self_report_sha256": sha256_file(report),
        "desktop_dir": str(desktop),
    }
    values.update(overrides)
    return run_open_chrome_slash_path_enter_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_open_chrome_slash_path_enter_no_send(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND
    assert result.selected_action == "upload_self_report_open_chrome_slash_full_path_enter_no_send"
    assert result.chrome_open_invoked is True
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.mouse_clicks_used is False
    assert result.slash_key_pressed is True
    assert result.upload_command_enter_pressed is True
    assert result.enter_key_pressed_in_chat_composer is False
    assert result.picker_opened is True
    assert result.full_path_pasted_to_picker is True
    assert result.filename_only_written_to_picker is False
    assert result.open_button_clicked is False
    assert result.ctrl_v_pressed_in_picker is True
    assert result.picker_enter_pressed is True
    assert result.enter_key_pressed_in_picker is True
    assert result.attachment_verified is True
    assert result.operator_report_attached_to_composer is True
    assert result.file_upload_attempted is True
    assert result.operator_report_uploaded is False
    assert result.chatgpt_submit_performed is False
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
    assert result.result_label == BLOCKED_CHROME_OPEN_SLASH_REPORT_NOT_ON_DESKTOP
    assert result.browser_action_performed is False


def test_confirmation_and_live_browser_required(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    assert run_ready(report, desktop, confirmation_text=None).result_label == BLOCKED_CHROME_OPEN_SLASH_CONFIRMATION_REQUIRED
    assert run_ready(report, desktop, confirmation_text="WRONG").result_label == BLOCKED_CHROME_OPEN_SLASH_CONFIRMATION_MISMATCH
    assert run_ready(report, desktop, live_browser=False).result_label == BLOCKED_CHROME_OPEN_SLASH_LIVE_BROWSER_REQUIRED


def test_fake_picker_failures(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    assert run_ready(report, desktop, provider="fake-no-picker").result_label == BLOCKED_CHROME_OPEN_SLASH_PICKER_NOT_OPENED
    assert run_ready(report, desktop, provider="fake-paste-failed").result_label == BLOCKED_CHROME_OPEN_SLASH_PATH_PASTE_FAILED
    assert run_ready(report, desktop, provider="fake-enter-failed").result_label == BLOCKED_CHROME_OPEN_SLASH_PICKER_ENTER_FAILED


def test_write_open_chrome_slash_path_enter_evidence(tmp_path: Path) -> None:
    desktop, report = make_desktop_report(tmp_path)
    result = run_ready(report, desktop)
    json_path = tmp_path / "open_chrome_slash_path.json"
    txt_path = tmp_path / "open_chrome_slash_path.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["result_label"] == PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND
    assert payload["chrome_open_invoked"] is True
    assert payload["mouse_clicks_used"] is False
    assert payload["slash_key_pressed"] is True
    assert payload["upload_command_enter_pressed"] is True
    assert payload["full_path_pasted_to_picker"] is True
    assert payload["ctrl_v_pressed_in_picker"] is True
    assert payload["picker_enter_pressed"] is True
    assert payload["open_button_clicked"] is False
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert TARGET_URL not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND" in text
    assert "mouse_clicks_used: false" in text
    assert "full_path_pasted_to_picker: true" in text
    assert "picker_enter_pressed: true" in text
    assert "send_button_pressed: false" in text


def test_source_contract_open_chrome_no_clicks_slash_path_enter() -> None:
    source = Path("patchops/chatgpt_uploader/chrome_self_report_open_chrome_slash_path_enter_no_send.py").read_text(encoding="utf-8")

    assert "subprocess.Popen([chrome, target_url]" in source
    assert 'keyboard.send_keys("/", pause=0.05)' in source
    assert 'keyboard.send_keys("{ENTER}", pause=0.05)' in source
    assert "set_clipboard_text(str(report_path.resolve(strict=False)))" in source
    assert 'send_keys("^v"' in source
    assert "click_input" not in source
    assert 'send_keys("{TAB}"' not in source