from __future__ import annotations

import json

from patchops.edge_rpa.edge_current_url_upload_menu_repair import CurrentUrlGuardUploadMenuRepairResult, _canonical_url, _score_upload_menu_candidate, assert_l26_12d_acceptance


def test_canonical_url_ignores_query_fragment_and_trailing_slash() -> None:
    assert _canonical_url("https://chatgpt.com/g/x/c/y/?model=z#frag") == _canonical_url("https://chatgpt.com/g/x/c/y")


def test_upload_menu_scoring_accepts_file_like_labels() -> None:
    assert _score_upload_menu_candidate("MenuItem", "", "Upload from computer", "") >= 90
    assert _score_upload_menu_candidate("Button", "", "Add photos and files", "") >= 90
    assert _score_upload_menu_candidate("Button", "", "Add files and more", "composer-plus-btn") == 0


def test_payload_json_safe() -> None:
    result = CurrentUrlGuardUploadMenuRepairResult(report_candidate_hash="abc", staged_file_name_hash="def")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "report_candidate_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_current_url_upload_menu_gate() -> None:
    result = CurrentUrlGuardUploadMenuRepairResult(
        target_url_is_requested_chat=True,
        current_url_read_attempted=True,
        current_url_observed=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
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
        upload_menu_inventory_written=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12d_acceptance(result)


def test_acceptance_rejects_navigation_refresh_or_send() -> None:
    result = CurrentUrlGuardUploadMenuRepairResult(
        target_url_is_requested_chat=True,
        current_url_read_attempted=True,
        current_url_observed=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=True,
        target_page_ready=True,
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
        upload_menu_inventory_written=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="def",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    try:
        assert_l26_12d_acceptance(result)
    except AssertionError as exc:
        assert "navigation_attempted" in str(exc)
    else:
        raise AssertionError("Navigation refresh must fail the same-URL skip acceptance")
