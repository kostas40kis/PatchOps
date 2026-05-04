from __future__ import annotations

import json

from patchops.edge_rpa.edge_requested_chat_diagnostic import (
    RequestedChatDiagnosticResult,
    REQUESTED_CHAT_URL,
    assert_l26_10b_acceptance,
    classify_node,
)


def test_requested_chat_url_constant_is_conversation_link() -> None:
    assert REQUESTED_CHAT_URL.startswith("https://chatgpt.com/")
    assert "/c/" in REQUESTED_CHAT_URL


def test_node_classifier_finds_prompt_textarea_without_logging_text() -> None:
    kind, score, chrome = classify_node("Edit", "ProseMirror ProseMirror-focused", "Chat with ChatGPT", "prompt-textarea", depth=14, in_page_scope=True)
    assert kind == "composer_prompt_textarea"
    assert score >= 140
    assert chrome is False


def test_node_classifier_filters_omnibox() -> None:
    kind, score, chrome = classify_node("Edit", "OmniboxViewViews", "Address and search bar", "view_123", depth=3, in_page_scope=False)
    assert kind == "browser_chrome"
    assert score == 0
    assert chrome is True


def test_payload_json_safe() -> None:
    result = RequestedChatDiagnosticResult(target_url_hash="abc", diagnostic_classification="chatgpt_loaded_no_composer_found")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "target_url_hash" in encoded
    assert "conversation_text_logged" in encoded


def test_acceptance_passes_completed_no_upload_diagnostic() -> None:
    result = RequestedChatDiagnosticResult(
        target_url_is_requested_chat=True,
        diagnostic_completed=True,
        controlled_navigation_attempted=True,
        navigation_json_written=True,
        edge_window_attached=True,
        bounded_tree_scanned=True,
        controls_scanned=10,
        diagnostic_classification="chatgpt_loaded_no_composer_found",
        recommended_next_patch="increase_settle_or_add_requested_chat_specific_selector_scan",
        result="PASS",
    )
    assert_l26_10b_acceptance(result)


def test_acceptance_rejects_upload_or_prompt_actions() -> None:
    result = RequestedChatDiagnosticResult(
        target_url_is_requested_chat=True,
        diagnostic_completed=True,
        controlled_navigation_attempted=True,
        navigation_json_written=True,
        edge_window_attached=True,
        bounded_tree_scanned=True,
        controls_scanned=10,
        diagnostic_classification="chatgpt_loaded_no_composer_found",
        recommended_next_patch="increase_settle_or_add_requested_chat_specific_selector_scan",
        report_upload_attempted=True,
        result="PASS",
    )
    try:
        assert_l26_10b_acceptance(result)
    except AssertionError as exc:
        assert "report_upload_attempted" in str(exc)
    else:
        raise AssertionError("Report upload must fail L26.10B acceptance")
