from patchops.edge_rpa.edge_l26_12x_generated_artifact_candidate_diff_filter import GeneratedArtifactCandidateDiffResult, assert_acceptance

def test_acceptance_passes_even_with_zero_novel_candidates() -> None:
    r = GeneratedArtifactCandidateDiffResult(baseline_scan_completed=True, baseline_candidate_count=2, baseline_fingerprints_recorded=True, upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, post_candidate_count=2, known_candidate_count=2, novel_candidate_count=0, novel_candidate_fingerprints_recorded=True, novel_candidate_rect_hashes_recorded=True, novel_candidate_control_types_recorded=True, result="PASS")
    assert_acceptance(r)

def test_acceptance_rejects_candidate_click() -> None:
    r = GeneratedArtifactCandidateDiffResult(baseline_scan_completed=True, baseline_fingerprints_recorded=True, upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, novel_candidate_fingerprints_recorded=True, novel_candidate_rect_hashes_recorded=True, novel_candidate_control_types_recorded=True, candidate_click_performed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate clicks must fail L26.12X acceptance")

def test_acceptance_rejects_click_permission() -> None:
    r = GeneratedArtifactCandidateDiffResult(baseline_scan_completed=True, baseline_fingerprints_recorded=True, upload_submit_idle_result="PASS", uploaded_report_count=1, uploaded_safe_copy_hash_matches_inner_report=True, chatgpt_submit_performed=True, ready_for_next_probe=True, post_scan_completed=True, novel_candidate_fingerprints_recorded=True, novel_candidate_rect_hashes_recorded=True, novel_candidate_control_types_recorded=True, generated_candidate_click_allowed=True, result="PASS")
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "generated_candidate_click_allowed" in str(exc)
    else:
        raise AssertionError("Click permission must be disabled in L26.12X")
