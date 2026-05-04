from patchops.edge_rpa.edge_l26_13c_stable_latest_canonical_upload_source import StableLatestCanonicalUploadSourceResult, assert_acceptance

def test_acceptance_passes_stable_latest_source() -> None:
    r = StableLatestCanonicalUploadSourceResult(stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_path="C:/latest.txt", latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_wildcard_selection() -> None:
    r = StableLatestCanonicalUploadSourceResult(stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_path="C:/latest.txt", latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, wildcard_source_selection_used=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "wildcard_source_selection_used" in str(exc)
    else:
        raise AssertionError("Wildcard source selection must fail L26.13C acceptance")

def test_acceptance_rejects_raw_apply_upload() -> None:
    r = StableLatestCanonicalUploadSourceResult(stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_path="C:/latest.txt", latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, raw_apply_report_uploaded_as_browser_target=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "raw_apply_report_uploaded_as_browser_target" in str(exc)
    else:
        raise AssertionError("Raw apply report upload target must fail L26.13C acceptance")
