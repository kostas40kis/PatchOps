from __future__ import annotations

import json

from patchops.edge_rpa.edge_targeted_session_classifier import TargetedChatGptClassificationResult, assert_l26_05a_acceptance


def test_payload_is_json_safe() -> None:
    result = TargetedChatGptClassificationResult(classification="accessible")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "classification" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_accessible_targeted_classification() -> None:
    result = TargetedChatGptClassificationResult(
        navigation_invoked=True,
        navigation_result="PASS",
        navigation_classification="accessible_or_loaded",
        session_classifier_invoked=True,
        chatgpt_session_classified=True,
        classification="accessible",
        target_chatgpt_confirmed=True,
        unknown_classification_rejected=True,
        targeted_sequence_completed=True,
        result="PASS",
    )
    assert_l26_05a_acceptance(result)


def test_acceptance_passes_known_stop_state() -> None:
    result = TargetedChatGptClassificationResult(
        navigation_invoked=True,
        session_classifier_invoked=True,
        chatgpt_session_classified=True,
        classification="login_required",
        login_required=True,
        loop_stopped=True,
        unknown_classification_rejected=True,
        targeted_sequence_completed=True,
        result="PASS",
    )
    assert_l26_05a_acceptance(result)


def test_acceptance_rejects_unknown_after_targeting() -> None:
    result = TargetedChatGptClassificationResult(
        navigation_invoked=True,
        session_classifier_invoked=True,
        chatgpt_session_classified=True,
        classification="unknown",
        targeted_sequence_completed=True,
        result="PASS",
    )
    try:
        assert_l26_05a_acceptance(result)
    except AssertionError as exc:
        assert "unknown_classification_rejected" in str(exc) or "classification_accessible_or_stop_state" in str(exc)
    else:
        raise AssertionError("unknown classification must fail L26.5A acceptance")


def test_acceptance_rejects_prompt_or_download() -> None:
    result = TargetedChatGptClassificationResult(
        navigation_invoked=True,
        session_classifier_invoked=True,
        chatgpt_session_classified=True,
        classification="accessible",
        unknown_classification_rejected=True,
        targeted_sequence_completed=True,
        chatgpt_prompt_submitted=True,
        result="PASS",
    )
    try:
        assert_l26_05a_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_prompt_submitted" in str(exc)
    else:
        raise AssertionError("prompt submission must fail L26.5A acceptance")
