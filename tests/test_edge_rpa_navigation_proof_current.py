from __future__ import annotations

import json

from patchops.edge_rpa.edge_navigation_proof import ControlledNavigationResult, NavigationObservation, assert_l26_04_acceptance, validate_target_url


def test_validate_target_url_allows_http_https_only() -> None:
    assert validate_target_url("https://chatgpt.com/") == "https://chatgpt.com/"
    assert validate_target_url("http://example.test/path") == "http://example.test/path"
    for bad in ["javascript:alert(1)", "file:///C:/temp/x", "about:blank", "https:///missing-host"]:
        try:
            validate_target_url(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unsafe URL accepted: {bad}")


def test_payload_is_json_safe() -> None:
    result = ControlledNavigationResult(observations=(NavigationObservation(0, "Before - Microsoft Edge", "abc", 23),))
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "observations" in encoded
    assert "conversation_text_logged" in encoded


def test_acceptance_policy_passes_for_controlled_navigation() -> None:
    result = ControlledNavigationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused_before_navigation=True,
        edge_window_title_before_read=True,
        ctrl_l_sent=True,
        clipboard_url_set=True,
        clipboard_verified_before_paste=True,
        url_pasted_by_patchops=True,
        enter_sent=True,
        normal_edge_navigation=True,
        page_load_state_observed=True,
        edge_window_title_after_read=True,
        title_changed_or_observed=True,
        observations=(NavigationObservation(0, "Before", "a", 6), NavigationObservation(1, "After", "b", 5)),
        result="PASS",
    )
    assert_l26_04_acceptance(result)


def test_acceptance_policy_rejects_prompt_send_or_download() -> None:
    result = ControlledNavigationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused_before_navigation=True,
        edge_window_title_before_read=True,
        ctrl_l_sent=True,
        clipboard_url_set=True,
        clipboard_verified_before_paste=True,
        url_pasted_by_patchops=True,
        enter_sent=True,
        normal_edge_navigation=True,
        page_load_state_observed=True,
        edge_window_title_after_read=True,
        title_changed_or_observed=True,
        chatgpt_prompt_submitted=True,
        result="PASS",
    )
    try:
        assert_l26_04_acceptance(result)
    except AssertionError as exc:
        assert "chatgpt_prompt_submitted" in str(exc)
    else:
        raise AssertionError("prompt submission must fail L26.4 acceptance")


def test_acceptance_policy_rejects_human_challenge() -> None:
    result = ControlledNavigationResult(
        pywinauto_imported=True,
        uia_backend_available=True,
        normal_edge_attached=True,
        edge_focused_before_navigation=True,
        edge_window_title_before_read=True,
        ctrl_l_sent=True,
        clipboard_url_set=True,
        clipboard_verified_before_paste=True,
        url_pasted_by_patchops=True,
        enter_sent=True,
        normal_edge_navigation=True,
        page_load_state_observed=True,
        edge_window_title_after_read=True,
        title_changed_or_observed=True,
        human_challenge_required=True,
        loop_stopped=True,
        result="PASS",
    )
    try:
        assert_l26_04_acceptance(result)
    except AssertionError as exc:
        assert "no_human_challenge_for_acceptance" in str(exc)
    else:
        raise AssertionError("human challenge must stop L26.4 acceptance")
