from __future__ import annotations

import json

from patchops.edge_rpa.edge_direct_report_upload_staging_gate import DirectReportUploadStagingResult, assert_l26_12b_acceptance


def test_payload_json_safe() -> None:
    result = DirectReportUploadStagingResult(report_candidate_hash="abc", staged_file_name_hash="def")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "report_candidate_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_direct_staging_gate() -> None:
    result = DirectReportUploadStagingResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        composer_candidate_found=True,
        composer_focus_verified=True,
        allow_report_upload_requested=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        plus_button_found=True,
        plus_button_clicked=True,
        upload_menu_item_found=True,
        upload_menu_item_clicked=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12b_acceptance(result)


def test_acceptance_rejects_chatgpt_send() -> None:
    result = DirectReportUploadStagingResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        composer_candidate_found=True,
        composer_focus_verified=True,
        allow_report_upload_requested=True,
        report_candidate_found=True,
        report_candidate_hash="abc",
        report_candidate_size_bytes=100,
        report_candidate_is_text=True,
        plus_button_found=True,
        plus_button_clicked=True,
        upload_menu_item_found=True,
        upload_menu_item_clicked=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        chatgpt_prompt_submitted=True,
        result="PASS",
    )
    try:
        assert_l26_12b_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_prompt_submitted" in str(exc)
    else:
        raise AssertionError("ChatGPT send must fail L26.12B acceptance")
