"""Optional PatchOps LLM browser runner package.

This package intentionally performs no Selenium imports at package import time.
Browser-specific dependencies are loaded lazily by later command modules so
core PatchOps remains usable without installing the optional browser extra.
"""

from __future__ import annotations

__all__ = ["BROWSER_OPTIONAL_DEPENDENCIES", "browser_optional_dependency_names"]

BROWSER_OPTIONAL_DEPENDENCIES: tuple[str, ...] = (
    "selenium>=4.20",
    "webdriver-manager>=4.0",
    "psutil>=5.9",
    "pyperclip>=1.8",
)


def browser_optional_dependency_names() -> tuple[str, ...]:
    """Return the distribution names required by the optional browser extra."""

    return BROWSER_OPTIONAL_DEPENDENCIES
