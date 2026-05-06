from __future__ import annotations

import json
from pathlib import Path

import pytest


TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_u2_1qk_write_target_config_keyword_compat_and_redaction(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import read_target_config, redact_target_url, write_target_config

    config_path = tmp_path / "target.json"
    written = write_target_config(config_path, target_url=TARGET_URL, source_patch="u2_1qk")

    assert written == config_path.resolve()
    payload = json.loads(config_path.read_text(encoding="utf-8"))

    assert payload["target_url"] == TARGET_URL
    assert payload["source_patch"] == "u2_1qk"
    assert payload["target_url_sha256"]
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False

    redacted = redact_target_url(TARGET_URL)
    assert redacted.startswith("https://chatgpt.com/")
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in redacted
    assert "69f8530a" in redacted
    assert "<conversation>" in redacted
    assert "<redacted>" in redacted

    loaded = read_target_config(config_path)
    assert loaded.target_url == TARGET_URL


def test_u2_1qk_empty_target_url_rejected() -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, validate_target_url, write_target_config

    with pytest.raises(ValueError):
        validate_target_url("")
    with pytest.raises(ValueError):
        ChatGPTUploaderConfig.create("")
    with pytest.raises(ValueError):
        write_target_config(Path("target.json"), target_url="")


def test_u2_1qk_finalize_evidence_accepts_result_label_without_result(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.evidence import finalize_evidence, new_evidence

    evidence = new_evidence("unit_u2_1qk", target_url=TARGET_URL, target_config_path=tmp_path / "target.json")
    finalized = finalize_evidence(evidence, status="PASS", result_label="PASS", reason="unit proof")

    assert finalized is not None
