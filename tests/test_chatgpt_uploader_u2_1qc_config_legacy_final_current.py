from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_u2_1qc_config_legacy_final_compatibility(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, load_config, write_config

    target = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
    cfg = ChatGPTUploaderConfig.create(target)

    assert cfg.browser == "msedge"
    assert cfg.mode == "operator_set"
    assert cfg.allow_real_edge_default is True
    assert cfg.allow_upload is False
    assert cfg.allow_send is False

    path = tmp_path / "target.json"
    assert write_config(cfg, path) == path.resolve()
    loaded = load_config(path)
    assert loaded == cfg


def test_u2_1qc_setter_plain_output_has_legacy_marker(tmp_path: Path) -> None:
    script = PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"
    config_path = tmp_path / "target.json"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            "https://chatgpt.com",
            "--mode",
            "operator_set",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "TARGET_CONFIG_WRITTEN:" in result.stdout
    assert str(config_path.resolve()) in result.stdout
