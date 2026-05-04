from __future__ import annotations
from patchops.edge_rpa.edge_l26_12o_upload_only_gate import UploadOnlyResult, assert_acceptance


def test_acceptance_allows_leftover_slash_without_cleanup() -> None:
    r = UploadOnlyResult(
        upload_result="PASS",
        upload_staging_observed=True,
        staged_file_name_hash="abc",
        slash_leftover_tolerated=True,
        cleanup_attempted=False,
        report_path_local_desktop=True,
        safe_copy_created=True,
        safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_drive_valid=True,
        full_quoted_path_used=True,
        picker_confirmed=True,
        picker_enter_sent=True,
        result="PASS",
    )
    assert_acceptance(r)


def test_acceptance_rejects_cleanup_attempt() -> None:
    r = UploadOnlyResult(
        upload_result="PASS",
        upload_staging_observed=True,
        staged_file_name_hash="abc",
        slash_leftover_tolerated=True,
        cleanup_attempted=True,
        report_path_local_desktop=True,
        safe_copy_created=True,
        safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_drive_valid=True,
        full_quoted_path_used=True,
        picker_confirmed=True,
        picker_enter_sent=True,
        result="PASS",
    )
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "cleanup_attempted" in str(exc)
    else:
        raise AssertionError("Cleanup must be outside L26.12O acceptance")
