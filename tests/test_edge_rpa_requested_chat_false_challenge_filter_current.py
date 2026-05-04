from __future__ import annotations

import json

from patchops.edge_rpa.edge_requested_chat_false_challenge_filter import RequestedChatFalseChallengeFilterResult, assert_l26_10c_acceptance


def test_payload_json_safe() -> None:
    result = RequestedChatFalseChallengeFilterResult(prompt_hash="abc", prompt_length=900)
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "prompt_hash" in encoded
    assert "chatgpt_prompt_submitted" in encoded


def test_acceptance_passes_false_challenge_filter_gate() -> None:
    result = RequestedChatFalseChallengeFilterResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        safe_composer_focus_candidate_found=True,
        composer_focus_verified=True,
        raw_challenge_terms_seen=True,
        transcript_challenge_terms_filtered=True,
        real_challenge_indicator_found=False,
        requested_chat_accessible_by_composer=True,
        prompt_hash="abc",
        prompt_length=900,
        clipboard_backup_captured=True,
        clipboard_prompt_set=True,
        prompt_paste_cycle_completed=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        clipboard_restored=True,
        send_gate_evaluated=True,
        send_blocked_by_default=True,
        send_path_disabled=True,
        result="PASS",
    )
    assert_l26_10c_acceptance(result)


def test_acceptance_rejects_real_challenge_or_send() -> None:
    result = RequestedChatFalseChallengeFilterResult(
        target_url_is_requested_chat=True,
        requested_chat_navigation_attempted=True,
        requested_chat_navigation_observed=True,
        safe_composer_focus_candidate_found=True,
        composer_focus_verified=True,
        raw_challenge_terms_seen=True,
        transcript_challenge_terms_filtered=True,
        real_challenge_indicator_found=True,
        requested_chat_accessible_by_composer=True,
        prompt_hash="abc",
        prompt_length=900,
        clipboard_backup_captured=True,
        clipboard_prompt_set=True,
        prompt_paste_cycle_completed=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        clipboard_restored=True,
        send_gate_evaluated=True,
        send_blocked_by_default=True,
        send_path_disabled=True,
        result="PASS",
    )
    try:
        assert_l26_10c_acceptance(result)
    except AssertionError as exc:
        assert "real_challenge_indicator_found" in str(exc)
    else:
        raise AssertionError("real challenge must fail L26.10C acceptance")
