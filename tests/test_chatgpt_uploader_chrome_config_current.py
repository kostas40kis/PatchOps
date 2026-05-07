from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from patchops.chatgpt_uploader import config as cfg

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_URL = "https://chatgpt.com/g/g-p-demo/c/69f8530a-cc98-83eb-8a76-b34eaa36070d"
REJECTED_BROWSERS = ["edge", "msedge", "opera", "brave", "vivaldi", "firefox", "chromium", "any", "auto", "default", "all"]


def test_chrome_config_accepts_only_chrome_by_default() -> None:
    created = cfg.ChatGPTUploaderConfig.create(TARGET_URL)
    payload = created.to_payload()

    assert cfg.SUPPORTED_BROWSERS == {"chrome"}
    assert cfg.VALID_BROWSERS == {"chrome"}
    assert cfg.supported_browser_lanes() == ("chrome",)
    assert created.browser == "chrome"
    assert payload["browser"] == "chrome"
    assert payload["expected_browser"] == "chrome"
    assert payload["result"] == "PASS_CHROME_CONFIG_VALIDATED"
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False
    assert payload["selenium_used"] is False
    assert payload["webdriver_used"] is False
    assert payload["browser_dom_automation_used"] is False


def test_chrome_config_rejects_non_chrome_browser_values() -> None:
    for browser in REJECTED_BROWSERS:
        with pytest.raises(cfg.ConfigValidationError) as excinfo:
            cfg.ChatGPTUploaderConfig.create(TARGET_URL, browser=browser)
        assert "BLOCKED_UNSUPPORTED_BROWSER" in str(excinfo.value)

    assert set(REJECTED_BROWSERS).issubset(set(cfg.rejected_browser_lanes()))
    assert cfg.chrome_config_acceptance_labels()["pass"] == "PASS_CHROME_CONFIG_VALIDATED"
    assert cfg.chrome_config_acceptance_labels()["unsupported_browser"] == "BLOCKED_UNSUPPORTED_BROWSER"
    assert cfg.chrome_config_acceptance_labels()["invalid_config"] == "BLOCKED_CONFIG_INVALID"


def test_chrome_config_write_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "target.json"
    created = cfg.ChatGPTUploaderConfig.create(TARGET_URL, browser="chrome")

    written = cfg.write_config(created, path)
    assert written == path.resolve()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["browser"] == "chrome"
    assert payload["expected_browser"] == "chrome"
    assert payload["result"] == "PASS_CHROME_CONFIG_VALIDATED"
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False

    loaded = cfg.load_config(path)
    assert loaded.browser == "chrome"
    assert loaded.to_payload()["browser"] == "chrome"


def test_chrome_config_rejects_unsupported_browser_from_file(tmp_path: Path) -> None:
    for browser in ["msedge", "edge", "any", "auto", "all"]:
        path = tmp_path / f"{browser}.json"
        path.write_text(
            json.dumps({"target_url": TARGET_URL, "browser": browser, "mode": "operator_set"}),
            encoding="utf-8",
        )
        with pytest.raises(cfg.ConfigValidationError) as excinfo:
            cfg.load_config(path)
        assert "BLOCKED_UNSUPPORTED_BROWSER" in str(excinfo.value)


def test_chrome_target_setter_accepts_chrome_and_rejects_old_browsers(tmp_path: Path) -> None:
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
            TARGET_URL,
            "--browser",
            "chrome",
            "--json",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["browser"] == "chrome"
    assert payload["result"] == "PASS_CHROME_CONFIG_VALIDATED"
    assert payload["file_upload_attempted"] is False
    assert payload["chatgpt_submit_performed"] is False

    written = json.loads(config_path.read_text(encoding="utf-8"))
    assert written["browser"] == "chrome"

    blocked = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(tmp_path / "blocked.json"),
            "--target-url",
            TARGET_URL,
            "--browser",
            "msedge",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert blocked.returncode != 0
    assert "msedge" in blocked.stderr.lower()


def test_chrome_target_show_redacts_url_and_reports_chrome(tmp_path: Path) -> None:
    config_path = tmp_path / "target.json"
    cfg.write_config(cfg.ChatGPTUploaderConfig.create(TARGET_URL), config_path)

    script = PROJECT_ROOT / "scripts" / "show_chatgpt_copilot_target.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-config",
            str(config_path),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "TARGET_CONFIG_STATUS: OK" in result.stdout
    assert "CHROME_CONFIG_STATUS: PASS_CHROME_CONFIG_VALIDATED" in result.stdout
    assert "BROWSER: chrome" in result.stdout
    assert "RAW_TARGET_URL_PRINTED: false" in result.stdout
    assert "69f8530a-cc98-83eb-8a76-b34eaa36070d" not in result.stdout


def test_chrome_config_patch_does_not_introduce_generic_browser_files() -> None:
    forbidden_files = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_factory.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_adapter.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "browser_registry.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "all_browsers.py",
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "generic_browser.py",
    ]

    for path in forbidden_files:
        assert not path.exists(), path


def test_chrome_config_files_do_not_import_forbidden_automation() -> None:
    paths = [
        PROJECT_ROOT / "patchops" / "chatgpt_uploader" / "config.py",
        PROJECT_ROOT / "scripts" / "set_chatgpt_copilot_target.py",
        PROJECT_ROOT / "scripts" / "show_chatgpt_copilot_target.py",
    ]

    forbidden = ["import selenium", "from selenium", "webdriver.chrome", "webdriver.edge", "chromedriver"]
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text