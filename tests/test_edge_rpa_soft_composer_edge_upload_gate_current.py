from __future__ import annotations

from patchops.edge_rpa.edge_soft_composer_edge_upload_gate import SoftComposerEdgeUploadResult, _score_edge_upload_candidate, assert_l26_12f_acceptance


def test_edge_upload_scoring_rejects_onedrive_status() -> None:
    assert _score_edge_upload_candidate("Button", "OneDrive Uploading 1 file remaining", "", "") == 0


def test_edge_upload_scoring_accepts_upload_files() -> None:
    assert _score_edge_upload_candidate("Button", "Upload files", "", "") >= 100


def test_acceptance_allows_soft_composer_focus_failure_when_candidate_exists() -> None:
    result = SoftComposerEdgeUploadResult(
        target_url_is_requested_chat=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
        composer_candidate_found=True,
        composer_focus_verified=False,
        composer_focus_soft_failure_allowed=True,
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
        edge_scoped_menu_search_used=True,
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
    assert_l26_12f_acceptance(result)
