from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

from patchops import cli
from patchops.llm_browser import opera_controller
from patchops.llm_browser.browser_factory import (
    BrowserFactoryError,
    build_opera_options,
    create_opera_driver,
)
from patchops.llm_browser.models import BrowserRunConfig


class FakeChromeOptions:
    def __init__(self) -> None:
        self.arguments: list[str] = []
        self.experimental_options: dict[str, object] = {}
        self.binary_location: str | None = None

    def add_argument(self, value: str) -> None:
        self.arguments.append(value)

    def add_experimental_option(self, name: str, value: object) -> None:
        self.experimental_options[name] = value


class FakeChromeDriver:
    created_with_options: FakeChromeOptions | None = None

    def __init__(self, *, options: FakeChromeOptions) -> None:
        self.options = options
        self.visited_urls: list[str] = []
        FakeChromeDriver.created_with_options = options

    def get(self, url: str) -> None:
        self.visited_urls.append(url)


def _config(tmp_path: Path) -> BrowserRunConfig:
    downloads = tmp_path / "Downloads"
    downloads.mkdir(exist_ok=True)
    return BrowserRunConfig(
        browser="opera",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=tmp_path / "opera_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=False,
        auto_paste=False,
    )


def test_browser_factory_import_does_not_import_selenium_for_opera() -> None:
    sys.modules.pop("patchops.llm_browser.browser_factory", None)
    before = set(sys.modules)

    module = importlib.import_module("patchops.llm_browser.browser_factory")

    loaded = set(sys.modules) - before
    assert "selenium" not in loaded
    assert hasattr(module, "create_opera_driver")


def test_build_opera_options_sets_profile_downloads_and_binary(tmp_path: Path) -> None:
    config = _config(tmp_path)
    opera_path = tmp_path / "opera.exe"

    options = build_opera_options(config, opera_executable_path=opera_path, options_cls=FakeChromeOptions)

    assert options.binary_location == str(opera_path)
    assert f"--user-data-dir={config.profile_dir}" in options.arguments
    assert "--disable-notifications" in options.arguments
    prefs = options.experimental_options["prefs"]
    assert isinstance(prefs, dict)
    assert prefs["download.default_directory"] == str(config.download_dir)
    assert prefs["download.prompt_for_download"] is False
    assert prefs["download.directory_upgrade"] is True


def test_build_opera_options_rejects_non_opera_config(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    config = BrowserRunConfig(
        browser="edge",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=tmp_path / "edge_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=False,
        auto_paste=False,
    )

    with pytest.raises(BrowserFactoryError, match="only supports opera"):
        build_opera_options(config, options_cls=FakeChromeOptions)


def test_create_opera_driver_uses_path_discovery_and_injected_driver(tmp_path: Path) -> None:
    config = _config(tmp_path)
    opera_exe = tmp_path / "opera.exe"
    opera_exe.write_text("", encoding="utf-8")

    driver = create_opera_driver(
        config,
        chrome_cls=FakeChromeDriver,
        options_cls=FakeChromeOptions,
        exists=lambda path: path == opera_exe,
        environ={"PATCHOPS_OPERA_PATH": str(opera_exe)},
    )

    assert isinstance(driver, FakeChromeDriver)
    assert driver.options.binary_location == str(opera_exe)
    assert f"--user-data-dir={config.profile_dir}" in driver.options.arguments


def test_create_opera_driver_returns_clear_missing_opera_error(tmp_path: Path) -> None:
    config = _config(tmp_path)

    with pytest.raises(FileNotFoundError, match="opera executable was not found"):
        create_opera_driver(
            config,
            chrome_cls=FakeChromeDriver,
            options_cls=FakeChromeOptions,
            exists=lambda _path: False,
            environ={},
        )


def test_open_opera_navigates_to_chat_url_with_fake_driver(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeChromeDriver(options=FakeChromeOptions())

    result = opera_controller.open_opera(config, driver_factory=lambda _config: driver)

    assert result.browser == "opera"
    assert result.navigated is True
    assert driver.visited_urls == ["https://chatgpt.com/"]
    assert result.to_payload()["driver_type"] == "FakeChromeDriver"


def test_open_opera_can_create_driver_without_navigation(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeChromeDriver(options=FakeChromeOptions())

    result = opera_controller.open_opera(config, driver_factory=lambda _config: driver, navigate=False)

    assert result.navigated is False
    assert driver.visited_urls == []


def test_llm_browser_open_help_includes_opera_and_no_auto_send(capsys) -> None:
    try:
        cli.main(["llm-browser", "open", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "{edge,opera}" in text
    assert "--profile-root" in text
    assert "--auto-send" not in text


def test_llm_browser_open_opera_uses_controller_without_real_browser(monkeypatch, tmp_path: Path, capsys) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    captured_configs: list[BrowserRunConfig] = []

    class Result:
        def to_payload(self) -> dict[str, object]:
            return {"browser": "opera", "chat_url": "https://chatgpt.com/", "navigated": True, "driver_type": "Fake"}

    def fake_open_opera(config: BrowserRunConfig) -> Result:
        captured_configs.append(config)
        return Result()

    monkeypatch.setattr(opera_controller, "open_opera", fake_open_opera)

    exit_code = cli.main(
        [
            "llm-browser",
            "open",
            "--browser",
            "opera",
            "--wrapper-root",
            str(tmp_path),
            "--download-dir",
            str(downloads),
            "--profile-root",
            str(tmp_path / "profiles"),
        ]
    )

    assert exit_code == 0
    assert captured_configs
    config = captured_configs[0]
    assert config.browser == "opera"
    assert config.profile_dir == tmp_path / "profiles" / "opera_chatgpt_default"
    assert config.profile_dir.exists()
    payload = json.loads(capsys.readouterr().out)
    assert payload["browser"] == "opera"
    assert payload["navigated"] is True
