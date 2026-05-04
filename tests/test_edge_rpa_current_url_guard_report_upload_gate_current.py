from __future__ import annotations

import json

from patchops.edge_rpa.edge_current_url_guard_report_upload_gate import CurrentUrlGuardUploadResult, _canonical_url, assert_l26_12c_acceptance


def test_canonical_url_ignores_query_fragment_and_trailing_slash() -> None:
    a = "https://chatgpt.com/g/g-p-abc/c/123/?model=x#frag"
    b = "https://chatgpt.com/g/g-p-abc/c/123"
    assert _canonical_url(a) == _canonical_url(b)


def test_payload_json_safe() -> None:
    result = CurrentUrlGuardUploadResult(report_candidate_hash="abc", staged_file_name_hash="def")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "report_candidate_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_current_url_skip_staging_gate() -> None:
    result = CurrentUrlGuardUploadResult(
        target_url_is_requested_chat=True,
        current_url_read_attempted=True,
        current_url_observed=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        navigation_observed=True,
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
    assert_l26_12c_acceptance(result)


def test_acceptance_rejects_navigation_refresh_or_send() -> None:
    result = CurrentUrlGuardUploadResult(
        target_url_is_requested_chat=True,
        current_url_read_attempted=True,
        current_url_observed=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=True,
        navigation_observed=True,
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
        assert_l26_12c_acceptance(result)
    except AssertionError as exc:
        assert "navigation_attempted" in str(exc)
    else:
        raise AssertionError("Navigation refresh must fail the same-URL skip acceptance")
