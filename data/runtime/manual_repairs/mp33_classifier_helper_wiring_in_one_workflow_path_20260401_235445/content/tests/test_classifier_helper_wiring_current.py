from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


def test_apply_workflow_source_mentions_classifier_helper_wiring():
    source = Path("patchops/workflows/apply_patch.py").read_text(encoding="utf-8")
    assert "from patchops.failure_categories import normalize_failure_category" in source
    assert "def _normalize_failure_info(" in source
    assert "failure=_normalize_failure_info(failure)" in source


def test_apply_workflow_normalize_helper_delegates_to_normalizer(monkeypatch: pytest.MonkeyPatch):
    from patchops.workflows import apply_patch as module

    failure = SimpleNamespace(category="legacy_category_value", message="x")
    seen: dict[str, str] = {}

    def fake_normalize(value: str) -> str:
        seen["value"] = value
        return "normalized_by_fake"

    monkeypatch.setattr(module, "normalize_failure_category", fake_normalize)
    result = module._normalize_failure_info(failure)

    assert result is failure
    assert seen["value"] == "legacy_category_value"
    assert result.category == "normalized_by_fake"


def test_apply_workflow_normalize_helper_passes_through_missing_category():
    from patchops.workflows import apply_patch as module

    failure = SimpleNamespace(message="x")
    result = module._normalize_failure_info(failure)

    assert result is failure
    assert not hasattr(result, "category")
