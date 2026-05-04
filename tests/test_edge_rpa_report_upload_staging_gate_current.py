from __future__ import annotations

import json

from patchops.edge_rpa.edge_report_upload_staging_gate import ReportUploadStagingResult, assert_l26_12_acceptance


def test_payload_json_safe() -> None:
    result = ReportUploadStagingResult(report_candidate_hash="abc", staged_file_name_hash="def")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "report_candidate_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_staging_gate() -> None:
    result = ReportUploadStagingResult(
        target_url_is_requested_chat=True,
        requested_chat_accessible_by_composer=True,
        composer_focus_verified=True,
        allow_report_upload_requested=True,
        report_discovery_completed=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        attach_candidate_found=True,
        attach_candidate_is_in_page_scope=True,
        report_upload_attempted=True,
        file_attach_attempted=True,
        attach_button_clicked=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_open_invoked=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        result="PASS",
    )
    assert_l26_12_acceptance(result)


def test_acceptance_rejects_send() -> None:
    result = ReportUploadStagingResult(
        target_url_is_requested_chat=True,
        requested_chat_accessible_by_composer=True,
        composer_focus_verified=True,
        allow_report_upload_requested=True,
        report_discovery_completed=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        attach_candidate_found=True,
        attach_candidate_is_in_page_scope=True,
        report_upload_attempted=True,
        file_attach_attempted=True,
        attach_button_clicked=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_open_invoked=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        send_submit_performed=True,
        result="PASS",
    )
    try:
        assert_l26_12_acceptance(result)
    except AssertionError as exc:
        assert "send_submit_performed" in str(exc)
    else:
        raise AssertionError("send must fail L26.12 acceptance")
