from __future__ import annotations

import json
from pathlib import Path


TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_u2_1ql_loaded_config_equals_written_path(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import read_target_config, write_target_config

    path = tmp_path / "target.json"
    written = write_target_config(path, target_url=TARGET_URL, source_patch="u2_1ql")
    loaded = read_target_config(path)

    assert written == path.resolve()
    assert loaded == written
    assert loaded == path.resolve()


def test_u2_1ql_write_evidence_basename_compat(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.evidence import finalize_evidence, new_evidence, write_evidence

    evidence = new_evidence("unit_u2_1ql", target_url=TARGET_URL, target_config_path=tmp_path / "target.json")
    finalize_evidence(evidence, status="PASS", result_label="PASS", reason="unit proof")

    paths = write_evidence(evidence, tmp_path, basename="evidence")

    assert paths.json_path == tmp_path.resolve() / "evidence.json"
    assert paths.txt_path == tmp_path.resolve() / "evidence.txt"
    assert paths.json_path.exists()
    assert paths.txt_path.exists()

    payload = json.loads(paths.json_path.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["result_label"] == "PASS"
    assert payload["reason"] == "unit proof"
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False

    text = paths.txt_path.read_text(encoding="utf-8")
    assert "FILE_UPLOAD_ATTEMPTED: false" in text
    assert "CHATGPT_SUBMIT_PERFORMED: false" in text
