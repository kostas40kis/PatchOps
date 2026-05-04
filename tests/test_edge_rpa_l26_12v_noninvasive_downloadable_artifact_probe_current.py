from patchops.edge_rpa.edge_l26_12v_noninvasive_downloadable_artifact_probe import NoninvasiveArtifactProbeResult, assert_acceptance

def test_acceptance_passes_no_candidates() -> None:
    r = NoninvasiveArtifactProbeResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, artifact_probe_started=True, artifact_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, artifact_candidate_count=0, candidate_hashes_recorded=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_download_click() -> None:
    r = NoninvasiveArtifactProbeResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, artifact_probe_started=True, artifact_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, artifact_candidate_count=1, candidate_hashes_recorded=True, download_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "download_click_performed" in str(exc)
    else:
        raise AssertionError("Download clicks must fail L26.12V acceptance")

def test_acceptance_rejects_content_logging() -> None:
    r = NoninvasiveArtifactProbeResult(upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, artifact_probe_started=True, artifact_probe_completed=True, edge_window_found_for_probe=True, scanned_control_count=100, candidate_hashes_recorded=True, conversation_text_logged=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "conversation_text_logged" in str(exc)
    else:
        raise AssertionError("Conversation logging must fail L26.12V acceptance")
