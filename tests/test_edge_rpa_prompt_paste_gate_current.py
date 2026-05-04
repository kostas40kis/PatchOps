from __future__ import annotations

import json

from patchops.edge_rpa.edge_prompt_paste_gate import PromptPasteGateResult, assert_l26_09_acceptance, build_l26_09_prompt


def test_prompt_builder_is_bounded_and_contains_frontier() -> None:
    prompt = build_l26_09_prompt()
    assert "L26.8 accepted" in prompt
    assert "L26.10" in prompt
    assert "--allow-send" in prompt
    assert len(prompt) > 200
    assert len(prompt) < 5000


def test_payload_json_safe_without_prompt_text() -> None:
    result = PromptPasteGateResult(prompt_hash="abc", prompt_length=1234)
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "prompt_hash" in encoded
    assert "prompt_text_logged" in encoded
    assert "You are continuing" not in encoded


def test_acceptance_passes_prompt_paste_gate() -> None:
    result = PromptPasteGateResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        focus_probe_completed=True,
        composer_focus_verified=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        prompt_built=True,
        prompt_hash_recorded=True,
        prompt_hash="abc",
        prompt_length=900,
        allow_paste_gate_enabled=True,
        clipboard_backup_captured=True,
        clipboard_prompt_set=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        clipboard_restored=True,
        result="PASS",
    )
    assert_l26_09_acceptance(result)


def test_acceptance_rejects_send_or_prompt_logging() -> None:
    result = PromptPasteGateResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        focus_probe_completed=True,
        composer_focus_verified=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        prompt_built=True,
        prompt_hash_recorded=True,
        prompt_hash="abc",
        prompt_length=900,
        allow_paste_gate_enabled=True,
        clipboard_backup_captured=True,
        clipboard_prompt_set=True,
        prompt_pasted=True,
        prompt_observed_by_copyback=True,
        copyback_hash_matches_prompt=True,
        prompt_cleared=True,
        clipboard_restored=True,
        send_submit_performed=True,
        result="PASS",
    )
    try:
        assert_l26_09_acceptance(result)
    except AssertionError as exc:
        assert "send_submit_performed" in str(exc)
    else:
        raise AssertionError("send must fail L26.9 acceptance")
