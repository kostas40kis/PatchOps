from patchops.edge_rpa.edge_l26_12w_actionable_artifact_candidate_inventory import ActionableArtifactInventoryResult, assert_acceptance

def test_acceptance_passes_actionable_inventory() -> None:
    r = ActionableArtifactInventoryResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, inventory_started=True, inventory_completed=True, edge_window_found_for_inventory=True, scanned_control_count=100, artifact_candidate_count=2, actionable_candidate_count=1, clickable_candidate_count=1, candidate_fingerprints_recorded=True, candidate_fingerprints=["a"], candidate_rect_hashes_recorded=True, candidate_rect_hashes=["r"], candidate_control_types_recorded=True, candidate_control_types=["Hyperlink"], result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_candidate_click() -> None:
    r = ActionableArtifactInventoryResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, inventory_started=True, inventory_completed=True, edge_window_found_for_inventory=True, scanned_control_count=100, artifact_candidate_count=2, actionable_candidate_count=1, candidate_fingerprints_recorded=True, candidate_fingerprints=["a"], candidate_rect_hashes_recorded=True, candidate_rect_hashes=["r"], candidate_control_types_recorded=True, candidate_control_types=["Button"], candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate clicking must fail L26.12W acceptance")

def test_acceptance_rejects_empty_actionable_inventory() -> None:
    r = ActionableArtifactInventoryResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, inventory_started=True, inventory_completed=True, edge_window_found_for_inventory=True, scanned_control_count=100, artifact_candidate_count=0, actionable_candidate_count=0, candidate_fingerprints_recorded=True, candidate_rect_hashes_recorded=True, candidate_control_types_recorded=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "actionable_candidate_count_positive" in str(exc)
    else:
        raise AssertionError("Empty actionable inventory must fail L26.12W acceptance")
