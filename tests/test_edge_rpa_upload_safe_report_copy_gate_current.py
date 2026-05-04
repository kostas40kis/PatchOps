from __future__ import annotations

import json
from pathlib import Path

from patchops.edge_rpa.edge_upload_safe_report_copy_gate import UploadSafeCopyResult, _is_onedrive_path, _score_strict_upload_menu_candidate, assert_l26_12e_acceptance


def test_strict_upload_menu_rejects_onedrive_status() -> None:
    score, rejected = _score_strict_upload_menu_candidate("Button", "", "OneDrive - OTE Uploading 281.1 KB of 546.1 KB at 0.0 KB/s, 1 file remaining", "")
    assert score == 0
    assert rejected is True


def test_strict_upload_menu_accepts_real_upload_labels() -> None:
    score, rejected = _score_strict_upload_menu_candidate("MenuItem", "", "Upload files", "")
    assert score >= 100
    assert rejected is False


def test_onedrive_path_detector() -> None:
    assert _is_onedrive_path(Path("C:/Users/kostas/OneDrive - OTE/Desktop/a.txt"))
    assert not _is_onedrive_path(Path("C:/dev/patchops/data/runtime/upload/a.txt"))


def test_payload_json_safe() -> None:
    encoded = json.dumps(UploadSafeCopyResult(source_report_hash="abc", upload_safe_copy_hash="def").to_payload(), sort_keys=True)
    assert "source_report_hash" in encoded
    assert "file_content_logged" in encoded


def test_acceptance_passes_upload_safe_copy_gate() -> None:
    result = UploadSafeCopyResult(
        target_url_is_requested_chat=True,
        current_url_matches_target=True,
        navigation_skipped_existing_target=True,
        navigation_attempted=False,
        target_page_ready=True,
        composer_candidate_found=True,
        composer_focus_verified=True,
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
        upload_menu_item_found=True,
        upload_menu_item_clicked=True,
        onedrive_status_candidate_rejected=True,
        file_picker_opened=True,
        file_picker_path_entered=True,
        file_picker_confirmed=True,
        upload_staging_observed=True,
        staged_file_name_hash="ghi",
        report_upload_attempted=True,
        file_attach_attempted=True,
        result="PASS",
    )
    assert_l26_12e_acceptance(result)
