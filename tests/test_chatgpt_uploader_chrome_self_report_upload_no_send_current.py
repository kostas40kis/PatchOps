from __future__ import annotations

from pathlib import Path

from patchops.chatgpt_uploader.chrome_self_report_upload_no_send import (
    BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_CONTROL_NOT_FOUND,
    BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_NOT_VERIFIED,
    BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_MISMATCH,
    BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_REQUIRED,
    BLOCKED_CHROME_SELF_REPORT_FILE_PICKER_NOT_READY,
    BLOCKED_CHROME_SELF_REPORT_HASH_MISMATCH,
    BLOCKED_CHROME_SELF_REPORT_LIVE_BROWSER_REQUIRED,
    BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND,
    BLOCKED_CHROME_SELF_REPORT_PATH_MISSING,
    BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY,
    CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND,
    PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND,
    run_self_report_upload_no_send,
    sha256_file,
    sha256_text,
    write_evidence,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69fb24e234b08191b691f750f5405732-patchops/c/69fc5f46-6e88-83eb-82b8-58a779a43ddd"


def make_report(tmp_path: Path) -> Path:
    report = tmp_path / "pseudo_self_report_upload_no_send_report.txt"
    report.write_text("pseudo patch self report\n", encoding="utf-8")
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
        "confirmation_text": CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND,
        "self_report_path": str(report),
        "expected_self_report_sha256": sha256_file(report),
    }
    values.update(overrides)
    return run_self_report_upload_no_send(**values)  # type: ignore[arg-type]


def test_fake_ready_attaches_self_report_no_send(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)

    assert result.ok is True
    assert result.result_label == PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
    assert result.selected_action == "upload_self_report_no_send"
    assert result.browser_lane == "chrome"
    assert result.live_browser is True
    assert result.stop_before_send is True
    assert result.confirmation_matched is True
    assert result.self_report_path == str(report)
    assert result.self_report_sha256 == sha256_file(report)
    assert result.computed_self_report_sha256 == sha256_file(report)
    assert result.chrome_target_ready is True
    assert result.chrome_target_focused is True
    assert result.attachment_control_found is True
    assert result.file_picker_used is True
    assert result.file_picker_opened is True
    assert result.file_path_written is True
    assert result.open_button_clicked is True
    assert result.enter_key_pressed is False
    assert result.attachment_verified is True
    assert result.operator_report_attached_to_composer is True
    assert result.browser_action_performed is True
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
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_REQUIRED
    assert result.browser_action_performed is False


def test_confirmation_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, confirmation_text="WRONG")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_CONFIRMATION_MISMATCH
    assert result.browser_action_performed is False


def test_live_browser_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, live_browser=False)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_LIVE_BROWSER_REQUIRED
    assert result.browser_action_performed is False


def test_report_path_required(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, self_report_path=None, expected_self_report_sha256=None)

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_PATH_MISSING


def test_report_hash_must_match(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, expected_self_report_sha256="wrong")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_HASH_MISMATCH
    assert result.browser_action_performed is False


def test_fake_no_target_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-target")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY
    assert result.send_button_pressed is False


def test_fake_no_attachment_control_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-attachment-control")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_CONTROL_NOT_FOUND
    assert result.file_upload_attempted is False


def test_fake_no_dialog_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-dialog")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_FILE_PICKER_NOT_READY


def test_fake_no_open_button_blocks_without_enter(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-no-open-button")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND
    assert result.enter_key_pressed is False
    assert result.send_button_pressed is False


def test_fake_not_verified_blocks(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report, provider="fake-not-verified")

    assert result.ok is False
    assert result.result_label == BLOCKED_CHROME_SELF_REPORT_ATTACHMENT_NOT_VERIFIED
    assert result.open_button_clicked is True
    assert result.enter_key_pressed is False


def test_write_evidence_no_send_flags(tmp_path: Path) -> None:
    report = make_report(tmp_path)
    result = run_ready(report)
    json_path = tmp_path / "self_report_upload.json"
    txt_path = tmp_path / "self_report_upload.txt"

    write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)

    raw_json = json_path.read_text(encoding="utf-8")
    assert TARGET_URL not in raw_json
    assert "Google Chrome" not in raw_json
    assert '"enter_key_pressed": false' in raw_json
    assert '"send_button_pressed": false' in raw_json
    assert '"chatgpt_submit_performed": false' in raw_json
    assert '"browser_dom_automation_used": false' in raw_json

    text = txt_path.read_text(encoding="utf-8")
    assert "result_label: PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND" in text
    assert "open_button_clicked: true" in text
    assert "enter_key_pressed: false" in text
    assert "send_button_pressed: false" in text

def test_attachment_token_list_includes_current_chatgpt_variants() -> None:
    from patchops.chatgpt_uploader.chrome_self_report_upload_no_send import ATTACHMENT_NAME_TOKENS

    for token in ("attach", "attachment", "add file", "files", "photos", "plus"):
        assert token in ATTACHMENT_NAME_TOKENS

def test_upload_menu_tokens_included() -> None:
    from patchops.chatgpt_uploader.chrome_self_report_upload_no_send import ATTACHMENT_NAME_TOKENS, FILE_DIALOG_TITLE_TOKENS

    assert "upload files" in ATTACHMENT_NAME_TOKENS
    assert "upload file" in ATTACHMENT_NAME_TOKENS
    assert "select" in FILE_DIALOG_TITLE_TOKENS