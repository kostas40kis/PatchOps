from patchops.edge_rpa.edge_l26_14c_response_action_candidate_selector_dry_run import ResponseActionCandidateSelectorDryRunResult, assert_acceptance, _rank_candidate

def test_rank_prefers_copy_like_button() -> None:
    rank, kind = _rank_candidate("Button", "Copy", "", "", True)
    assert rank >= 90
    assert kind == "copy_like_response_action"

def test_rank_has_composer_fallback() -> None:
    rank, kind = _rank_candidate("Edit", "Message", "", "", True)
    assert rank > 0
    assert kind == "composer_or_response_surface"

def test_acceptance_passes_dry_run_selection() -> None:
    r = ResponseActionCandidateSelectorDryRunResult(upstream_stability_result="PASS", response_ready_stable=True, canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, selector_started=True, selector_completed=True, edge_window_found_for_selector=True, selector_scanned_control_count=100, candidate_inventory_count=3, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_rank=95, selected_candidate_fingerprint="abc", selected_candidate_rect_hash="rect", selected_candidate_control_type="Button", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_selected_candidate_click() -> None:
    r = ResponseActionCandidateSelectorDryRunResult(upstream_stability_result="PASS", response_ready_stable=True, canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, selector_started=True, selector_completed=True, edge_window_found_for_selector=True, selector_scanned_control_count=100, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_rank=95, selected_candidate_fingerprint="abc", selected_candidate_rect_hash="rect", selected_candidate_control_type="Button", selected_candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Selector dry run must reject any candidate click")
