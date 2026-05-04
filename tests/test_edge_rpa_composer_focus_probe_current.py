from __future__ import annotations

import json

from patchops.edge_rpa.edge_composer_focus_probe import ComposerFocusProbeResult, FocusCandidate, assert_l26_07_acceptance, _score_focus_candidate


def test_focus_candidate_scoring_accepts_prompt_textarea_and_rejects_buttons() -> None:
    kind, score = _score_focus_candidate("Edit", "ProseMirror ProseMirror-focused", "Chat with ChatGPT", "prompt-textarea", 14, True, False)
    assert kind != "none"
    assert score >= 200
    kind, score = _score_focus_candidate("Button", "composer-btn", "Start dictation", "", 14, True, False)
    assert kind == "none"
    assert score == 0


def test_payload_json_safe() -> None:
    candidate = FocusCandidate(14, "Edit", "ProseMirror", "Chat with ChatGPT", "abc", 17, "prompt-textarea", "L0 T0 R1 B1", 220, "composer_prompt_textarea_focus_candidate", False, True)
    result = ComposerFocusProbeResult(candidate=candidate)
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "prompt-textarea" in encoded
    assert "keyboard_text_sent" in encoded


def test_acceptance_passes_focus_only_probe() -> None:
    result = ComposerFocusProbeResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        composer_detector_completed=True,
        composer_candidate_found=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        composer_focus_attempted=True,
        focus_call_succeeded=True,
        focus_state_observed=True,
        composer_focus_verified=True,
        focus_probe_report_written=True,
        result="PASS",
    )
    assert_l26_07_acceptance(result)


def test_acceptance_rejects_text_entry_clicks_or_prompt_submit() -> None:
    result = ComposerFocusProbeResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        composer_detector_completed=True,
        composer_candidate_found=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        composer_focus_attempted=True,
        focus_call_succeeded=True,
        focus_state_observed=True,
        composer_focus_verified=True,
        focus_probe_report_written=True,
        keyboard_text_sent=True,
        result="PASS",
    )
    try:
        assert_l26_07_acceptance(result)
    except AssertionError as exc:
        assert "keyboard_text_sent" in str(exc)
    else:
        raise AssertionError("keyboard text must fail L26.7 acceptance")
