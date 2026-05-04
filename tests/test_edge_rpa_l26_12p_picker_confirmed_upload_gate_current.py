from __future__ import annotations
from patchops.edge_rpa.edge_l26_12p_picker_confirmed_upload_gate import PickerConfirmedUploadResult, assert_acceptance


def test_acceptance_passes_picker_confirmed_upload() -> None:
    r = PickerConfirmedUploadResult(
        report_path_exists=True,
        report_path_local_desktop=True,
        report_hash="rh",
        safe_copy_created=True,
        safe_copy_name="copy.txt",
        safe_copy_hash="sh",
        safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_drive_valid=True,
        composer_candidate_found=True,
        composer_cleared=True,
        slash_typed=True,
        ctrl_u_sent=True,
        foreground_picker_handoff_used=True,
        foreground_class="#32770",
        full_quoted_path_used=True,
        filename_field_strategy="alt_n_full_quoted_path_enter",
        picker_confirmed=True,
        picker_enter_sent=True,
        picker_confirmed_upload_accepted=True,
        slash_leftover_tolerated=True,
        result="PASS",
    )
    assert_acceptance(r)


def test_acceptance_rejects_cleanup() -> None:
    r = PickerConfirmedUploadResult(
        report_path_exists=True,
        report_path_local_desktop=True,
        report_hash="rh",
        safe_copy_created=True,
        safe_copy_name="copy.txt",
        safe_copy_hash="sh",
        safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_drive_valid=True,
        composer_candidate_found=True,
        composer_cleared=True,
        slash_typed=True,
        ctrl_u_sent=True,
        foreground_picker_handoff_used=True,
        foreground_class="#32770",
        full_quoted_path_used=True,
        filename_field_strategy="alt_n_full_quoted_path_enter",
        picker_confirmed=True,
        picker_enter_sent=True,
        picker_confirmed_upload_accepted=True,
        slash_leftover_tolerated=True,
        cleanup_attempted=True,
        result="PASS",
    )
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "cleanup_attempted" in str(exc)
    else:
        raise AssertionError("Cleanup must not be part of L26.12P")
