from __future__ import annotations

import json

from patchops.edge_rpa.edge_report_upload_dry_run_gate import AttachCandidate, ReportUploadDryRunResult, assert_l26_11_acceptance


def test_payload_json_safe() -> None:
    result = ReportUploadDryRunResult(report_candidate_hash="abc", report_candidate_size_bytes=100)
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "report_candidate_hash" in encoded
    assert "report_upload_attempted" in encoded


def test_acceptance_passes_dry_run_gate() -> None:
    result = ReportUploadDryRunResult(
        target_url_is_requested_chat=True,
        requested_chat_accessible_by_composer=True,
        composer_focus_verified=True,
        report_discovery_completed=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        attach_discovery_completed=True,
        attach_candidate_found=True,
        attach_candidate_kind="composer_plus_attach_candidate",
        attach_candidate_automation_id_redacted="composer-plus-btn",
        attach_candidate_name_redacted="Add files and more",
        attach_candidate_is_in_page_scope=True,
        attach_candidate=AttachCandidate(candidate_kind="composer_plus_attach_candidate", automation_id_redacted="composer-plus-btn", name_redacted="Add files and more", is_in_page_scope=True, score=150),
        result="PASS",
    )
    assert_l26_11_acceptance(result)


def test_acceptance_rejects_upload_or_click() -> None:
    result = ReportUploadDryRunResult(
        target_url_is_requested_chat=True,
        requested_chat_accessible_by_composer=True,
        composer_focus_verified=True,
        report_discovery_completed=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        attach_discovery_completed=True,
        attach_candidate_found=True,
        attach_candidate_automation_id_redacted="composer-plus-btn",
        attach_candidate_is_in_page_scope=True,
        report_upload_attempted=True,
        result="PASS",
    )
    try:
        assert_l26_11_acceptance(result)
    except AssertionError as exc:
        assert "report_upload_attempted" in str(exc)
    else:
        raise AssertionError("upload must fail dry-run acceptance")
