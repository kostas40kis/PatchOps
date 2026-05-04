from __future__ import annotations

import json

from patchops.edge_rpa.edge_session_classifier import (
    ChatGptSessionClassificationResult,
    SessionIndicator,
    assert_l26_05_acceptance,
    classify_text,
)


def test_classify_text_detects_challenge_login_accessible() -> None:
    assert classify_text("Verify you are human Cloudflare")[0] == "challenge"
    assert classify_text("Sign in to continue")[0] == "login"
    assert classify_text("ChatGPT New chat")[0] == "accessible"
    assert classify_text("plain browser chrome")[0] == "none"


def test_payload_is_json_safe() -> None:
    result = ChatGptSessionClassificationResult(
        indicators=(SessionIndicator(0, "Button", "", "Sign in", "abc", 7, "login", 80),)
    )
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "indicators" in encoded
    assert "conversation_text_logged" in encoded


def test_acceptance_policy_passes_for_accessible_classification() -> None:
    result = ChatGptSessionClassificationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused=True,
        edge_window_title_read=True,
        title_mentions_chatgpt=True,
        indicator_scan_completed=True,
        accessible_indicator_found=True,
        chatgpt_session_classified=True,
        classification="accessible",
        result="PASS",
    )
    assert_l26_05_acceptance(result)


def test_acceptance_policy_passes_for_challenge_as_classified_stop() -> None:
    result = ChatGptSessionClassificationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused=True,
        edge_window_title_read=True,
        indicator_scan_completed=True,
        challenge_indicator_found=True,
        chatgpt_session_classified=True,
        classification="human_challenge_required",
        human_challenge_required=True,
        loop_stopped=True,
        result="PASS",
    )
    assert_l26_05_acceptance(result)


def test_acceptance_policy_rejects_navigation_or_prompt_submit() -> None:
    result = ChatGptSessionClassificationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused=True,
        edge_window_title_read=True,
        indicator_scan_completed=True,
        chatgpt_session_classified=True,
        classification="accessible",
        browser_navigation_performed=True,
        result="PASS",
    )
    try:
        assert_l26_05_acceptance(result)
    except AssertionError as exc:
        assert "browser_navigation_performed" in str(exc)
    else:
        raise AssertionError("navigation must remain forbidden in L26.5")
