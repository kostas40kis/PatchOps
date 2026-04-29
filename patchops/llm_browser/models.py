"""Stable models for the optional LLM browser runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .browser_paths import normalize_browser
from .browser_profiles import validate_profile_dir_override


@dataclass(frozen=True)
class BrowserRunConfig:
    """Validated configuration for one browser-runner session.

    The model is intentionally passive. Constructing it must not import
    Selenium, open a browser, start a driver, or create a network listener.
    """

    browser: str
    wrapper_root: Path
    target_root: Path | None
    download_dir: Path
    profile_dir: Path
    chat_url: str
    auto_download: bool
    auto_paste: bool
    auto_send: bool = False
    poll_seconds: int = 5
    stability_seconds: int = 15
    run_package_timeout_seconds: int = 1800

    def __post_init__(self) -> None:
        browser = normalize_browser(self.browser)
        wrapper_root = Path(self.wrapper_root)
        target_root = None if self.target_root is None else Path(self.target_root)
        download_dir = Path(self.download_dir)
        profile_dir = validate_profile_dir_override(Path(self.profile_dir), browser=browser)
        chat_url = self.chat_url.strip()

        if not wrapper_root.exists() or not wrapper_root.is_dir():
            raise ValueError(f"wrapper_root must be an existing directory: {wrapper_root}")

        if target_root is not None and (not target_root.exists() or not target_root.is_dir()):
            raise ValueError(f"target_root must be an existing directory when supplied: {target_root}")

        if not download_dir.exists() or not download_dir.is_dir():
            raise ValueError(f"download_dir must be an existing directory: {download_dir}")

        if not chat_url:
            raise ValueError("chat_url must not be empty")
        if not (chat_url.startswith("https://") or chat_url.startswith("http://")):
            raise ValueError("chat_url must start with http:// or https://")

        if type(self.auto_download) is not bool:
            raise ValueError("auto_download must be a bool")
        if type(self.auto_paste) is not bool:
            raise ValueError("auto_paste must be a bool")
        if type(self.auto_send) is not bool:
            raise ValueError("auto_send must be a bool")

        # This stream must not silently submit messages. A later explicit patch
        # can add a reviewed opt-in unlock if that ever becomes desirable.
        if self.auto_send:
            raise ValueError("auto_send cannot be enabled in BrowserRunConfig safety defaults")

        if int(self.poll_seconds) <= 0:
            raise ValueError("poll_seconds must be positive")
        if int(self.stability_seconds) <= 0:
            raise ValueError("stability_seconds must be positive")
        if int(self.run_package_timeout_seconds) <= 0:
            raise ValueError("run_package_timeout_seconds must be positive")

        object.__setattr__(self, "browser", browser)
        object.__setattr__(self, "wrapper_root", wrapper_root)
        object.__setattr__(self, "target_root", target_root)
        object.__setattr__(self, "download_dir", download_dir)
        object.__setattr__(self, "profile_dir", profile_dir)
        object.__setattr__(self, "chat_url", chat_url)
        object.__setattr__(self, "poll_seconds", int(self.poll_seconds))
        object.__setattr__(self, "stability_seconds", int(self.stability_seconds))
        object.__setattr__(self, "run_package_timeout_seconds", int(self.run_package_timeout_seconds))

    def to_payload(self) -> dict[str, Any]:
        return {
            "browser": self.browser,
            "wrapper_root": str(self.wrapper_root),
            "target_root": None if self.target_root is None else str(self.target_root),
            "download_dir": str(self.download_dir),
            "profile_dir": str(self.profile_dir),
            "chat_url": self.chat_url,
            "auto_download": self.auto_download,
            "auto_paste": self.auto_paste,
            "auto_send": self.auto_send,
            "poll_seconds": self.poll_seconds,
            "stability_seconds": self.stability_seconds,
            "run_package_timeout_seconds": self.run_package_timeout_seconds,
        }
