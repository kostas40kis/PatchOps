from __future__ import annotations

from pathlib import Path


def test_u2_1qa_config_api_exports_and_roundtrip(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader import config as cfg

    required = [
        "UploaderConfig",
        "create_default_config",
        "write_config",
        "read_config",
        "load_config",
        "save_config",
        "normalize_target_url",
        "validate_target_url",
        "redact_target_url",
        "default_config_path",
    ]
    for name in required:
        assert hasattr(cfg, name), name

    created = cfg.create_default_config(target_url="https://chatgpt.com/")
    assert created.allow_upload is False
    assert created.allow_send is False
    assert created.allow_browser_launch is False
    assert created.target_url == "https://chatgpt.com/"

    path = tmp_path / "chatgpt_copilot_target.json"
    written = cfg.write_config(created, path)
    assert written == path.resolve()

    loaded = cfg.load_config(path)
    assert loaded.target_url == "https://chatgpt.com/"
    assert loaded.allow_upload is False
    assert loaded.allow_send is False
    assert loaded.to_payload()["chatgpt_submit_performed"] is False

    saved = cfg.save_config({"target_url": "https://chatgpt.com/g/demo/c/abc123def456", "allow_upload": False}, path)
    assert saved == path.resolve()

    reloaded = cfg.read_config(path)
    assert reloaded.target_url.startswith("https://chatgpt.com/")
    assert "abc123def456" not in cfg.redact_target_url(reloaded.target_url)
    assert "<redacted>" in cfg.redact_target_url(reloaded.target_url)


def test_u2_1qa_config_rejects_non_chatgpt_target() -> None:
    from patchops.chatgpt_uploader import config as cfg

    assert cfg.normalize_target_url("https://chatgpt.com") == "https://chatgpt.com/"
    assert cfg.validate_target_url("https://chatgpt.com/") == "https://chatgpt.com/"

    try:
        cfg.validate_target_url("https://example.com/")
    except Exception as exc:
        assert "chatgpt.com" in str(exc).lower() or isinstance(exc, ValueError)
    else:
        raise AssertionError("non-chatgpt target should be rejected")
