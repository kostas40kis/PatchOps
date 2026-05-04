from __future__ import annotations

from patchops.edge_rpa.edge_foreground_picker_directory_upload_gate import ForegroundPickerUploadResult, assert_l26_12k_acceptance


def test_acceptance_passes_foreground_picker_result() -> None:
    result = ForegroundPickerUploadResult(
        target_chat_accepted_without_navigation=True,
        navigation_attempted=False,
        report_path_exists=True,
        report_path_written_by_outer_script=True,
        report_hash="abc",
        report_size_bytes=100,
        report_safe_copy_created=True,
        report_safe_copy_name="upload_copy_of_report.txt",
        report_safe_copy_hash="abc",
        report_safe_copy_size_bytes=100,
        report_safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_outside_onedrive=True,
        composer_candidate_found=True,
        composer_cleared_before_slash=True,
        slash_typed_in_composer=True,
        plus_button_clicked_after_slash=False,
        ctrl_u_shortcut_sent=True,
        foreground_picker_handoff_used=True,
        foreground_window_class="#32770",
        picker_keyboard_entry_attempted=True,
        picker_directory_change_attempted=True,
        picker_directory_changed_assumed=True,
        picker_filename_entered=True,
        file_picker_confirmed=True,
        file_picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12k_acceptance(result)


def test_acceptance_rejects_chatgpt_submit() -> None:
    result = ForegroundPickerUploadResult(
        target_chat_accepted_without_navigation=True,
        navigation_attempted=False,
        report_path_exists=True,
        report_path_written_by_outer_script=True,
        report_hash="abc",
        report_safe_copy_created=True,
        report_safe_copy_name="copy.txt",
        report_safe_copy_hash="abc",
        report_safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_outside_onedrive=True,
        composer_candidate_found=True,
        composer_cleared_before_slash=True,
        slash_typed_in_composer=True,
        ctrl_u_shortcut_sent=True,
        foreground_picker_handoff_used=True,
        foreground_window_class="#32770",
        picker_keyboard_entry_attempted=True,
        picker_directory_change_attempted=True,
        picker_directory_changed_assumed=True,
        picker_filename_entered=True,
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
        assert_l26_12k_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_submit_enter_sent" in str(exc)
    else:
        raise AssertionError("ChatGPT submit must fail L26.12K acceptance")
