from __future__ import annotations

import json
from pathlib import Path

from patchops.suspicious_artifacts import SuspiciousRunArtifact

MARKER = "PATCHOPS_MP44_STRUCTURED_BUG_ARTIFACT_MODEL_TEST"


def test_bug_artifact_to_dict_contains_required_fields(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="summary contradicts required command evidence",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="apply",
        manifest_path=tmp_path / "patch_manifest.json",
        recommended_follow_up="inspect report and repair wrapper layer",
    )

    payload = artifact.to_dict()

    assert payload["detection_reason"] == "summary contradicts required command evidence"
    assert payload["failure_class"] == "wrapper_failure"
    assert payload["workflow_mode"] == "apply"
    assert payload["report_path"].endswith("latest_report.txt")
    assert payload["manifest_path"].endswith("patch_manifest.json")
    assert payload["recommended_follow_up"] == "inspect report and repair wrapper layer"


def test_bug_artifact_json_text_is_machine_readable(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="critical provenance fields missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "report.txt",
        workflow_mode="verify",
        recommended_follow_up="collect fresh wrapper evidence",
    )

    parsed = json.loads(artifact.to_json_text())

    assert parsed["detection_reason"] == "critical provenance fields missing"
    assert parsed["failure_class"] == "wrapper_failure"
    assert parsed["workflow_mode"] == "verify"
    assert parsed["manifest_path"] is None
    assert parsed["recommended_follow_up"] == "collect fresh wrapper evidence"


def test_bug_artifact_path_fields_are_stringified(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="latest copied report missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "nested" / "report.txt",
        workflow_mode="export_handoff",
        manifest_path=tmp_path / "patch_manifest.json",
    )

    payload = artifact.to_dict()

    assert isinstance(payload["report_path"], str)
    assert isinstance(payload["manifest_path"], str)


def test_bug_artifact_keeps_shape_compact_when_manifest_path_missing(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="core report fields missing",
        failure_class="wrapper_failure",
        report_path=tmp_path / "report.txt",
        workflow_mode="wrapper_retry",
        manifest_path=None,
        recommended_follow_up=None,
    )

    payload = artifact.to_dict()
    assert set(payload.keys()) == {
        "detection_reason",
        "failure_class",
        "report_path",
        "workflow_mode",
        "manifest_path",
        "recommended_follow_up",
    }
