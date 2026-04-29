"""Selenium browser factory helpers for the optional LLM browser runner.

The module is lazy by design:
- importing this module does not import Selenium,
- building options with injected test doubles does not import Selenium,
- a real Selenium driver is created only when create_*_driver() is called
  without injected driver classes.

D0.6 implemented Edge. D0.7 adds Opera via Chromium/Chrome options with
Opera's binary location.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from .browser_paths import require_browser_path
from .models import BrowserRunConfig


class BrowserFactoryError(RuntimeError):
    """Raised when a browser driver cannot be prepared."""


class SeleniumDependencyError(BrowserFactoryError):
    """Raised when Selenium is needed but not installed."""


def _load_edge_selenium() -> tuple[type[Any], type[Any]]:
    try:
        from selenium import webdriver  # type: ignore[import-not-found]
        from selenium.webdriver.edge.options import Options as EdgeOptions  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise SeleniumDependencyError(
            'Selenium is not installed. Install the optional browser extra with: '
            'python -m pip install -e ".[browser]"'
        ) from exc

    return webdriver.Edge, EdgeOptions


def _load_chromium_selenium_for_opera() -> tuple[type[Any], type[Any]]:
    try:
        from selenium import webdriver  # type: ignore[import-not-found]
        from selenium.webdriver.chrome.options import Options as ChromeOptions  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        raise SeleniumDependencyError(
            'Selenium is not installed. Install the optional browser extra with: '
            'python -m pip install -e ".[browser]"'
        ) from exc

    return webdriver.Chrome, ChromeOptions


def _add_common_chromium_options(options: Any, config: BrowserRunConfig, binary_path: str | Path | None) -> Any:
    if binary_path is not None:
        options.binary_location = str(binary_path)

    options.add_argument(f"--user-data-dir={config.profile_dir}")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-popup-blocking")

    prefs = {
        "download.default_directory": str(config.download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    return options


def build_edge_options(
    config: BrowserRunConfig,
    *,
    edge_executable_path: str | Path | None = None,
    options_cls: type[Any] | None = None,
) -> Any:
    """Build Edge Selenium options for a validated BrowserRunConfig.

    This is safe to unit-test with a fake options class. It does not start a
    browser and does not create a driver.
    """

    if config.browser != "edge":
        raise BrowserFactoryError(f"build_edge_options only supports edge, got: {config.browser}")

    if options_cls is None:
        _edge_cls, options_cls = _load_edge_selenium()

    return _add_common_chromium_options(options_cls(), config, edge_executable_path)


def build_opera_options(
    config: BrowserRunConfig,
    *,
    opera_executable_path: str | Path | None = None,
    options_cls: type[Any] | None = None,
) -> Any:
    """Build Opera Selenium options for a validated BrowserRunConfig.

    Opera is Chromium-based, so Selenium's Chrome options/driver surface is
    used with Opera's binary_location. This function does not start a browser.
    """

    if config.browser != "opera":
        raise BrowserFactoryError(f"build_opera_options only supports opera, got: {config.browser}")

    if options_cls is None:
        _chrome_cls, options_cls = _load_chromium_selenium_for_opera()

    return _add_common_chromium_options(options_cls(), config, opera_executable_path)


def create_edge_driver(
    config: BrowserRunConfig,
    *,
    edge_cls: type[Any] | None = None,
    options_cls: type[Any] | None = None,
    exists: Callable[[Path], bool] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Any:
    """Create a Selenium Edge driver for the supplied config.

    Real browser startup occurs only here, and only when a real Edge class is
    used. Tests pass injected fake classes so no browser opens.
    """

    if config.browser != "edge":
        raise BrowserFactoryError(f"create_edge_driver only supports edge, got: {config.browser}")

    path_exists = Path.exists if exists is None else exists
    edge_path = require_browser_path("edge", environ=environ, exists=path_exists)

    if edge_cls is None or options_cls is None:
        loaded_edge_cls, loaded_options_cls = _load_edge_selenium()
        if edge_cls is None:
            edge_cls = loaded_edge_cls
        if options_cls is None:
            options_cls = loaded_options_cls

    options = build_edge_options(
        config,
        edge_executable_path=edge_path,
        options_cls=options_cls,
    )

    return edge_cls(options=options)


def create_opera_driver(
    config: BrowserRunConfig,
    *,
    chrome_cls: type[Any] | None = None,
    options_cls: type[Any] | None = None,
    exists: Callable[[Path], bool] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Any:
    """Create a Selenium-backed Opera driver for the supplied config.

    Real browser startup occurs only here, and only when a real Chrome class is
    used. Tests pass injected fake classes so no browser opens.
    """

    if config.browser != "opera":
        raise BrowserFactoryError(f"create_opera_driver only supports opera, got: {config.browser}")

    path_exists = Path.exists if exists is None else exists
    opera_path = require_browser_path("opera", environ=environ, exists=path_exists)

    if chrome_cls is None or options_cls is None:
        loaded_chrome_cls, loaded_options_cls = _load_chromium_selenium_for_opera()
        if chrome_cls is None:
            chrome_cls = loaded_chrome_cls
        if options_cls is None:
            options_cls = loaded_options_cls

    options = build_opera_options(
        config,
        opera_executable_path=opera_path,
        options_cls=options_cls,
    )

    return chrome_cls(options=options)
