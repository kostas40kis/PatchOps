from patchops.edge_rpa.edge_l26_13b_canonical_rollover_publish import CanonicalRolloverPublishResult, assert_acceptance

def test_acceptance_passes_rollover_publish() -> None:
    r = CanonicalRolloverPublishResult(previous_canonical_uploaded=True, previous_canonical_source_path="C:/prev_canonical.txt", previous_canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/cur_canonical.txt", current_canonical_report_size_bytes=100, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, current_canonical_uploaded_this_run=False, latest_canonical_pointer_created=True, latest_canonical_path="C:/latest_canonical.txt", latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_current_canonical_same_run_upload() -> None:
    r = CanonicalRolloverPublishResult(previous_canonical_uploaded=True, previous_canonical_source_path="C:/prev_canonical.txt", previous_canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/cur_canonical.txt", current_canonical_report_size_bytes=100, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, current_canonical_uploaded_this_run=True, latest_canonical_pointer_created=True, latest_canonical_path="C:/latest_canonical.txt", latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "current_canonical_uploaded_this_run" in str(exc)
    else:
        raise AssertionError("Current canonical self-upload must fail acceptance")

def test_acceptance_rejects_latest_mismatch() -> None:
    r = CanonicalRolloverPublishResult(previous_canonical_uploaded=True, previous_canonical_source_path="C:/prev_canonical.txt", previous_canonical_source_hash="h", uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/cur_canonical.txt", current_canonical_report_size_bytes=100, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_path="C:/latest_canonical.txt", latest_canonical_matches_current=False, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "latest_canonical_matches_current" in str(exc)
    else:
        raise AssertionError("Latest canonical pointer must match current canonical")
