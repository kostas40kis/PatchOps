from __future__ import annotations

from types import SimpleNamespace

import pytest


def test_apply_workflow_normalize_helper_delegates_to_normalizer(monkeypatch: pytest.MonkeyPatch) -> None:
    from patchops.workflows import apply_patch as module

    seen: dict[str, object] = {}

    def fake_normalize(category: object) -> object:
        seen["category"] = category
        return "wrapper_failure"

    monkeypatch.setattr(module, "normalize_failure_category", fake_normalize)
    failure = SimpleNamespace(category="wrapper mechanics failure", message="boom", details={"x": 1})

    normalized = module._normalize_failure_info(failure)

    assert seen["category"] == "wrapper mechanics failure"
    assert normalized.category == "wrapper_failure"
    assert normalized.message == "boom"
    assert normalized.details == {"x": 1}


def test_apply_workflow_normalize_helper_passes_through_when_category_is_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    from patchops.workflows import apply_patch as module

    monkeypatch.setattr(module, "normalize_failure_category", lambda category: category)
    failure = SimpleNamespace(category=None, message="boom", details=None)

    normalized = module._normalize_failure_info(failure)

    assert normalized is failure
