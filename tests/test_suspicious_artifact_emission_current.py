from __future__ import annotations

import json
from pathlib import Path

from patchops.suspicious_artifacts import SuspiciousRunArtifact, emit_suspicious_run_artifact

MARKER = "PATCHOPS_MP45_OPTIONAL_ARTIFACT_EMISSION_TEST"


def _artifact(tmp_path: Path) -> SuspiciousRunArtifact:
    return SuspiciousRunArtifact(
        detection_reason="summary contradicts required command evidence",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="apply",
        manifest_path=tmp_path / "patch_manifest.json",
        recommended_follow_up="inspect wrapper evidence before widening scope",
    )


def test_artifact_emission_is_opt_in_by_default(tmp_path: Path):
    artifact_path = tmp_path / "artifacts" / "suspicious_run.json"
    emitted = emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path)
    assert emitted is None
    assert not artifact_path.exists()


def test_artifact_is_emitted_when_flag_is_enabled(tmp_path: Path):
    artifact_path = tmp_path / "artifacts" / "suspicious_run.json"
    emitted = emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path, emit=True)
    assert emitted == artifact_path
    assert artifact_path.exists()


def test_emitted_artifact_payload_is_json_ready(tmp_path: Path):
    artifact_path = tmp_path / "nested" / "artifact.json"
    emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path, emit=True)
    parsed = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert parsed["detection_reason"] == "summary contradicts required command evidence"
    assert parsed["failure_class"] == "wrapper_failure"
    assert parsed["workflow_mode"] == "apply"
    assert parsed["report_path"].endswith("latest_report.txt")
    assert parsed["manifest_path"].endswith("patch_manifest.json")


def test_emission_creates_parent_directory_when_needed(tmp_path: Path):
    artifact_path = tmp_path / "deep" / "nested" / "artifact.json"
    emit_suspicious_run_artifact(_artifact(tmp_path), artifact_path, emit=True)
    assert artifact_path.parent.exists()
