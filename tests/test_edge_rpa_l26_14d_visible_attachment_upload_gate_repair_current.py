from patchops.edge_rpa.edge_l26_14d_visible_attachment_upload_gate_repair import VisibleAttachmentUploadGateRepairResult, assert_acceptance

def test_acceptance_passes_visible_attachment_gate() -> None:
    r = VisibleAttachmentUploadGateRepairResult(upload_source_is_canonical=True, attachment_source_basename="canonical_visible_attachment_1.txt", attachment_source_basename_hash="h", uploaded_safe_copy_path="C:/short/canonical_visible_attachment_1.txt", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, attachment_visible_before_submit=True, attachment_signal_count_before_submit=1, visible_attachment_gate_passed=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_started=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_no_visible_attachment() -> None:
    r = VisibleAttachmentUploadGateRepairResult(upload_source_is_canonical=True, attachment_source_basename="canonical_visible_attachment_1.txt", attachment_source_basename_hash="h", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, attachment_visible_before_submit=False, attachment_signal_count_before_submit=0, visible_attachment_gate_passed=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_started=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "attachment_visible_before_submit" in str(exc)
    else:
        raise AssertionError("Visible attachment proof is required")

def test_acceptance_rejects_candidate_click() -> None:
    r = VisibleAttachmentUploadGateRepairResult(upload_source_is_canonical=True, attachment_source_basename="canonical_visible_attachment_1.txt", attachment_source_basename_hash="h", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, attachment_visible_before_submit=True, attachment_signal_count_before_submit=1, visible_attachment_gate_passed=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, selector_started=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", selected_candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14D acceptance")
