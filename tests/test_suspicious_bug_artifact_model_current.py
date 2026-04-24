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
        workflow_mode="verify_only",
        manifest_path=None,
        recommended_follow_up="capture wrapper evidence before rerun",
    )

    payload = json.loads(artifact.to_json_text())

    assert payload["detection_reason"] == "critical provenance fields missing"
    assert payload["failure_class"] == "wrapper_failure"
    assert payload["workflow_mode"] == "verify_only"
    assert payload["report_path"].endswith("report.txt")
    assert payload["manifest_path"] is None
    assert payload["recommended_follow_up"] == "capture wrapper evidence before rerun"


def test_bug_artifact_json_text_stays_pretty_and_stable(tmp_path: Path):
    artifact = SuspiciousRunArtifact(
        detection_reason="missing latest report copy",
        failure_class="wrapper_failure",
        report_path=tmp_path / "latest_report.txt",
        workflow_mode="export_handoff",
        manifest_path=tmp_path / "manifest.json",
        recommended_follow_up="repair handoff export path",
    )

    text = artifact.to_json_text()

    assert text.endswith("\n")
    assert '"detection_reason"' in text
    assert '"failure_class"' in text
    assert '"recommended_follow_up"' in text
