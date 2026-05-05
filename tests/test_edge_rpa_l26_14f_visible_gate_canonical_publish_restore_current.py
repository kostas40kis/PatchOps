from patchops.edge_rpa.edge_l26_14f_visible_gate_canonical_publish_restore import VisibleGateCanonicalPublishRestoreResult, assert_acceptance

def test_acceptance_passes_visible_gate_publish_restore() -> None:
    r = VisibleGateCanonicalPublishRestoreResult(upstream_bridge_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_bridge=True, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_report_size_bytes=100, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_path="C:/latest.txt", latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="response_feedback_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_missing_canonical_publish() -> None:
    r = VisibleGateCanonicalPublishRestoreResult(upstream_bridge_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_bridge=True, current_canonical_report_created=False, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="response_feedback_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "current_canonical_report_created" in str(exc)
    else:
        raise AssertionError("Canonical publish must be required")

def test_acceptance_rejects_candidate_click() -> None:
    r = VisibleGateCanonicalPublishRestoreResult(upstream_bridge_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_bridge=True, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_report_size_bytes=100, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_path="C:/latest.txt", latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="response_feedback_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", selected_candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14F acceptance")
