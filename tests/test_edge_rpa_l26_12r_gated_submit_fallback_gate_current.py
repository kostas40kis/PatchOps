from patchops.edge_rpa.edge_l26_12r_gated_submit_fallback_gate import GatedSubmitFallbackResult, assert_acceptance

def test_acceptance_passes_coordinate_fallback_submit() -> None:
    r = GatedSubmitFallbackResult(allow_chatgpt_submit=True, picker_confirmed_upload_accepted=True, escape_sent_before_submit=True, coordinate_fallback_used=True, coordinate_click_performed=True, coordinate_click_target_hash="h", submit_invocation_completed=True, chatgpt_submit_performed=True, submit_method="edge_window_lower_right_coordinate_click", post_submit_wait_completed=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_missing_gate() -> None:
    r = GatedSubmitFallbackResult(allow_chatgpt_submit=False, picker_confirmed_upload_accepted=True, escape_sent_before_submit=True, coordinate_fallback_used=True, coordinate_click_performed=True, coordinate_click_target_hash="h", submit_invocation_completed=True, chatgpt_submit_performed=True, submit_method="edge_window_lower_right_coordinate_click", post_submit_wait_completed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "allow_chatgpt_submit" in str(exc)
    else:
        raise AssertionError("Submit gate must be required")
