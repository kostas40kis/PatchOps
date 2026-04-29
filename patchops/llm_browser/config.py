"""Config construction helpers for the optional LLM browser runner."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .browser_profiles import DEFAULT_PROFILE_NAME, resolve_browser_profile
from .models import BrowserRunConfig


DEFAULT_CHAT_URL = "https://chatgpt.com/"


def default_download_dir() -> Path:
    return Path.home() / "Downloads"


def build_browser_run_config(
    *,
    browser: str = "edge",
    wrapper_root: str | Path,
    target_root: str | Path | None = None,
    download_dir: str | Path | None = None,
    profile_dir: str | Path | None = None,
    profile_root: str | Path | None = None,
    profile_name: str = DEFAULT_PROFILE_NAME,
    chat_url: str = DEFAULT_CHAT_URL,
    auto_download: bool = False,
    auto_paste: bool = False,
    auto_send: bool = False,
    poll_seconds: int = 5,
    stability_seconds: int = 15,
    run_package_timeout_seconds: int = 1800,
    create_profile_dir: bool = False,
    environ: Mapping[str, str] | None = None,
) -> BrowserRunConfig:
    """Build a validated browser-runner config.

    Construction is passive. It may create the dedicated profile directory only
    when create_profile_dir=True, and it never opens a browser or starts a
    Selenium driver.
    """

    resolved_download_dir = Path(download_dir).expanduser() if download_dir is not None else default_download_dir()

    resolved_profile = resolve_browser_profile(
        browser,
        profile_name=profile_name,
        profile_root=profile_root,
        profile_dir=profile_dir,
        environ=environ,
        create=create_profile_dir,
    )

    return BrowserRunConfig(
        browser=browser,
        wrapper_root=Path(wrapper_root).expanduser(),
        target_root=None if target_root is None else Path(target_root).expanduser(),
        download_dir=resolved_download_dir,
        profile_dir=resolved_profile.profile_dir,
        chat_url=chat_url,
        auto_download=auto_download,
        auto_paste=auto_paste,
        auto_send=auto_send,
        poll_seconds=poll_seconds,
        stability_seconds=stability_seconds,
        run_package_timeout_seconds=run_package_timeout_seconds,
    )
