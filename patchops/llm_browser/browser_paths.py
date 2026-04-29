"""Browser executable path discovery for the optional LLM browser runner.

This module is pure Python and passive:
- it imports no Selenium modules,
- it starts no browser driver,
- it opens no browser window,
- it creates no network listener.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Callable, Iterable, Mapping


PathExists = Callable[[Path], bool]


SUPPORTED_BROWSERS: tuple[str, ...] = ("edge", "opera")


@dataclass(frozen=True)
class BrowserPathResult:
    browser: str
    executable_path: Path | None
    candidates: tuple[Path, ...]
    source: str
    message: str

    @property
    def found(self) -> bool:
        return self.executable_path is not None

    def to_payload(self) -> dict[str, object]:
        return {
            "browser": self.browser,
            "found": self.found,
            "executable_path": None if self.executable_path is None else str(self.executable_path),
            "candidates": [str(candidate) for candidate in self.candidates],
            "source": self.source,
            "message": self.message,
        }


def _path_exists(path: Path) -> bool:
    return path.exists()


def normalize_browser(browser: str) -> str:
    normalized = browser.strip().lower()
    if normalized not in SUPPORTED_BROWSERS:
        raise ValueError(f"browser must be one of: {', '.join(SUPPORTED_BROWSERS)}")
    return normalized


def _explicit_override_path(
    *,
    browser: str,
    explicit_path: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path | None:
    if explicit_path is not None:
        return Path(explicit_path)

    env = os.environ if environ is None else environ
    if browser == "edge":
        value = env.get("PATCHOPS_EDGE_PATH") or env.get("MSEDGE_PATH")
    elif browser == "opera":
        value = env.get("PATCHOPS_OPERA_PATH") or env.get("OPERA_PATH")
    else:
        value = None

    return None if not value else Path(value)


def edge_candidate_paths(
    environ: Mapping[str, str] | None = None,
    *,
    explicit_path: str | Path | None = None,
) -> tuple[Path, ...]:
    candidates: list[Path] = []
    override = _explicit_override_path(browser="edge", explicit_path=explicit_path, environ=environ)
    if override is not None:
        candidates.append(override)

    candidates.extend(
        [
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ]
    )
    return tuple(candidates)


def opera_candidate_paths(
    environ: Mapping[str, str] | None = None,
    *,
    explicit_path: str | Path | None = None,
) -> tuple[Path, ...]:
    env = os.environ if environ is None else environ
    candidates: list[Path] = []
    override = _explicit_override_path(browser="opera", explicit_path=explicit_path, environ=env)
    if override is not None:
        candidates.append(override)

    local_app_data = env.get("LOCALAPPDATA")
    if local_app_data:
        candidates.extend(
            [
                Path(local_app_data) / "Programs" / "Opera" / "opera.exe",
                Path(local_app_data) / "Programs" / "Opera GX" / "opera.exe",
            ]
        )

    candidates.extend(
        [
            Path(r"C:\Program Files\Opera\opera.exe"),
            Path(r"C:\Program Files\Opera GX\opera.exe"),
            Path(r"C:\Program Files (x86)\Opera\opera.exe"),
            Path(r"C:\Program Files (x86)\Opera GX\opera.exe"),
        ]
    )
    return tuple(candidates)


def browser_candidate_paths(
    browser: str,
    environ: Mapping[str, str] | None = None,
    *,
    explicit_path: str | Path | None = None,
) -> tuple[Path, ...]:
    normalized = normalize_browser(browser)
    if normalized == "edge":
        return edge_candidate_paths(environ, explicit_path=explicit_path)
    return opera_candidate_paths(environ, explicit_path=explicit_path)


def first_existing_path(
    candidates: Iterable[Path],
    *,
    exists: PathExists = _path_exists,
) -> Path | None:
    for candidate in candidates:
        try:
            if exists(candidate):
                return candidate
        except OSError:
            continue
    return None


def find_browser_path(
    browser: str,
    *,
    explicit_path: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    exists: PathExists = _path_exists,
) -> BrowserPathResult:
    normalized = normalize_browser(browser)
    candidates = browser_candidate_paths(normalized, environ, explicit_path=explicit_path)
    found_path = first_existing_path(candidates, exists=exists)

    if found_path is None:
        return BrowserPathResult(
            browser=normalized,
            executable_path=None,
            candidates=candidates,
            source="not_found",
            message=f"{normalized} executable was not found in known locations.",
        )

    explicit_candidate = _explicit_override_path(
        browser=normalized,
        explicit_path=explicit_path,
        environ=os.environ if environ is None else environ,
    )
    source = "override" if explicit_candidate is not None and found_path == explicit_candidate else "candidate"

    return BrowserPathResult(
        browser=normalized,
        executable_path=found_path,
        candidates=candidates,
        source=source,
        message=f"{normalized} executable found at {found_path}",
    )


def require_browser_path(
    browser: str,
    *,
    explicit_path: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    exists: PathExists = _path_exists,
) -> Path:
    result = find_browser_path(
        browser,
        explicit_path=explicit_path,
        environ=environ,
        exists=exists,
    )
    if result.executable_path is None:
        raise FileNotFoundError(result.message)
    return result.executable_path
