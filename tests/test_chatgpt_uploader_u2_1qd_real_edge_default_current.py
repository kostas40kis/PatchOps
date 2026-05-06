from __future__ import annotations

from pathlib import Path


def test_u2_1qd_real_edge_default_is_true_and_roundtrips(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, load_config, write_config

    target = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
    cfg = ChatGPTUploaderConfig.create(target)

    assert cfg.browser == "msedge"
    assert cfg.mode == "operator_set"
    assert cfg.allow_real_edge_default is True
    assert cfg.real_edge_default is True
    assert cfg.allow_upload is False
    assert cfg.allow_send is False

    path = tmp_path / "target.json"
    assert write_config(cfg, path) == path.resolve()

    loaded = load_config(path)
    assert loaded.allow_real_edge_default is True
    assert loaded.real_edge_default is True
    assert loaded == cfg


def test_u2_1qd_explicit_false_real_edge_default_is_preserved() -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig

    cfg = ChatGPTUploaderConfig.create("https://chatgpt.com/", allow_real_edge_default=False)
    assert cfg.allow_real_edge_default is False
    assert cfg.real_edge_default is False
