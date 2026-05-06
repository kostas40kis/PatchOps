from __future__ import annotations

import json

from patchops.chatgpt_uploader.evidence import REQUIRED_SAFETY_FLAG_NAMES, default_safety_flags, finalize_evidence, new_evidence, write_evidence

TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_default_safety_flags_are_all_false() -> None:
    flags = default_safety_flags()
    assert set(flags) == set(REQUIRED_SAFETY_FLAG_NAMES)
    assert all(value is False for value in flags.values())


def test_evidence_writes_json_and_txt(tmp_path) -> None:
    evidence = new_evidence("unit_u2_0", target_url=TARGET_URL, target_config_path=tmp_path / "target.json")
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
    assert "file_upload_attempted: False" in text
    assert "chatgpt_submit_performed: False" in text
