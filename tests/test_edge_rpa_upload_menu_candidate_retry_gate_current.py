from __future__ import annotations

from patchops.edge_rpa.edge_upload_menu_candidate_retry_gate import MenuCandidateFingerprint, UploadMenuCandidateRetryResult, assert_l26_12g_acceptance


def test_candidate_fingerprint_payload_is_redacted() -> None:
    fp = MenuCandidateFingerprint(fingerprint="abc", control_type="Button", score=120, name_length=25, automation_id_length=0, class_name_length=3, depth=4)
    payload = fp.to_payload()
    assert payload["fingerprint"] == "abc"
    assert "name" not in payload


def test_acceptance_passes_retry_result() -> None:
    result = UploadMenuCandidateRetryResult(
        target_url_is_requested_chat=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
        source_report_found=True,
        source_report_hash="abc",
        source_report_size_bytes=100,
        source_report_is_text=True,
        upload_safe_copy_created=True,
        upload_safe_copy_hash="abc",
        upload_safe_copy_size_bytes=100,
        upload_safe_copy_closed=True,
        safe_copy_outside_onedrive=True,
        composer_candidate_found=True,
        allow_report_upload_requested=True,
        plus_button_found=True,
        plus_button_clicked=True,
        edge_scoped_candidate_retry_used=True,
        candidate_count=2,
        candidate_attempt_count=2,
        successful_candidate_fingerprint="good",
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12g_acceptance(result)
