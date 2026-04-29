from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

from patchops import cli
from patchops.llm_browser import edge_controller
from patchops.llm_browser.browser_factory import (
    BrowserFactoryError,
    build_edge_options,
    create_edge_driver,
)
from patchops.llm_browser.models import BrowserRunConfig


class FakeEdgeOptions:
    def __init__(self) -> None:
        self.arguments: list[str] = []
        self.experimental_options: dict[str, object] = {}
        self.binary_location: str | None = None

    def add_argument(self, value: str) -> None:
        self.arguments.append(value)

    def add_experimental_option(self, name: str, value: object) -> None:
        self.experimental_options[name] = value


class FakeEdgeDriver:
    created_with_options: FakeEdgeOptions | None = None

    def __init__(self, *, options: FakeEdgeOptions) -> None:
        self.options = options
        self.visited_urls: list[str] = []
        FakeEdgeDriver.created_with_options = options

    def get(self, url: str) -> None:
        self.visited_urls.append(url)


def _config(tmp_path: Path) -> BrowserRunConfig:
    downloads = tmp_path / "Downloads"
    downloads.mkdir(exist_ok=True)
    return BrowserRunConfig(
        browser="edge",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=tmp_path / "edge_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=False,
        auto_paste=False,
    )


def test_browser_factory_import_does_not_import_selenium() -> None:
    sys.modules.pop("patchops.llm_browser.browser_factory", None)
    before = set(sys.modules)

    module = importlib.import_module("patchops.llm_browser.browser_factory")

    loaded = set(sys.modules) - before
    assert "selenium" not in loaded
    assert hasattr(module, "create_edge_driver")


def test_build_edge_options_sets_profile_downloads_and_notifications(tmp_path: Path) -> None:
    config = _config(tmp_path)
    edge_path = tmp_path / "msedge.exe"

    options = build_edge_options(config, edge_executable_path=edge_path, options_cls=FakeEdgeOptions)

    assert options.binary_location == str(edge_path)
    assert f"--user-data-dir={config.profile_dir}" in options.arguments
    assert "--disable-notifications" in options.arguments
    prefs = options.experimental_options["prefs"]
    assert isinstance(prefs, dict)
    assert prefs["download.default_directory"] == str(config.download_dir)
    assert prefs["download.prompt_for_download"] is False
    assert prefs["download.directory_upgrade"] is True


def test_build_edge_options_rejects_non_edge_config(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    config = BrowserRunConfig(
        browser="opera",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=tmp_path / "opera_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=False,
        auto_paste=False,
    )

    with pytest.raises(BrowserFactoryError, match="only supports edge"):
        build_edge_options(config, options_cls=FakeEdgeOptions)


def test_create_edge_driver_uses_path_discovery_and_injected_driver(tmp_path: Path) -> None:
    config = _config(tmp_path)
    edge_exe = tmp_path / "msedge.exe"
    edge_exe.write_text("", encoding="utf-8")

    driver = create_edge_driver(
        config,
        edge_cls=FakeEdgeDriver,
        options_cls=FakeEdgeOptions,
        exists=lambda path: path == edge_exe,
        environ={"PATCHOPS_EDGE_PATH": str(edge_exe)},
    )

    assert isinstance(driver, FakeEdgeDriver)
    assert driver.options.binary_location == str(edge_exe)
    assert f"--user-data-dir={config.profile_dir}" in driver.options.arguments


def test_create_edge_driver_returns_clear_missing_edge_error(tmp_path: Path) -> None:
    config = _config(tmp_path)

    with pytest.raises(FileNotFoundError, match="edge executable was not found"):
        create_edge_driver(
            config,
            edge_cls=FakeEdgeDriver,
            options_cls=FakeEdgeOptions,
            exists=lambda _path: False,
            environ={},
        )


def test_open_edge_navigates_to_chat_url_with_fake_driver(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeEdgeDriver(options=FakeEdgeOptions())

    result = edge_controller.open_edge(config, driver_factory=lambda _config: driver)

    assert result.browser == "edge"
    assert result.navigated is True
    assert driver.visited_urls == ["https://chatgpt.com/"]
    assert result.to_payload()["driver_type"] == "FakeEdgeDriver"


def test_open_edge_can_create_driver_without_navigation(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeEdgeDriver(options=FakeEdgeOptions())

    result = edge_controller.open_edge(config, driver_factory=lambda _config: driver, navigate=False)

    assert result.navigated is False
    assert driver.visited_urls == []


def test_llm_browser_open_help_is_registered(capsys) -> None:
    try:
        cli.main(["llm-browser", "open", "--help"])
    except SystemExit as exc:
        assert exc.code == 0

    captured = capsys.readouterr()
    text = captured.out + captured.err
    assert "--browser" in text
    assert "--wrapper-root" in text
    assert "--download-dir" in text
    assert "--profile-root" in text
    assert "--auto-send" not in text


def test_llm_browser_open_edge_uses_controller_without_real_browser(monkeypatch, tmp_path: Path, capsys) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    captured_configs: list[BrowserRunConfig] = []

    class Result:
        def to_payload(self) -> dict[str, object]:
            return {"browser": "edge", "chat_url": "https://chatgpt.com/", "navigated": True, "driver_type": "Fake"}

    def fake_open_edge(config: BrowserRunConfig) -> Result:
        captured_configs.append(config)
        return Result()

    monkeypatch.setattr(edge_controller, "open_edge", fake_open_edge)

    exit_code = cli.main(
        [
            "llm-browser",
            "open",
            "--browser",
            "edge",
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
    assert config.browser == "edge"
    assert config.profile_dir == tmp_path / "profiles" / "edge_chatgpt_default"
    assert config.profile_dir.exists()
    payload = json.loads(capsys.readouterr().out)
    assert payload["browser"] == "edge"
    assert payload["navigated"] is True
