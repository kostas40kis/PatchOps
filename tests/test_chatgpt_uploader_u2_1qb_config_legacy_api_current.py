from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_u2_1qb_chatgpt_uploader_config_legacy_create_roundtrip(tmp_path: Path) -> None:
    from patchops.chatgpt_uploader.config import ChatGPTUploaderConfig, ConfigValidationError, read_config, redact_target_url, write_config

    target = "https://chatgpt.com/g/g-p-69c28e6fc27881919f542bcccbe34314-wrapper/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
    cfg = ChatGPTUploaderConfig.create(target, mode="operator_set")

    assert cfg.target_url == target
    assert cfg.mode == "operator_set"
    assert cfg.allow_upload is False
    assert cfg.allow_send is False

    redacted = redact_target_url(target)
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in redacted
    assert "<conversation>" in redacted

    path = tmp_path / "target.json"
    assert write_config(path, cfg) == path.resolve()
    loaded = read_config(path)
    assert loaded.target_url == target
    assert loaded.mode == "operator_set"

    assert cfg.write(path) == path.resolve()
    assert ChatGPTUploaderConfig.read(path).target_url == target

    try:
        ChatGPTUploaderConfig.create("https://example.com/")
    except ConfigValidationError:
        pass
    else:
        raise AssertionError("non-chatgpt target should be rejected")


def test_u2_1qb_target_setter_accepts_repo_root_and_target_config_aliases(tmp_path: Path) -> None:
    config_path = tmp_path / "target.json"
    script = PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py"

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
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["target_config_path"] == str(config_path.resolve())
    assert payload["target_url"] == "https://chatgpt.com/"
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False

    written = json.loads(config_path.read_text(encoding="utf-8"))
    assert written["target_url"] == "https://chatgpt.com/"
    assert written["mode"] == "operator_set"
