from __future__ import annotations

from pathlib import Path

from patchops.suspicious_artifacts import (
    SuspiciousRunArtifact,
    emit_suspicious_run_artifact,
    suspicious_run_artifact_report_lines,
)

MARKER = "PATCHOPS_MP46A_ARTIFACT_REPORT_MENTION_REPAIR_TEST"


def _artifact(tmp_path: Path) -> SuspiciousRunArtifact:
    return SuspiciousRunArtifact(
        detection_reason="summary contradicts required command evidence",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="apply",
        manifest_path=tmp_path / "patch_manifest.json",
        recommended_follow_up="inspect wrapper evidence before widening scope",
    )


def test_report_lines_are_empty_when_no_artifact_was_emitted(tmp_path: Path):
    lines = suspicious_run_artifact_report_lines(None)
    assert lines == []


def test_report_lines_include_emitted_artifact_path(tmp_path: Path):
    artifact_path = tmp_path / "artifacts" / "suspicious_run.json"
    emitted = emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path, emit=True)
    lines = suspicious_run_artifact_report_lines(emitted)
    assert len(lines) == 1
    assert lines[0].startswith("Suspicious-run artifact emitted : ")
    assert str(artifact_path) in lines[0]


def test_report_line_wording_stays_compact():
    line = suspicious_run_artifact_report_lines(Path("artifact.json"))[0]
    assert "emitted" in line.lower()
    assert "artifact" in line.lower()
    label_text = line.split(":", 1)[0].lower()
    assert "report" not in label_text
