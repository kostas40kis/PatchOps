from pathlib import Path
from patchops.edge_rpa.edge_l26_14i_restore_good_canonical_and_strict_upload_gate import RestoreGoodCanonicalAndStrictUploadGateResult, assert_acceptance, canonical_is_good

def test_canonical_is_good_requires_browser_pass(tmp_path: Path) -> None:
    good = tmp_path / "good.txt"
    good.write_text("PATCHOPS CANONICAL BROWSER EVIDENCE REPORT\nPATCHOPS APPLY EVIDENCE\nBROWSER LIVE PROOF SUMMARY\nvisible_attachment_gate_passed: True\nbrowser_live_passed: True\nExitCode : 0\nResult   : PASS\n", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("PATCHOPS CANONICAL BROWSER EVIDENCE REPORT\nPATCHOPS APPLY EVIDENCE\nBROWSER LIVE PROOF SUMMARY\nvisible_attachment_gate_passed: False\nbrowser_live_passed: False\nExitCode : 1\nResult   : FAIL\n", encoding="utf-8")
    assert canonical_is_good(good)
    assert not canonical_is_good(bad)

def base(**kw):
    d = dict(latest_restored_from_good_canonical=True, restored_source_path="C:/good.txt", restored_source_hash="h", strict_visible_gate_required=True, upstream_strict_result="PASS", visible_attachment_gate_passed=True, attachment_visible_before_submit=True, attachment_signal_count_before_submit=1, picker_confirmed_upload_accepted=True, chatgpt_submit_performed=True, idle_observation_completed=True, ready_for_next_probe=True, current_canonical_report_created=True, current_canonical_contains_apply_evidence=True, current_canonical_contains_browser_evidence=True, latest_canonical_pointer_created=True, latest_canonical_matches_current=True, selector_completed=True, candidate_selected=True, selected_candidate_kind="copy_like_response_action", selected_candidate_fingerprint="fp", selected_candidate_rect_hash="rh", result="PASS")
    d.update(kw)
    return RestoreGoodCanonicalAndStrictUploadGateResult(**d)

def test_acceptance_passes_strict_restore_cycle() -> None:
    assert_acceptance(base())

def test_acceptance_rejects_detector_fallback_only() -> None:
    r = base(visible_attachment_gate_passed=False, attachment_visible_before_submit=False, attachment_signal_count_before_submit=0)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "visible_attachment_gate_passed" in str(exc)
    else:
        raise AssertionError("L26.14I must require the strict visible gate")

def test_acceptance_rejects_candidate_click() -> None:
    r = base(selected_candidate_click_performed=True)
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "selected_candidate_click_performed" in str(exc)
    else:
        raise AssertionError("Candidate click must fail L26.14I acceptance")
