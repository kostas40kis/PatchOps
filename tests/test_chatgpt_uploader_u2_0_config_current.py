from __future__ import annotations

import json

import pytest

from patchops.chatgpt_uploader.config import (
    ChatGPTUploaderConfig,
    ConfigValidationError,
    load_config,
    redact_target_url,
    target_url_sha256,
    write_config,
)

TARGET_URL = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"


def test_config_create_defaults_are_no_upload_no_send() -> None:
    cfg = ChatGPTUploaderConfig.create(TARGET_URL)
    assert cfg.browser == "msedge"
    assert cfg.mode == "operator_set"
    assert cfg.allow_real_edge_default is True
    assert cfg.allow_upload_default is False
    assert cfg.allow_send_default is False
    assert cfg.target_url_sha256 == target_url_sha256(TARGET_URL)


def test_config_write_read_roundtrip(tmp_path) -> None:
    path = tmp_path / "target.json"
    cfg = ChatGPTUploaderConfig.create(TARGET_URL)
    write_config(cfg, path)
    loaded = load_config(path)
    assert loaded == cfg
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["target_url_sha256"] == target_url_sha256(TARGET_URL)
    assert payload["allow_upload_default"] is False
    assert payload["allow_send_default"] is False


def test_redacted_url_hides_conversation_id() -> None:
    redacted = redact_target_url(TARGET_URL)
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in redacted
    assert "<conversation>" in redacted
    assert redacted.startswith("https://chatgpt.com/")


def test_invalid_target_rejected() -> None:
    with pytest.raises(ConfigValidationError):
        ChatGPTUploaderConfig.create("http://example.com/not-chatgpt")
