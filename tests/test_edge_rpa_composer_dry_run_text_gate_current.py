from __future__ import annotations

import json

from patchops.edge_rpa.edge_composer_dry_run_text_gate import ComposerDryRunTextGateResult, assert_l26_08_acceptance


def test_payload_json_safe() -> None:
    result = ComposerDryRunTextGateResult(dry_run_marker_hash="abc", copied_text_hash="def")
    encoded = json.dumps(result.to_payload(), sort_keys=True)
    assert "dry_run_marker_hash" in encoded
    assert "enter_key_sent" in encoded


def test_acceptance_passes_gated_dry_run_text_cycle() -> None:
    result = ComposerDryRunTextGateResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        focus_probe_completed=True,
        composer_focus_verified=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        dry_run_marker_built=True,
        clipboard_backup_captured=True,
        clipboard_dry_run_marker_set=True,
        paste_shortcut_sent=True,
        dry_run_text_observed=True,
        clear_shortcut_sent=True,
        backspace_sent=True,
        dry_run_text_cleared=True,
        clipboard_restored=True,
        result="PASS",
    )
    assert_l26_08_acceptance(result)


def test_acceptance_rejects_enter_or_submit() -> None:
    result = ComposerDryRunTextGateResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        focus_probe_completed=True,
        composer_focus_verified=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        dry_run_marker_built=True,
        clipboard_backup_captured=True,
        clipboard_dry_run_marker_set=True,
        paste_shortcut_sent=True,
        dry_run_text_observed=True,
        clear_shortcut_sent=True,
        backspace_sent=True,
        dry_run_text_cleared=True,
        clipboard_restored=True,
        enter_key_sent=True,
        result="PASS",
    )
    try:
        assert_l26_08_acceptance(result)
    except AssertionError as exc:
        assert "enter_key_sent" in str(exc)
    else:
        raise AssertionError("Enter/send must fail L26.8 acceptance")


def test_acceptance_rejects_uncleared_marker() -> None:
    result = ComposerDryRunTextGateResult(
        targeted_sequence_completed=True,
        classification="accessible",
        chatgpt_accessible=True,
        focus_probe_completed=True,
        composer_focus_verified=True,
        candidate_not_browser_chrome=True,
        candidate_in_page_scope=True,
        dry_run_marker_built=True,
        clipboard_backup_captured=True,
        clipboard_dry_run_marker_set=True,
        paste_shortcut_sent=True,
        dry_run_text_observed=True,
        clear_shortcut_sent=True,
        backspace_sent=True,
        clipboard_restored=True,
        result="PASS",
    )
    try:
        assert_l26_08_acceptance(result)
    except AssertionError as exc:
        assert "dry_run_text_cleared" in str(exc)
    else:
        raise AssertionError("Uncleared dry-run text must fail L26.8 acceptance")
