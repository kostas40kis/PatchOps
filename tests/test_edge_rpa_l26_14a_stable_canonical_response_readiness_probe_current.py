from patchops.edge_rpa.edge_l26_14a_stable_canonical_response_readiness_probe import StableCanonicalResponseReadinessProbeResult, assert_acceptance

def test_acceptance_passes_response_readiness_probe() -> None:
    r = StableCanonicalResponseReadinessProbeResult(canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, response_readiness_probe_started=True, response_readiness_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, candidate_fingerprints_recorded=True, candidate_rect_hashes_recorded=True, candidate_control_types_recorded=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_content_logging() -> None:
    r = StableCanonicalResponseReadinessProbeResult(canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, response_readiness_probe_started=True, response_readiness_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, candidate_fingerprints_recorded=True, candidate_rect_hashes_recorded=True, candidate_control_types_recorded=True, conversation_text_logged=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "conversation_text_logged" in str(exc)
    else:
        raise AssertionError("Conversation text logging must fail L26.14A acceptance")

def test_acceptance_rejects_candidate_click() -> None:
    r = StableCanonicalResponseReadinessProbeResult(canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, response_readiness_probe_started=True, response_readiness_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, candidate_fingerprints_recorded=True, candidate_rect_hashes_recorded=True, candidate_control_types_recorded=True, candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14A acceptance")
