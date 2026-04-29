from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from patchops.llm_browser.config import DEFAULT_CHAT_URL, build_browser_run_config
from patchops.llm_browser.models import BrowserRunConfig


def _profile(tmp_path: Path) -> Path:
    return tmp_path / "edge_chatgpt_default"


def test_browser_run_config_defaults_are_safe(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    profile = _profile(tmp_path)

    config = BrowserRunConfig(
        browser="EDGE",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=profile,
        chat_url=DEFAULT_CHAT_URL,
        auto_download=False,
        auto_paste=False,
    )

    assert config.browser == "edge"
    assert config.wrapper_root == tmp_path
    assert config.target_root is None
    assert config.download_dir == downloads
    assert config.profile_dir == profile
    assert config.auto_send is False
    assert config.poll_seconds == 5
    assert config.stability_seconds == 15
    assert config.run_package_timeout_seconds == 1800


def test_browser_run_config_rejects_auto_send_true(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="auto_send cannot be enabled"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path,
            target_root=None,
            download_dir=downloads,
            profile_dir=_profile(tmp_path),
            chat_url=DEFAULT_CHAT_URL,
            auto_download=True,
            auto_paste=True,
            auto_send=True,
        )


def test_browser_run_config_requires_existing_wrapper_root(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="wrapper_root"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path / "missing",
            target_root=None,
            download_dir=downloads,
            profile_dir=_profile(tmp_path),
            chat_url=DEFAULT_CHAT_URL,
            auto_download=False,
            auto_paste=False,
        )


def test_browser_run_config_requires_existing_target_root_when_supplied(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="target_root"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path,
            target_root=tmp_path / "missing-target",
            download_dir=downloads,
            profile_dir=_profile(tmp_path),
            chat_url=DEFAULT_CHAT_URL,
            auto_download=False,
            auto_paste=False,
        )


def test_browser_run_config_requires_existing_download_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="download_dir"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path,
            target_root=None,
            download_dir=tmp_path / "missing-downloads",
            profile_dir=_profile(tmp_path),
            chat_url=DEFAULT_CHAT_URL,
            auto_download=False,
            auto_paste=False,
        )


@pytest.mark.parametrize("bad_url", ["", "chatgpt.com", "ftp://chatgpt.com"])
def test_browser_run_config_rejects_bad_chat_url(tmp_path: Path, bad_url: str) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="chat_url"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path,
            target_root=None,
            download_dir=downloads,
            profile_dir=_profile(tmp_path),
            chat_url=bad_url,
            auto_download=False,
            auto_paste=False,
        )


@pytest.mark.parametrize(
    "field_name, value",
    [
        ("poll_seconds", 0),
        ("stability_seconds", 0),
        ("run_package_timeout_seconds", 0),
    ],
)
def test_browser_run_config_rejects_nonpositive_timing_values(tmp_path: Path, field_name: str, value: int) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    kwargs = {
        "browser": "edge",
        "wrapper_root": tmp_path,
        "target_root": None,
        "download_dir": downloads,
        "profile_dir": _profile(tmp_path),
        "chat_url": DEFAULT_CHAT_URL,
        "auto_download": False,
        "auto_paste": False,
        field_name: value,
    }

    with pytest.raises(ValueError, match=field_name):
        BrowserRunConfig(**kwargs)


def test_browser_run_config_rejects_default_browser_profile(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="default browser profile"):
        BrowserRunConfig(
            browser="edge",
            wrapper_root=tmp_path,
            target_root=None,
            download_dir=downloads,
            profile_dir=r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default",
            chat_url=DEFAULT_CHAT_URL,
            auto_download=False,
            auto_paste=False,
        )


def test_browser_run_config_payload_uses_stable_string_paths(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    target = tmp_path / "target"
    downloads.mkdir()
    target.mkdir()

    config = BrowserRunConfig(
        browser="opera",
        wrapper_root=tmp_path,
        target_root=target,
        download_dir=downloads,
        profile_dir=tmp_path / "opera_chatgpt_default",
        chat_url="https://chatgpt.com/",
        auto_download=True,
        auto_paste=False,
    )

    payload = config.to_payload()

    assert payload["browser"] == "opera"
    assert payload["wrapper_root"] == str(tmp_path)
    assert payload["target_root"] == str(target)
    assert payload["download_dir"] == str(downloads)
    assert payload["profile_dir"] == str(tmp_path / "opera_chatgpt_default")
    assert payload["auto_send"] is False


def test_browser_run_config_is_frozen(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    config = BrowserRunConfig(
        browser="edge",
        wrapper_root=tmp_path,
        target_root=None,
        download_dir=downloads,
        profile_dir=_profile(tmp_path),
        chat_url=DEFAULT_CHAT_URL,
        auto_download=False,
        auto_paste=False,
    )

    with pytest.raises(FrozenInstanceError):
        config.auto_send = True  # type: ignore[misc]


def test_build_browser_run_config_uses_dedicated_profile_and_defaults(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    config = build_browser_run_config(
        browser="edge",
        wrapper_root=tmp_path,
        download_dir=downloads,
        profile_root=tmp_path / "profiles",
        auto_download=True,
        auto_paste=True,
    )

    assert config.browser == "edge"
    assert config.profile_dir == tmp_path / "profiles" / "edge_chatgpt_default"
    assert config.profile_dir.exists() is False
    assert config.auto_download is True
    assert config.auto_paste is True
    assert config.auto_send is False


def test_build_browser_run_config_can_create_profile_dir_when_requested(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    config = build_browser_run_config(
        browser="opera",
        wrapper_root=tmp_path,
        download_dir=downloads,
        profile_root=tmp_path / "profiles",
        create_profile_dir=True,
    )

    assert config.profile_dir == tmp_path / "profiles" / "opera_chatgpt_default"
    assert config.profile_dir.exists()


def test_build_browser_run_config_rejects_auto_send_true(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()

    with pytest.raises(ValueError, match="auto_send cannot be enabled"):
        build_browser_run_config(
            browser="edge",
            wrapper_root=tmp_path,
            download_dir=downloads,
            profile_root=tmp_path / "profiles",
            auto_send=True,
        )


def test_build_browser_run_config_honors_environment_profile_root(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    profile_root = tmp_path / "env_profiles"
    downloads.mkdir()

    config = build_browser_run_config(
        browser="edge",
        wrapper_root=tmp_path,
        download_dir=downloads,
        environ={"PATCHOPS_LLM_BROWSER_PROFILE_ROOT": str(profile_root)},
    )

    assert config.profile_dir == profile_root / "edge_chatgpt_default"
