from __future__ import annotations

from patchops.edge_rpa.edge_ctrl_u_upload_shortcut_gate import CtrlUUploadShortcutResult, assert_l26_12h_acceptance


def test_acceptance_passes_ctrl_u_upload_shortcut_result() -> None:
    result = CtrlUUploadShortcutResult(
        target_url_is_requested_chat=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
        composer_candidate_found=True,
        source_report_found=True,
        source_report_hash="abc",
        source_report_size_bytes=100,
        source_report_is_text=True,
        upload_safe_copy_created=True,
        upload_safe_copy_hash="abc",
        upload_safe_copy_size_bytes=100,
        upload_safe_copy_closed=True,
        safe_copy_outside_onedrive=True,
        allow_report_upload_requested=True,
        plus_button_found=True,
        plus_button_clicked=True,
        ctrl_u_shortcut_sent=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        file_picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12h_acceptance(result)


def test_acceptance_rejects_chatgpt_submit_enter() -> None:
    result = CtrlUUploadShortcutResult(
        target_url_is_requested_chat=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
        composer_candidate_found=True,
        source_report_found=True,
        source_report_hash="abc",
        source_report_size_bytes=100,
        source_report_is_text=True,
        upload_safe_copy_created=True,
        upload_safe_copy_hash="abc",
        upload_safe_copy_size_bytes=100,
        upload_safe_copy_closed=True,
        safe_copy_outside_onedrive=True,
        allow_report_upload_requested=True,
        plus_button_found=True,
        plus_button_clicked=True,
        ctrl_u_shortcut_sent=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        file_picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        chatgpt_submit_enter_sent=True,
        result="PASS",
    )
    try:
        assert_l26_12h_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_submit_enter_sent" in str(exc)
    else:
        raise AssertionError("ChatGPT submit Enter must fail L26.12H acceptance")
