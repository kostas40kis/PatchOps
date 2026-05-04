from patchops.edge_rpa.edge_l26_14b_response_readiness_stability_classifier import ResponseReadinessStabilityClassifierResult, assert_acceptance, classify_stability

def test_classifier_marks_stable_idle_response_state() -> None:
    first = {"edge_window_found_for_probe": True, "scanned_control_count": 10, "response_like_candidate_count": 1, "composer_like_candidate_count": 1, "stop_generating_seen": False, "candidate_fingerprints": ["a", "b"]}
    second = {"edge_window_found_for_probe": True, "scanned_control_count": 12, "response_like_candidate_count": 1, "composer_like_candidate_count": 1, "stop_generating_seen": False, "candidate_fingerprints": ["a", "b", "c"]}
    stable, reason, overlap, union, ratio = classify_stability(first, second)
    assert stable is True
    assert reason == "stable_idle_response_state"
    assert overlap == 2
    assert union == 3
    assert ratio >= 600

def test_classifier_rejects_stop_generating() -> None:
    first = {"edge_window_found_for_probe": True, "scanned_control_count": 10, "response_like_candidate_count": 1, "candidate_fingerprints": ["a"]}
    second = {"edge_window_found_for_probe": True, "scanned_control_count": 10, "response_like_candidate_count": 1, "stop_generating_seen": True, "candidate_fingerprints": ["a"]}
    stable, reason, *_ = classify_stability(first, second)
    assert stable is False
    assert reason == "stop_generating_seen"

def test_acceptance_passes_stable_classifier_result() -> None:
    r = ResponseReadinessStabilityClassifierResult(upstream_response_probe_result="PASS", canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, first_probe_completed=True, second_probe_completed=True, edge_window_found_for_probe=True, first_scanned_control_count=10, second_scanned_control_count=12, response_ready_stable=True, response_ready_reason="stable_idle_response_state", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_candidate_click() -> None:
    r = ResponseReadinessStabilityClassifierResult(upstream_response_probe_result="PASS", canonical_cycle_result="PASS", stable_latest_source_used=True, previous_canonical_uploaded=True, uploaded_report_role="canonical_browser_evidence_report", uploaded_report_count=1, current_canonical_report_created=True, latest_canonical_matches_current=True, chatgpt_submit_performed=True, ready_for_next_probe=True, first_probe_completed=True, second_probe_completed=True, edge_window_found_for_probe=True, first_scanned_control_count=10, second_scanned_control_count=12, response_ready_stable=True, response_ready_reason="stable_idle_response_state", candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14B acceptance")
