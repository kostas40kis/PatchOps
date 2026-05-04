from __future__ import annotations

from patchops.edge_rpa.edge_local_desktop_fullpath_upload_gate import LocalDesktopFullPathUploadResult, _has_lc_prefix, assert_l26_12l_acceptance


def test_lc_prefix_detector() -> None:
    assert _has_lc_prefix("lC:\\dev\\patchops\\x.txt")
    assert _has_lc_prefix("iC:\\dev\\patchops\\x.txt")
    assert not _has_lc_prefix("C:\\dev\\patchops\\x.txt")


def test_acceptance_passes_local_desktop_fullpath_result() -> None:
    result = LocalDesktopFullPathUploadResult(
        local_desktop_report_path_used=True,
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
        safe_copy_full_path_used=True,
        safe_copy_full_path_drive_valid=True,
        safe_copy_full_path_had_lc_prefix=False,
        composer_candidate_found=True,
        composer_cleared_before_slash=True,
        slash_typed_in_composer=True,
        plus_button_clicked_after_slash=False,
        ctrl_u_shortcut_sent=True,
        foreground_picker_handoff_used=True,
        foreground_window_class="#32770",
        picker_ctrl_l_used=False,
        picker_full_path_entry_attempted=True,
        picker_full_path_quoted=True,
        picker_filename_field_strategy="alt_n_full_quoted_path_enter",
        file_picker_confirmed=True,
        file_picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12l_acceptance(result)


def test_acceptance_rejects_ctrl_l_usage() -> None:
    result = LocalDesktopFullPathUploadResult(
        local_desktop_report_path_used=True,
        report_path_exists=True,
        report_path_written_by_outer_script=True,
        report_hash="abc",
        report_safe_copy_created=True,
        report_safe_copy_name="copy.txt",
        report_safe_copy_hash="abc",
        report_safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_outside_onedrive=True,
        safe_copy_full_path_used=True,
        safe_copy_full_path_drive_valid=True,
        composer_candidate_found=True,
        composer_cleared_before_slash=True,
        slash_typed_in_composer=True,
        ctrl_u_shortcut_sent=True,
        foreground_picker_handoff_used=True,
        foreground_window_class="#32770",
        picker_ctrl_l_used=True,
        picker_full_path_entry_attempted=True,
        picker_full_path_quoted=True,
        picker_filename_field_strategy="bad",
        file_picker_confirmed=True,
        file_picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    try:
        assert_l26_12l_acceptance(result)
    except AssertionError as exc:
        assert "picker_ctrl_l_used" in str(exc)
    else:
        raise AssertionError("Ctrl+L picker usage must fail L26.12L acceptance")
