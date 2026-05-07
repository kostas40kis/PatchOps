from __future__ import annotations

import json
from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT = Path("scripts/run_pseudo_self_report_foreground_picker_edit_set_text_no_send_apply_smoke.py")


def test_source_contract_sets_picker_edit_text_no_clipboard_no_clicks() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "subprocess.Popen" not in source
    assert "os.startfile" not in source
    assert "click_input" not in source
    assert 'keyboard.send_keys("/", pause=0.05)' in source
    assert 'keyboard.send_keys("{ENTER}", pause=0.05)' in source
    assert "foreground_looks_like_picker()" in source
    assert "_picker_edit_candidates" in source
    assert "edit.set_edit_text(full_path)" in source
    assert "full_path_written_to_picker=True" in source
    assert "send_ctrl_v_low_level" not in source
    assert "SendInput" not in source
    assert 'send_keys("^v"' not in source
    assert 'send_keys("{TAB}"' not in source


def test_fake_ready_writes_expected_evidence(tmp_path: Path) -> None:
    module = SourceFileLoader("fg_picker_edit_smoke", str(SCRIPT)).load_module()
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_no_send_repair_15_foreground_picker_edit_set_text_self_report.txt"
    report.write_text("fake report\n", encoding="utf-8")
    target_url = "https://chatgpt.com/g/g-p-test/c/test"
    config = {"status_chat": {"enabled": True, "browser_lane": "chrome", "target_url": target_url, "target_url_sha256": module.sha256_text(target_url)}}

    result = module.run_smoke(
        config_payload=config,
        provider="fake-ready",
        live_browser=True,
        confirmation_text=module.CONFIRM_TEXT,
        self_report_path=str(report),
        expected_sha256=module.sha256_file(report),
        desktop_dir=desktop,
    )
    json_path = tmp_path / "evidence.json"
    txt_path = tmp_path / "evidence.txt"
    module.write_evidence(result, json_output_path=json_path, txt_output_path=txt_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["result_label"] == module.PASS_LABEL
    assert payload["chrome_open_invoked"] is False
    assert payload["mouse_clicks_used"] is False
    assert payload["foreground_picker_ready"] is True
    assert payload["picker_edit_found"] is True
    assert payload["picker_edit_value_set"] is True
    assert payload["picker_edit_verified"] is True
    assert payload["full_path_written_to_picker"] is True
    assert payload["clipboard_text_written"] is False
    assert payload["ctrl_v_pressed_in_picker"] is False
    assert payload["low_level_ctrl_v_sent"] is False
    assert payload["picker_enter_pressed"] is True
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert target_url not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "picker_edit_value_set: true" in text
    assert "full_path_written_to_picker: true" in text
    assert "send_button_pressed: false" in text