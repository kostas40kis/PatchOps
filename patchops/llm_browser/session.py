"""Browser session lifecycle helpers for the optional LLM browser runner.

This module owns lifecycle semantics around an already configured browser run:
start, optional navigation, close, idempotent shutdown, and context-manager use.

It remains safe to import and unit-test:
- importing this module does not import Selenium,
- tests can inject fake driver factories,
- a real browser starts only when default factories are used at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .browser_factory import create_edge_driver, create_opera_driver
from .models import BrowserRunConfig


DriverFactory = Callable[[BrowserRunConfig], Any]


class BrowserSessionError(RuntimeError):
    """Raised when the browser session lifecycle is used incorrectly."""


@dataclass
class BrowserSession:
    config: BrowserRunConfig
    driver_factory: DriverFactory | None = None
    navigate_on_start: bool = True
    driver: Any | None = field(default=None, init=False)
    started: bool = field(default=False, init=False)
    navigated: bool = field(default=False, init=False)
    closed: bool = field(default=False, init=False)

    def _default_factory(self) -> DriverFactory:
        if self.config.browser == "edge":
            return create_edge_driver
        if self.config.browser == "opera":
            return create_opera_driver
        raise BrowserSessionError(f"unsupported browser: {self.config.browser}")

    def start(self) -> "BrowserSession":
        """Create the browser driver and optionally navigate to chat_url.

        Calling start twice is a lifecycle error. This avoids accidentally
        spawning multiple browser instances from one session object.
        """

        if self.started and not self.closed:
            raise BrowserSessionError("browser session is already started")
        if self.closed:
            raise BrowserSessionError("browser session is already closed")

        factory = self.driver_factory or self._default_factory()
        self.driver = factory(self.config)
        self.started = True

        if self.navigate_on_start:
            self.navigate(self.config.chat_url)

        return self

    def navigate(self, url: str) -> None:
        if not self.started or self.driver is None:
            raise BrowserSessionError("browser session is not started")
        if self.closed:
            raise BrowserSessionError("browser session is closed")
        self.driver.get(url)
        self.navigated = True

    def close(self) -> None:
        """Close the browser session.

        Shutdown is idempotent. Selenium drivers usually expose quit(), but this
        also supports close() for simple fakes or alternate drivers.
        """

        if self.closed:
            return

        driver = self.driver
        if driver is not None:
            quit_method = getattr(driver, "quit", None)
            close_method = getattr(driver, "close", None)
            if callable(quit_method):
                quit_method()
            elif callable(close_method):
                close_method()

        self.closed = True

    def __enter__(self) -> "BrowserSession":
        return self.start()

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self.close()
        return False

    def to_payload(self) -> dict[str, object]:
        return {
            "browser": self.config.browser,
            "chat_url": self.config.chat_url,
            "started": self.started,
            "navigated": self.navigated,
            "closed": self.closed,
            "driver_type": None if self.driver is None else type(self.driver).__name__,
        }
