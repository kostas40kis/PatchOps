from patchops.edge_rpa.edge_l26_14h_attachment_detector_false_negative_tolerant_cycle import AttachmentDetectorFalseNegativeTolerantCycleResult, assert_acceptance

def base(**kw):
    d = dict(upload_source_is_canonical=True, uploaded_safe_copy_path="C:/safe.txt", uploaded_safe_copy_hash_matches_source=True, uploaded_safe_copy_drive_valid=True, picker_confirmed_upload_accepted=True, attachment_gate_effective_passed=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, current_canonical_report_created=True, current_canonical_report_path="C:/current.txt", current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    d.update(kw)
    return AttachmentDetectorFalseNegativeTolerantCycleResult(**d)

def test_acceptance_passes_with_visible_attachment() -> None:
    assert_acceptance(base(attachment_visible_before_submit=True, attachment_signal_count_before_submit=1))

def test_acceptance_passes_with_detector_false_negative_fallback() -> None:
    assert_acceptance(base(attachment_visible_before_submit=False, attachment_detector_false_negative_tolerated=True))

def test_acceptance_rejects_no_visible_and_no_fallback() -> None:
    r = base(attachment_visible_before_submit=False, attachment_detector_false_negative_tolerated=False)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "visible_or_detector_fallback" in str(exc)
    else:
        raise AssertionError("Must require visible attachment or explicit detector false-negative fallback")

def test_acceptance_rejects_candidate_click() -> None:
    r = base(attachment_visible_before_submit=True, selected_candidate_click_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14H acceptance")
