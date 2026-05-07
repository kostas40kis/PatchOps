from __future__ import annotations

import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT = Path("scripts/run_pseudo_self_report_operator_observed_type_path_no_send_apply_smoke.py")


def test_source_contract_operator_observed_no_ui_step_validation() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "operator_observed_mode=True" in source
    assert "automated_ui_step_validation_used=False" in source
    assert "automated_attachment_verification_used=False" in source
    assert "foreground_looks_like_picker" not in source
    assert "GetForegroundWindow" not in source
    assert "GetDlgItem" not in source
    assert "SetWindowTextW" not in source
    assert "SendInput" not in source
    assert "click_input" not in source
    assert "subprocess.Popen" not in source
    assert "os.startfile" not in source
    assert 'keyboard.send_keys("/", pause=0.05)' in source
    assert 'keyboard.send_keys("{ENTER}", pause=0.05)' in source
    assert "send_literal_path(path_text)" in source
    assert "vk_packet=True" in source
    assert 'send_keys("^v"' not in source
    assert 'send_keys("{TAB}"' not in source


def test_fake_ready_operator_observed_attempt_evidence(tmp_path: Path) -> None:
    module = SourceFileLoader("operator_observed_type_path", str(SCRIPT)).load_module()
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_no_send_repair_17_operator_observed_type_path_self_report.txt"
    report.write_text("fake report\n", encoding="utf-8")
    target_url = "https://chatgpt.com/g/g-p-test/c/test"
    config = {"status_chat": {"enabled": True, "browser_lane": "chrome", "target_url": target_url, "target_url_sha256": module.sha256_text(target_url)}}

    result = module.run_attempt(
        config_payload=config,
        provider="fake-ready",
        live_browser=True,
        confirmation_text=module.CONFIRM_TEXT,
        self_report_path=str(report),
        expected_sha256=module.sha256_file(report),
        desktop_dir=desktop,
        slash_delay=0.01,
        picker_ready_delay=0.01,
        after_type_delay=0.01,
    )
    json_path = tmp_path / "evidence.json"
    txt_path = tmp_path / "evidence.txt"
    module.write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["result_label"] == module.RESULT_LABEL
    assert payload["ok"] is True
    assert payload["operator_observed_mode"] is True
    assert payload["automated_ui_step_validation_used"] is False
    assert payload["automated_attachment_verification_used"] is False
    assert payload["chrome_open_invoked"] is False
    assert payload["mouse_clicks_used"] is False
    assert payload["slash_key_attempted"] is True
    assert payload["upload_command_enter_attempted"] is True
    assert payload["full_path_type_attempted"] is True
    assert payload["picker_enter_attempted"] is True
    assert payload["operator_must_confirm_visible_result"] is True
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert target_url not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "operator_observed_mode: true" in text
    assert "automated_ui_step_validation_used: false" in text
    assert "full_path_type_attempted: true" in text
    assert "send_button_pressed: false" in text