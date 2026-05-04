from __future__ import annotations

from patchops.edge_rpa.edge_slash_ctrl_u_explorer_picker_gate import SlashCtrlUExplorerPickerResult, assert_l26_12i_acceptance


def test_acceptance_passes_slash_ctrl_u_picker_result() -> None:
    result = SlashCtrlUExplorerPickerResult(
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
        slash_typed_in_composer=True,
        plus_button_found=True,
        plus_button_clicked=True,
        ctrl_u_shortcut_sent=True,
        picker_window_detected=True,
        picker_window_kind="#32770",
        picker_path_set_strategy="alt_n_clipboard_enter",
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
    assert_l26_12i_acceptance(result)


def test_acceptance_rejects_chatgpt_submit_enter() -> None:
    result = SlashCtrlUExplorerPickerResult(
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
        slash_typed_in_composer=True,
        plus_button_found=True,
        plus_button_clicked=True,
        ctrl_u_shortcut_sent=True,
        picker_window_detected=True,
        picker_window_kind="#32770",
        picker_path_set_strategy="alt_n_clipboard_enter",
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
        assert_l26_12i_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_submit_enter_sent" in str(exc)
    else:
        raise AssertionError("ChatGPT submit Enter must fail L26.12I acceptance")
