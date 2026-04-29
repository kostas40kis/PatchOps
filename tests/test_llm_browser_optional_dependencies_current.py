from __future__ import annotations

import importlib
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - maintained runtime is Python 3.11+
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_BROWSER_DEPS = {
    "selenium>=4.20",
    "webdriver-manager>=4.0",
    "psutil>=5.9",
    "pyperclip>=1.8",
}


def _load_pyproject() -> dict:
    assert tomllib is not None, "Python 3.11+ tomllib is required for this test"
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_browser_extra_is_declared_as_optional_dependency_group() -> None:
    data = _load_pyproject()
    optional = data["project"]["optional-dependencies"]
    browser_deps = set(optional["browser"])

    missing = EXPECTED_BROWSER_DEPS - browser_deps
    assert not missing, f"missing browser optional dependencies: {sorted(missing)}"


def test_llm_browser_package_import_is_lightweight() -> None:
    sys.modules.pop("patchops.llm_browser", None)
    before = set(sys.modules)

    module = importlib.import_module("patchops.llm_browser")

    newly_loaded = set(sys.modules) - before
    assert "selenium" not in newly_loaded
    assert set(module.browser_optional_dependency_names()) == EXPECTED_BROWSER_DEPS
