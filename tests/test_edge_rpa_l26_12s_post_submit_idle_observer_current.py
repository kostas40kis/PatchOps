from patchops.edge_rpa.edge_l26_12s_post_submit_idle_observer import PostSubmitIdleObserverResult, assert_acceptance

def test_acceptance_passes_idle_observer_result() -> None:
    r = PostSubmitIdleObserverResult(picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", post_submit_observation_started=True, observe_wait_completed=True, edge_window_found=True, stop_generating_absent_at_end=True, final_control_count=100, idle_observation_completed=True, ready_for_next_probe=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_conversation_logging() -> None:
    r = PostSubmitIdleObserverResult(picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, submit_method="uia_send_button_click", post_submit_observation_started=True, observe_wait_completed=True, edge_window_found=True, stop_generating_absent_at_end=True, final_control_count=100, idle_observation_completed=True, ready_for_next_probe=True, conversation_text_logged=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "conversation_text_logged" in str(exc)
    else:
        raise AssertionError("Conversation text logging must fail acceptance")
