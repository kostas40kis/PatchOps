from __future__ import annotations

from types import SimpleNamespace

from patchops.reporting.sections import failure_section


class _Category:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_failure_section_includes_verify_only_recommendation() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed after writes already landed",
            details=None,
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : verify_only" in rendered


def test_failure_section_includes_wrapper_only_repair_recommendation() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="report writer failed after target stayed correct",
            details=None,
        ),
        target_content_already_present=True,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : wrapper_only_repair" in rendered


def test_failure_section_includes_content_repair_recommendation_when_content_is_not_already_present() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("target_project_failure"),
            message="validation failed before content was proven landed",
            details=None,
        ),
        target_content_already_present=False,
        writes_applied_by_wrapper=False,
    )

    rendered = failure_section(result)

    assert "Recommended Next Mode : content_repair" in rendered
