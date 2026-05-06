from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, ConfigValidationError, load_config, redact_target_url, target_url_sha256, write_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT_TARGET = "https://chatgpt.com/"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def test_root_chatgpt_target_is_valid_and_normalized() -> None:
    cfg = ChatGPTUploaderConfig.create("https://chatgpt.com")
    assert cfg.target_url == ROOT_TARGET
    assert cfg.target_url_sha256 == target_url_sha256(ROOT_TARGET)
    assert cfg.allow_upload_default is False
    assert cfg.allow_send_default is False


def test_root_chatgpt_target_redaction_keeps_only_root() -> None:
    assert redact_target_url(ROOT_TARGET) == ROOT_TARGET


def test_root_config_write_read_roundtrip(tmp_path) -> None:
    path = tmp_path / "target.json"
    cfg = ChatGPTUploaderConfig.create(ROOT_TARGET, mode="operator_set")
    write_config(cfg, path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["target_url"] == ROOT_TARGET
    assert payload["target_url_redacted"] == ROOT_TARGET
    assert payload["allow_upload_default"] is False
    assert payload["allow_send_default"] is False
    loaded = load_config(path)
    assert loaded.target_url == ROOT_TARGET


def test_non_chatgpt_root_is_still_rejected() -> None:
    with pytest.raises(ConfigValidationError):
        ChatGPTUploaderConfig.create("https://example.com/")


def test_setter_accepts_root_chatgpt_target(tmp_path) -> None:
    config_path = tmp_path / "target.json"
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
            "--target-url",
            ROOT_TARGET,
            "--mode",
            "operator_set",
        ],
        cwd=PROJECT_ROOT,
        env=_env(),
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "TARGET_CONFIG_WRITTEN:" in result.stdout
    assert "TARGET_URL_REDACTED: https://chatgpt.com/" in result.stdout
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["target_url"] == ROOT_TARGET
    assert payload["allow_upload_default"] is False
    assert payload["allow_send_default"] is False
