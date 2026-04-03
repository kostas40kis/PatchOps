from __future__ import annotations

from types import SimpleNamespace

from patchops.reporting.sections import failure_section


class _Category:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_failure_section_includes_failure_class_and_reason() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="wrapper layer failed after authoring",
            details="report capture mismatch",
        )
    )

    rendered = failure_section(result)

    assert "FAILURE DETAILS" in rendered
    assert "Failure Class : wrapper_failure" in rendered
    assert "Failure Reason: wrapper layer failed after authoring" in rendered
    assert "Category : wrapper_failure" in rendered
    assert "Message  : wrapper layer failed after authoring" in rendered
    assert "Details  : report capture mismatch" in rendered


def test_failure_section_none_shape_stays_compact() -> None:
    result = SimpleNamespace(failure=None)
    rendered = failure_section(result)
    assert "FAILURE DETAILS" in rendered
    assert "(none)" in rendered
