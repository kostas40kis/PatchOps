"""Dedicated browser profile directory management for the LLM browser runner.

This module is pure Python and passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it opens no browser window,
- it creates no network listener.

The browser runner must not use the operator's normal browser profile by
default. These helpers create and validate dedicated PatchOps automation
profile directories instead.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Mapping

from .browser_paths import normalize_browser


DEFAULT_PROFILE_NAME = "chatgpt_default"
PROFILE_ROOT_ENV_VAR = "PATCHOPS_LLM_BROWSER_PROFILE_ROOT"
PROFILE_ROOT_PARTS: tuple[str, ...] = ("PatchOps", "llm_browser_profiles")


@dataclass(frozen=True)
class BrowserProfileResult:
    browser: str
    profile_dir: Path
    profile_root: Path | None
    profile_name: str
    source: str
    created: bool
    message: str

    def to_payload(self) -> dict[str, object]:
        return {
            "browser": self.browser,
            "profile_dir": str(self.profile_dir),
            "profile_root": None if self.profile_root is None else str(self.profile_root),
            "profile_name": self.profile_name,
            "source": self.source,
            "created": self.created,
            "message": self.message,
        }


def _has_parent_traversal(path: Path) -> bool:
    return any(part == ".." for part in path.parts)


def validate_profile_name(profile_name: str = DEFAULT_PROFILE_NAME) -> str:
    name = (profile_name or "").strip()
    if not name:
        raise ValueError("profile_name must not be empty")
    if name in {".", ".."}:
        raise ValueError("profile_name must not be a traversal segment")
    if "/" in name or "\\" in name:
        raise ValueError("profile_name must be a single path segment")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("profile_name may only contain letters, numbers, underscore, dash, and dot")
    return name


def default_profile_root(environ: Mapping[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ

    override = env.get(PROFILE_ROOT_ENV_VAR)
    if override:
        root = Path(override)
    else:
        local_app_data = env.get("LOCALAPPDATA")
        if local_app_data:
            root = Path(local_app_data)
        else:
            root = Path.home() / "AppData" / "Local"
        for part in PROFILE_ROOT_PARTS:
            root = root / part

    validate_profile_root(root)
    return root


def validate_profile_root(profile_root: str | Path) -> Path:
    root = Path(profile_root)
    if _has_parent_traversal(root):
        raise ValueError("profile_root must not contain parent traversal")
    return root


def _normalized_path_text(path: str | Path) -> str:
    return str(path).replace("\\", "/").lower().rstrip("/")


def is_probably_default_browser_profile(
    profile_dir: str | Path,
    *,
    browser: str,
) -> bool:
    normalized_browser = normalize_browser(browser)
    text = _normalized_path_text(profile_dir)

    if normalized_browser == "edge":
        return (
            "/microsoft/edge/user data/default" in text
            or text.endswith("/microsoft/edge/user data")
        )

    return (
        "/opera software/opera stable" in text
        or "/opera software/opera gx stable" in text
        or text.endswith("/opera stable")
        or text.endswith("/opera gx stable")
    )


def validate_profile_dir_override(
    profile_dir: str | Path,
    *,
    browser: str,
) -> Path:
    path = Path(profile_dir)
    if _has_parent_traversal(path):
        raise ValueError("profile_dir must not contain parent traversal")
    if is_probably_default_browser_profile(path, browser=browser):
        raise ValueError("profile_dir must not point at a normal/default browser profile")
    return path


def profile_dir_for_browser(
    browser: str,
    *,
    profile_name: str = DEFAULT_PROFILE_NAME,
    profile_root: str | Path | None = None,
    profile_dir: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    normalized_browser = normalize_browser(browser)

    if profile_dir is not None:
        return validate_profile_dir_override(profile_dir, browser=normalized_browser)

    safe_name = validate_profile_name(profile_name)
    root = validate_profile_root(profile_root) if profile_root is not None else default_profile_root(environ)
    return root / f"{normalized_browser}_{safe_name}"


def resolve_browser_profile(
    browser: str,
    *,
    profile_name: str = DEFAULT_PROFILE_NAME,
    profile_root: str | Path | None = None,
    profile_dir: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    create: bool = True,
) -> BrowserProfileResult:
    normalized_browser = normalize_browser(browser)
    resolved_profile_dir = profile_dir_for_browser(
        normalized_browser,
        profile_name=profile_name,
        profile_root=profile_root,
        profile_dir=profile_dir,
        environ=environ,
    )

    existed_before = resolved_profile_dir.exists()
    if create:
        resolved_profile_dir.mkdir(parents=True, exist_ok=True)

    if profile_dir is not None:
        source = "override"
        resolved_root = None
        safe_name = resolved_profile_dir.name
    else:
        source = "dedicated_default"
        resolved_root = validate_profile_root(profile_root) if profile_root is not None else default_profile_root(environ)
        safe_name = validate_profile_name(profile_name)

    created = create and not existed_before and resolved_profile_dir.exists()
    return BrowserProfileResult(
        browser=normalized_browser,
        profile_dir=resolved_profile_dir,
        profile_root=resolved_root,
        profile_name=safe_name,
        source=source,
        created=created,
        message=f"{normalized_browser} profile directory ready at {resolved_profile_dir}",
    )


def ensure_browser_profile_dir(
    browser: str,
    *,
    profile_name: str = DEFAULT_PROFILE_NAME,
    profile_root: str | Path | None = None,
    profile_dir: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    return resolve_browser_profile(
        browser,
        profile_name=profile_name,
        profile_root=profile_root,
        profile_dir=profile_dir,
        environ=environ,
        create=True,
    ).profile_dir
