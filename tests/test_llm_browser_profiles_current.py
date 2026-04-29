from __future__ import annotations

from pathlib import Path

import pytest

from patchops.llm_browser.browser_profiles import (
    DEFAULT_PROFILE_NAME,
    PROFILE_ROOT_ENV_VAR,
    default_profile_root,
    ensure_browser_profile_dir,
    is_probably_default_browser_profile,
    profile_dir_for_browser,
    resolve_browser_profile,
    validate_profile_dir_override,
    validate_profile_name,
    validate_profile_root,
)


def test_default_profile_root_uses_localappdata(tmp_path: Path) -> None:
    root = default_profile_root({"LOCALAPPDATA": str(tmp_path)})

    assert root == tmp_path / "PatchOps" / "llm_browser_profiles"


def test_default_profile_root_honors_explicit_environment_override(tmp_path: Path) -> None:
    override = tmp_path / "custom_profiles"

    root = default_profile_root({PROFILE_ROOT_ENV_VAR: str(override), "LOCALAPPDATA": str(tmp_path / "ignored")})

    assert root == override


def test_default_profile_names_are_dedicated_per_browser(tmp_path: Path) -> None:
    edge_dir = profile_dir_for_browser("edge", profile_root=tmp_path)
    opera_dir = profile_dir_for_browser("opera", profile_root=tmp_path)

    assert edge_dir == tmp_path / f"edge_{DEFAULT_PROFILE_NAME}"
    assert opera_dir == tmp_path / f"opera_{DEFAULT_PROFILE_NAME}"


def test_profile_manager_creates_directory_and_reports_created(tmp_path: Path) -> None:
    result = resolve_browser_profile("edge", profile_root=tmp_path, create=True)

    assert result.profile_dir.exists()
    assert result.profile_dir.is_dir()
    assert result.created is True
    assert result.source == "dedicated_default"
    assert result.profile_root == tmp_path

    second = resolve_browser_profile("edge", profile_root=tmp_path, create=True)
    assert second.created is False


def test_ensure_browser_profile_dir_returns_created_path(tmp_path: Path) -> None:
    profile_dir = ensure_browser_profile_dir("opera", profile_root=tmp_path)

    assert profile_dir == tmp_path / f"opera_{DEFAULT_PROFILE_NAME}"
    assert profile_dir.exists()


def test_explicit_profile_dir_override_is_allowed_when_safe(tmp_path: Path) -> None:
    override = tmp_path / "my_edge_automation_profile"

    result = resolve_browser_profile("edge", profile_dir=override, create=True)

    assert result.profile_dir == override
    assert result.profile_root is None
    assert result.source == "override"
    assert override.exists()


@pytest.mark.parametrize(
    "bad_name",
    ["", ".", "..", "../Default", r"..\Default", "nested/name", r"nested\name", "bad:name"],
)
def test_profile_name_rejects_path_traversal_and_invalid_segments(bad_name: str) -> None:
    with pytest.raises(ValueError):
        validate_profile_name(bad_name)


def test_profile_root_rejects_parent_traversal() -> None:
    with pytest.raises(ValueError, match="profile_root"):
        validate_profile_root(Path("..") / "profiles")


def test_profile_dir_override_rejects_parent_traversal() -> None:
    with pytest.raises(ValueError, match="profile_dir"):
        validate_profile_dir_override(Path("..") / "profile", browser="edge")


def test_profile_dir_override_rejects_default_edge_profile() -> None:
    default_edge_profile = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"

    with pytest.raises(ValueError, match="default browser profile"):
        validate_profile_dir_override(default_edge_profile, browser="edge")


def test_profile_dir_override_rejects_default_opera_profile() -> None:
    default_opera_profile = r"C:\Users\kostas\AppData\Roaming\Opera Software\Opera Stable"

    with pytest.raises(ValueError, match="default browser profile"):
        validate_profile_dir_override(default_opera_profile, browser="opera")


def test_default_profile_detection_is_browser_specific() -> None:
    edge_default = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
    opera_default = r"C:\Users\kostas\AppData\Roaming\Opera Software\Opera Stable"

    assert is_probably_default_browser_profile(edge_default, browser="edge") is True
    assert is_probably_default_browser_profile(edge_default, browser="opera") is False
    assert is_probably_default_browser_profile(opera_default, browser="opera") is True
    assert is_probably_default_browser_profile(opera_default, browser="edge") is False


def test_resolve_profile_without_create_does_not_touch_filesystem(tmp_path: Path) -> None:
    result = resolve_browser_profile("edge", profile_root=tmp_path, create=False)

    assert result.profile_dir == tmp_path / f"edge_{DEFAULT_PROFILE_NAME}"
    assert result.profile_dir.exists() is False
    assert result.created is False


def test_profile_result_payload_is_stable(tmp_path: Path) -> None:
    result = resolve_browser_profile("edge", profile_root=tmp_path, create=False)

    payload = result.to_payload()

    assert payload["browser"] == "edge"
    assert payload["profile_name"] == DEFAULT_PROFILE_NAME
    assert payload["source"] == "dedicated_default"
    assert payload["created"] is False
    assert str(tmp_path) in payload["profile_dir"]
