from patchops.edge_rpa.edge_l26_14e_picker_remembered_directory_bridge import PickerRememberedDirectoryBridgeResult, assert_acceptance

def test_acceptance_passes_picker_bridge() -> None:
    r = PickerRememberedDirectoryBridgeResult(upload_bridge_dir_used=True, upload_bridge_dir_path="C:/dev/patchops/data/runtime/edge_upload_short/s_1", uploaded_safe_copy_parent_matches_bridge=True, visible_attachment_gate_passed=True, attachment_visible_before_submit=True, attachment_signal_count_before_submit=1, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_wrong_parent() -> None:
    r = PickerRememberedDirectoryBridgeResult(upload_bridge_dir_used=True, upload_bridge_dir_path="C:/bridge", uploaded_safe_copy_parent_matches_bridge=False, visible_attachment_gate_passed=True, attachment_visible_before_submit=True, attachment_signal_count_before_submit=1, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "uploaded_safe_copy_parent_matches_bridge" in str(exc)
    else:
        raise AssertionError("Upload copy must be in the bridge directory")

def test_acceptance_rejects_missing_visible_attachment() -> None:
    r = PickerRememberedDirectoryBridgeResult(upload_bridge_dir_used=True, upload_bridge_dir_path="C:/bridge", uploaded_safe_copy_parent_matches_bridge=True, visible_attachment_gate_passed=True, attachment_visible_before_submit=False, attachment_signal_count_before_submit=0, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "attachment_visible_before_submit" in str(exc)
    else:
        raise AssertionError("Visible attachment is required")
