"""Opera controller for the optional LLM browser runner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .browser_factory import create_opera_driver
from .models import BrowserRunConfig


DriverFactory = Callable[[BrowserRunConfig], Any]


@dataclass(frozen=True)
class OperaOpenResult:
    browser: str
    chat_url: str
    navigated: bool
    driver: Any

    def to_payload(self) -> dict[str, object]:
        return {
            "browser": self.browser,
            "chat_url": self.chat_url,
            "navigated": self.navigated,
            "driver_type": type(self.driver).__name__,
        }


def open_opera(
    config: BrowserRunConfig,
    *,
    driver_factory: DriverFactory | None = None,
    navigate: bool = True,
) -> OperaOpenResult:
    """Open Opera for a validated config and optionally navigate to chat_url.

    This function starts a browser only when driver_factory creates a real
    Selenium driver. Unit tests inject a fake factory.
    """

    if config.browser != "opera":
        raise ValueError(f"open_opera only supports opera, got: {config.browser}")

    factory = driver_factory or create_opera_driver
    driver = factory(config)

    navigated = False
    if navigate:
        driver.get(config.chat_url)
        navigated = True

    return OperaOpenResult(
        browser="opera",
        chat_url=config.chat_url,
        navigated=navigated,
        driver=driver,
    )
