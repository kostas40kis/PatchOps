from __future__ import annotations

import json

from patchops.edge_rpa.edge_composer_detector import ComposerCandidate, ComposerDetectorResult, assert_l26_06_acceptance, normalize_candidates


def make_candidate(**overrides):
    base = dict(index=0, depth=8, control_type="Edit", class_name="Textfield", name_redacted="", name_hash="abc", name_length=0, automation_id_redacted="", rectangle="L0 T0 R0 B0", candidate_kind="in_page_text_surface_candidate", candidate_score=70, is_browser_chrome=False, is_in_page_scope=True, exclusion_reason="")
    base.update(overrides)
    return ComposerCandidate(**base)


def test_payload_json_safe_for_dict_candidates_after_round_trip() -> None:
    candidate = make_candidate()
    payload = ComposerDetectorResult(candidates=(candidate,), filtered_candidates=(make_candidate(is_browser_chrome=True, candidate_kind="browser_chrome_filtered"),)).to_payload()
    rebuilt = ComposerDetectorResult(**payload)
    encoded = json.dumps(rebuilt.to_payload(), sort_keys=True)
    assert "in_page_text_surface_candidate" in encoded
    assert normalize_candidates(rebuilt.candidates)[0].is_in_page_scope is True


def test_acceptance_passes_with_in_page_scope_and_chrome_filtered() -> None:
    result = ComposerDetectorResult(targeted_sequence_completed=True, classification="accessible", chatgpt_accessible=True, composer_scan_completed=True, candidate_report_written=True, controls_scanned=12, browser_chrome_candidates_filtered=True, root_web_area_found=True, in_page_scope_confirmed=True, in_page_candidate_count=1, candidate_count=1, candidates=(make_candidate(),), result="PASS")
    assert_l26_06_acceptance(result)


def test_acceptance_rejects_top_browser_chrome_candidate() -> None:
    result = ComposerDetectorResult(targeted_sequence_completed=True, classification="accessible", chatgpt_accessible=True, composer_scan_completed=True, candidate_report_written=True, controls_scanned=12, browser_chrome_candidates_filtered=True, in_page_scope_confirmed=True, top_candidate_is_browser_chrome=True, result="PASS")
    try:
        assert_l26_06_acceptance(result)
    except AssertionError as exc:
        assert "top_candidate_is_browser_chrome" in str(exc)
    else:
        raise AssertionError("browser chrome top candidate must fail L26.6B acceptance")


def test_acceptance_rejects_text_entry_or_clicks() -> None:
    result = ComposerDetectorResult(targeted_sequence_completed=True, classification="accessible", chatgpt_accessible=True, composer_scan_completed=True, candidate_report_written=True, browser_chrome_candidates_filtered=True, in_page_scope_confirmed=True, controls_scanned=5, prompt_text_entered=True, result="PASS")
    try:
        assert_l26_06_acceptance(result)
    except AssertionError as exc:
        assert "prompt_text_entered" in str(exc)
    else:
        raise AssertionError("text entry must fail L26.6B acceptance")
