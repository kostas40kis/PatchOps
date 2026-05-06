from __future__ import annotations

import json
import sys
from pathlib import Path

from patchops.copilot_downloader.commands import run_foundation_doctor
from patchops.copilot_downloader.evidence import write_evidence_pair
from patchops.copilot_downloader.models import (
    FOUNDATION_RESULT_LABEL,
    RESULT_LABELS,
    DownloaderEvidenceRecord,
    DownloaderSafetyFlags,
)
from patchops.copilot_downloader.safety_policy import default_safety_flags, validate_foundation_boundary


def test_result_labels_include_foundation_and_downloader_ladder_labels():
    assert FOUNDATION_RESULT_LABEL in RESULT_LABELS
    for label in [
        "PASS_ARTIFACT_DETECTED",
        "PASS_STABLE_ARTIFACT_VALIDATED",
        "PASS_SCRIPT_EXTRACTED_RUN_BLOCKED",
        "PASS_SCRIPT_VALIDATED_RUN_BLOCKED",
        "PASS_PATCHOPS_RUN_COMPLETED",
        "PASS_CANONICAL_REPORT_FOUND",
        "PASS_HANDOFF_WRITTEN",
        "BLOCKED_NO_ARTIFACT",
        "BLOCKED_UNSTABLE_FILE",
        "BLOCKED_INVALID_ARTIFACT",
        "BLOCKED_AMBIGUOUS_ARTIFACTS",
        "BLOCKED_RUN_NOT_AUTHORIZED",
        "BLOCKED_BROWSER_NOT_READY",
        "BLOCKED_AMBIGUOUS_BROWSER_TARGET",
        "BLOCKED_LOGIN_OR_CHALLENGE",
        "FAIL_PATCHOPS_RUN",
        "FAIL_REPORT_MISSING",
        "FAIL_HANDOFF_WRITE",
    ]:
        assert label in RESULT_LABELS


def test_default_safety_flags_match_d0_01_no_runtime_side_effect_boundary():
    flags = default_safety_flags()
    data = flags.to_dict()
    assert isinstance(flags, DownloaderSafetyFlags)
    assert data
    assert all(value is False for value in data.values())
    assert flags.true_flags() == ()
    assert validate_foundation_boundary(flags) == []


def test_foundation_safety_boundary_rejects_browser_or_execution_flags():
    flags = DownloaderSafetyFlags(browser_used=True, artifact_executed=True)
    issues = validate_foundation_boundary(flags)
    assert any("browser_used" in issue for issue in issues)
    assert any("artifact_executed" in issue for issue in issues)


def test_evidence_writer_outputs_json_and_text(tmp_path: Path):
    record = DownloaderEvidenceRecord(
        patch_name="d0_01_copilot_downloader_foundation",
        result_label=FOUNDATION_RESULT_LABEL,
        safety=default_safety_flags(),
        details={"example_path": tmp_path / "example.txt"},
    )
    paths = write_evidence_pair(tmp_path, "foundation", record)
    json_path = Path(paths["json"])
    text_path = Path(paths["text"])
    assert json_path.is_file()
    assert text_path.is_file()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["producer"] == "patchops.copilot_downloader"
    assert payload["result_label"] == FOUNDATION_RESULT_LABEL
    assert payload["safety"]["browser_used"] is False
    assert "PatchOps Co-Pilot downloader evidence" in text_path.read_text(encoding="utf-8")


def test_foundation_doctor_writes_evidence_without_uploader_import_or_forbidden_actions(tmp_path: Path):
    result = run_foundation_doctor(repo_root=Path.cwd(), evidence_root=tmp_path)
    assert result["ok"] is True
    assert result["result_label"] == FOUNDATION_RESULT_LABEL
    assert result["safety"]["browser_used"] is False
    assert result["safety"]["clipboard_read"] is False
    assert result["safety"]["artifact_executed"] is False
    assert result["checks"]["uploader_module_not_imported"] is True
    assert "patchops.chatgpt_uploader" not in sys.modules
    assert Path(result["evidence_files"]["json"]).is_file()
    assert Path(result["evidence_files"]["text"]).is_file()