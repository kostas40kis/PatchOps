from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from patchops.reporting.sections import failure_section


class _Category:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return self.value


def test_failure_section_includes_suspicious_artifact_line_when_present(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifacts" / "suspicious_run.json"
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="summary contradicted required command evidence",
            details=None,
        ),
        suspicious_artifact_path=artifact_path,
    )

    rendered = failure_section(result)

    assert "Suspicious Run Artifact : " in rendered
    assert f"Suspicious Run Artifact : {artifact_path}" in rendered


def test_failure_section_omits_suspicious_artifact_line_when_absent() -> None:
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="summary contradicted required command evidence",
            details=None,
        )
    )

    rendered = failure_section(result)

    assert "Suspicious Run Artifact : " not in rendered


def test_failure_section_keeps_artifact_line_compact(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.json"
    result = SimpleNamespace(
        failure=SimpleNamespace(
            category=_Category("wrapper_failure"),
            message="summary contradicted required command evidence",
            details=None,
        ),
        suspicious_artifact_path=artifact_path,
    )

    rendered = failure_section(result)
    artifact_lines = [line for line in rendered.splitlines() if line.startswith("Suspicious Run Artifact : ")]

    assert len(artifact_lines) == 1
    assert "failure_class" not in artifact_lines[0]
    assert "detection_reason" not in artifact_lines[0]
