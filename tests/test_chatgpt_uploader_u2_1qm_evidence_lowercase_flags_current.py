from __future__ import annotations

import json
from pathlib import Path


TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_u2_1qm_write_evidence_text_has_upper_and_lower_legacy_flags(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.evidence import finalize_evidence, new_evidence, write_evidence

    evidence = new_evidence("unit_u2_1qm", target_url=TARGET_URL, target_config_path=tmp_path / "target.json")
    finalize_evidence(evidence, status="PASS", result_label="PASS", reason="unit proof")

    paths = write_evidence(evidence, tmp_path, basename="evidence")

    assert paths.json_path.exists()
    assert paths.txt_path.exists()

    payload = json.loads(paths.json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["result_label"] == "PASS"
    assert payload["safety_flags"]["file_upload_attempted"] is False
    assert payload["safety_flags"]["chatgpt_submit_performed"] is False

    text = paths.txt_path.read_text(encoding="utf-8")
    assert "PATCHOPS CHATGPT UPLOADER EVIDENCE" in text

    assert "FILE_UPLOAD_ATTEMPTED: false" in text
    assert "CHATGPT_SUBMIT_PERFORMED: false" in text

    assert "file_upload_attempted: False" in text
    assert "chatgpt_submit_performed: False" in text
    assert "conversation_text_logged: False" in text
    assert "selenium_used: False" in text
    assert "webdriver_used: False" in text
    assert "browser_dom_automation_used: False" in text
