from __future__ import annotations

from pathlib import Path

import pytest

from patchops.llm_browser.models import BrowserRunConfig
from patchops.llm_browser.session import BrowserSession, BrowserSessionError


class FakeDriver:
    def __init__(self) -> None:
        self.visited_urls: list[str] = []
        self.quit_calls = 0
        self.close_calls = 0

    def get(self, url: str) -> None:
        self.visited_urls.append(url)

    def quit(self) -> None:
        self.quit_calls += 1

    def close(self) -> None:
        self.close_calls += 1


class CloseOnlyDriver:
    def __init__(self) -> None:
        self.visited_urls: list[str] = []
        self.close_calls = 0

    def get(self, url: str) -> None:
        self.visited_urls.append(url)

    def close(self) -> None:
        self.close_calls += 1


def _config(tmp_path: Path, *, browser: str = "edge") -> BrowserRunConfig:
    downloads = tmp_path / "Downloads"
    downloads.mkdir(exist_ok=True)
    return BrowserRunConfig(
        browser=browser,
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=tmp_path / f"{browser}_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=False,
        auto_paste=False,
    )


def test_session_import_and_construction_do_not_start_driver(tmp_path: Path) -> None:
    config = _config(tmp_path)
    calls: list[BrowserRunConfig] = []

    session = BrowserSession(config, driver_factory=lambda cfg: calls.append(cfg) or FakeDriver())

    assert calls == []
    assert session.driver is None
    assert session.started is False
    assert session.closed is False


def test_session_start_creates_driver_and_navigates(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver).start()

    assert session.driver is driver
    assert session.started is True
    assert session.navigated is True
    assert driver.visited_urls == ["https://chatgpt.com/"]


def test_session_can_start_without_navigation_then_navigate_manually(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver, navigate_on_start=False).start()

    assert session.started is True
    assert session.navigated is False
    assert driver.visited_urls == []

    session.navigate("https://chatgpt.com/g/g-test")
    assert session.navigated is True
    assert driver.visited_urls == ["https://chatgpt.com/g/g-test"]


def test_session_close_calls_quit_once_and_is_idempotent(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver).start()
    session.close()
    session.close()

    assert session.closed is True
    assert driver.quit_calls == 1
    assert driver.close_calls == 0


def test_session_close_falls_back_to_close_when_quit_missing(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = CloseOnlyDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver).start()
    session.close()

    assert session.closed is True
    assert driver.close_calls == 1


def test_session_context_manager_closes_on_exit(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    with BrowserSession(config, driver_factory=lambda _cfg: driver) as session:
        assert session.started is True
        assert session.closed is False
        assert driver.visited_urls == ["https://chatgpt.com/"]

    assert session.closed is True
    assert driver.quit_calls == 1


def test_session_context_manager_closes_on_exception(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    with pytest.raises(RuntimeError, match="boom"):
        with BrowserSession(config, driver_factory=lambda _cfg: driver):
            raise RuntimeError("boom")

    assert driver.quit_calls == 1


def test_session_start_twice_is_rejected(tmp_path: Path) -> None:
    config = _config(tmp_path)
    session = BrowserSession(config, driver_factory=lambda _cfg: FakeDriver()).start()

    with pytest.raises(BrowserSessionError, match="already started"):
        session.start()


def test_session_cannot_start_after_close(tmp_path: Path) -> None:
    config = _config(tmp_path)
    session = BrowserSession(config, driver_factory=lambda _cfg: FakeDriver()).start()
    session.close()

    with pytest.raises(BrowserSessionError, match="already closed"):
        session.start()


def test_session_cannot_navigate_before_start(tmp_path: Path) -> None:
    config = _config(tmp_path)
    session = BrowserSession(config, driver_factory=lambda _cfg: FakeDriver())

    with pytest.raises(BrowserSessionError, match="not started"):
        session.navigate("https://chatgpt.com/")


def test_session_cannot_navigate_after_close(tmp_path: Path) -> None:
    config = _config(tmp_path)
    session = BrowserSession(config, driver_factory=lambda _cfg: FakeDriver()).start()
    session.close()

    with pytest.raises(BrowserSessionError, match="closed"):
        session.navigate("https://chatgpt.com/")


def test_session_payload_is_stable(tmp_path: Path) -> None:
    config = _config(tmp_path)
    driver = FakeDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver).start()
    payload = session.to_payload()

    assert payload["browser"] == "edge"
    assert payload["chat_url"] == "https://chatgpt.com/"
    assert payload["started"] is True
    assert payload["navigated"] is True
    assert payload["closed"] is False
    assert payload["driver_type"] == "FakeDriver"


def test_session_supports_opera_with_injected_factory(tmp_path: Path) -> None:
    config = _config(tmp_path, browser="opera")
    driver = FakeDriver()

    session = BrowserSession(config, driver_factory=lambda _cfg: driver).start()

    assert session.config.browser == "opera"
    assert session.started is True
    assert driver.visited_urls == ["https://chatgpt.com/"]
