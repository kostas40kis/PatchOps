from __future__ import annotations

import json
from pathlib import Path

SCRIPT = Path("scripts/run_pseudo_self_report_foreground_picker_low_level_paste_enter_no_send_apply_smoke.py")


def test_source_contract_uses_low_level_paste_enter_no_new_tab_no_clicks() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "subprocess.Popen" not in source
    assert "os.startfile" not in source
    assert "click_input" not in source
    assert 'keyboard.send_keys("/", pause=0.05)' in source
    assert 'keyboard.send_keys("{ENTER}", pause=0.05)' in source
    assert "foreground_looks_like_picker()" in source
    assert "set_clipboard_text(str(report_path.resolve(strict=False)))" in source
    assert "send_ctrl_v_low_level()" in source
    assert "send_enter_low_level()" in source
    assert "VK_CONTROL" in source
    assert "VK_V" in source
    assert "VK_RETURN" in source
    assert 'send_keys("^v"' not in source
    assert 'send_keys("{TAB}"' not in source


def test_fake_ready_writes_expected_evidence(tmp_path: Path) -> None:
    from importlib.machinery import SourceFileLoader

    module = SourceFileLoader("fg_picker_smoke", str(SCRIPT)).load_module()
    desktop = tmp_path / "Desktop"
    desktop.mkdir()
    report = desktop / "pseudo_self_report_upload_no_send_repair_14_foreground_picker_low_level_paste_enter_self_report.txt"
    report.write_text("fake report\n", encoding="utf-8")
    target_url = "https://chatgpt.com/g/g-p-test/c/test"
    config = {"status_chat": {"enabled": True, "browser_lane": "chrome", "target_url": target_url, "target_url_sha256": module.sha256_text(target_url)}}

    result = module.run_smoke(
        config_payload=config,
        config_path=tmp_path / "config.json",
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
    assert payload["clipboard_text_written"] is True
    assert payload["full_path_pasted_to_picker"] is True
    assert payload["low_level_ctrl_v_sent"] is True
    assert payload["low_level_enter_sent"] is True
    assert payload["picker_enter_pressed"] is True
    assert payload["send_button_pressed"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["operator_report_uploaded"] is False
    assert target_url not in json_path.read_text(encoding="utf-8")

    text = txt_path.read_text(encoding="utf-8")
    assert "low_level_ctrl_v_sent: true" in text
    assert "low_level_enter_sent: true" in text
    assert "send_button_pressed: false" in text