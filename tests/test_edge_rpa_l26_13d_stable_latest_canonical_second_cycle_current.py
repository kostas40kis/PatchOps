from patchops.edge_rpa.edge_l26_13d_stable_latest_canonical_second_cycle import StableLatestCanonicalSecondCycleResult, assert_acceptance

def test_acceptance_passes_second_cycle() -> None:
    r = StableLatestCanonicalSecondCycleResult(second_cycle_confirmed=True, initial_latest_canonical_hash="old", final_latest_canonical_hash="new", latest_hash_changed_after_publish=True, stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_no_pointer_change() -> None:
    r = StableLatestCanonicalSecondCycleResult(second_cycle_confirmed=True, initial_latest_canonical_hash="same", final_latest_canonical_hash="same", latest_hash_changed_after_publish=False, stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "latest_hash_changed_after_publish" in str(exc)
    else:
        raise AssertionError("Second cycle must update the latest pointer hash")

def test_acceptance_rejects_wildcard_selection() -> None:
    r = StableLatestCanonicalSecondCycleResult(second_cycle_confirmed=True, initial_latest_canonical_hash="old", final_latest_canonical_hash="new", latest_hash_changed_after_publish=True, stable_latest_source_used=True, latest_canonical_source_exists=True, latest_canonical_source_is_canonical_report=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, wildcard_source_selection_used=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "wildcard_source_selection_used" in str(exc)
    else:
        raise AssertionError("Wildcard selection must fail L26.13D acceptance")
