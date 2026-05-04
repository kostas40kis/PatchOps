from __future__ import annotations
from patchops.edge_rpa.edge_l26_12m_upload_gate import UploadResult, has_bad_lc_prefix, assert_acceptance


def test_bad_lc_prefix_detector() -> None:
    from pathlib import Path
    assert has_bad_lc_prefix(Path("lC:/dev/patchops/file.txt"))
    assert has_bad_lc_prefix(Path("iC:/dev/patchops/file.txt"))
    assert not has_bad_lc_prefix(Path("C:/dev/patchops/file.txt"))


def test_acceptance_rejects_ctrl_l_usage() -> None:
    r = UploadResult(
        report_path_exists=True,
        report_path_local_desktop=True,
        report_hash="a",
        safe_copy_created=True,
        safe_copy_name="copy.txt",
        safe_copy_hash="a",
        safe_copy_closed=True,
        safe_copy_hash_matches_report=True,
        safe_copy_drive_valid=True,
        composer_candidate_found=True,
        composer_cleared=True,
        slash_typed=True,
        ctrl_u_sent=True,
        foreground_picker_handoff_used=True,
        foreground_class="#32770",
        ctrl_l_used=True,
        full_quoted_path_used=True,
        filename_field_strategy="x",
        picker_confirmed=True,
        picker_enter_sent=True,
        upload_staging_observed=True,
        staged_file_name_hash="s",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "ctrl_l_used" in str(exc)
    else:
        raise AssertionError("Ctrl+L use must fail acceptance")
