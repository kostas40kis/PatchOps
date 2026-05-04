from __future__ import annotations

import json

from patchops.edge_rpa.edge_prompt_send_gate import PromptSendGateResult, REQUESTED_CHAT_URL, assert_l26_10_acceptance


def test_requested_chat_url_constant_is_conversation_link() -> None:
    assert "/c/" in REQUESTED_CHAT_URL
    assert REQUESTED_CHAT_URL.startswith("https://chatgpt.com/")


def test_payload_json_safe() -> None:
    result = PromptSendGateResult(target_url_hash="abc")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "target_url_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_requested_chat_fallback_gate() -> None:
    result = PromptSendGateResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        classifier_unknown_fallback_used=True,
        composer_fallback_attempted=True,
        composer_fallback_focus_verified=True,
        prompt_paste_cycle_completed=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        prompt_hash="abc",
        prompt_length=900,
        send_gate_evaluated=True,
        send_blocked_by_default=True,
        send_path_disabled=True,
        result="PASS",
    )
    assert_l26_10_acceptance(result)


def test_acceptance_rejects_allow_send_or_submit() -> None:
    result = PromptSendGateResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        classifier_unknown_fallback_used=True,
        composer_fallback_attempted=True,
        composer_fallback_focus_verified=True,
        prompt_paste_cycle_completed=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        prompt_hash="abc",
        prompt_length=900,
        send_gate_evaluated=True,
        send_blocked_by_default=True,
        send_path_disabled=True,
        allow_send_requested=True,
        result="PASS",
    )
    try:
        assert_l26_10_acceptance(result)
    except AssertionError as exc:
        assert "allow_send_requested" in str(exc)
    else:
        raise AssertionError("L26.10A must reject allow-send in disabled-by-default proof")
