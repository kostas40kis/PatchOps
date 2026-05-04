from patchops.edge_rpa.edge_l26_12q_gated_send_gate import GatedSendResult, assert_acceptance

def test_acceptance_passes_gated_send() -> None:
    r = GatedSendResult(allow_chatgpt_submit=True, picker_confirmed_upload_accepted=True, send_button_found=True, send_button_clicked=True, send_button_candidate_hash="h", send_button_candidate_control_type="Button", chatgpt_submit_performed=True, submit_method="uia_send_button_click", send_invocation_completed=True, post_send_wait_completed=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_missing_submit_permission() -> None:
    r = GatedSendResult(allow_chatgpt_submit=False, picker_confirmed_upload_accepted=True, send_button_found=True, send_button_clicked=True, send_button_candidate_hash="h", send_button_candidate_control_type="Button", chatgpt_submit_performed=True, submit_method="uia_send_button_click", send_invocation_completed=True, post_send_wait_completed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "allow_chatgpt_submit" in str(exc)
    else:
        raise AssertionError("Submit permission must be required")
