from patchops.edge_rpa.edge_l26_13a_canonical_report_upload_target_smoke import CanonicalReportUploadTargetSmokeResult, assert_acceptance

def test_acceptance_passes_canonical_upload_target() -> None:
    r = CanonicalReportUploadTargetSmokeResult(canonical_upload_source_exists=True, canonical_source_is_canonical_report=True, canonical_source_contains_apply_evidence=True, canonical_source_contains_browser_evidence=True, canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, uploaded_safe_copy_path="C:/short/canonical_browser_evidence_report.txt", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_raw_apply_report_upload_target() -> None:
    r = CanonicalReportUploadTargetSmokeResult(canonical_upload_source_exists=True, canonical_source_is_canonical_report=True, canonical_source_contains_apply_evidence=True, canonical_source_contains_browser_evidence=True, canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, uploaded_safe_copy_path="C:/short/canonical_browser_evidence_report.txt", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, raw_apply_report_uploaded_as_browser_target=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "raw_apply_report_uploaded_as_browser_target" in str(exc)
    else:
        raise AssertionError("Raw apply report must not be accepted as browser upload target")

def test_acceptance_rejects_missing_browser_evidence() -> None:
    r = CanonicalReportUploadTargetSmokeResult(canonical_upload_source_exists=True, canonical_source_is_canonical_report=True, canonical_source_contains_apply_evidence=True, canonical_source_contains_browser_evidence=False, canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, uploaded_safe_copy_path="C:/short/canonical_browser_evidence_report.txt", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, allow_chatgpt_submit=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "canonical_source_contains_browser_evidence" in str(exc)
    else:
        raise AssertionError("Canonical source must include browser evidence")
