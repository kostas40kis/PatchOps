from patchops.edge_rpa.edge_l26_14g_seeded_picker_bridge_canonical_cycle import SeededPickerBridgeCanonicalCycleResult, assert_acceptance

def test_acceptance_passes_seeded_picker_bridge() -> None:
    r = SeededPickerBridgeCanonicalCycleResult(seeded_bridge_count=3, seeded_bridge_dirs_recorded=True, primary_bridge_dir_path="C:/bridge", seed_copy_count=3, seed_copy_hashes_match=True, upstream_publish_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_primary_bridge=True, current_canonical_report_created=True, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_unseeded_cycle() -> None:
    r = SeededPickerBridgeCanonicalCycleResult(seeded_bridge_count=0, seeded_bridge_dirs_recorded=True, seed_copy_count=0, seed_copy_hashes_match=True, upstream_publish_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_primary_bridge=True, current_canonical_report_created=True, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "seeded_bridge_count_positive" in str(exc)
    else:
        raise AssertionError("Seeded bridge count must be required")

def test_acceptance_rejects_candidate_click() -> None:
    r = SeededPickerBridgeCanonicalCycleResult(seeded_bridge_count=3, seeded_bridge_dirs_recorded=True, primary_bridge_dir_path="C:/bridge", seed_copy_count=3, seed_copy_hashes_match=True, upstream_publish_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, uploaded_safe_copy_parent_matches_primary_bridge=True, current_canonical_report_created=True, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", selected_candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14G acceptance")
