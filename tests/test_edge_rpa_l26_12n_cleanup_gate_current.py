from __future__ import annotations
from patchops.edge_rpa.edge_l26_12n_cleanup_gate import CleanupResult, assert_acceptance


def test_acceptance_rejects_send() -> None:
    r = CleanupResult(
        upload_result="PASS",
        upload_staging_observed_before_cleanup=True,
        staged_file_name_hash="abc",
        composer_refocused_for_cleanup=True,
        cleanup_ctrl_a_backspace_sent=True,
        cleanup_attempted=True,
        cleanup_preserved_staged_attachment=True,
        send_submit_performed=True,
        result="PASS",
    )
    try:
        assert_acceptance(r)
    except AssertionError as exc:
        assert "send_submit_performed" in str(exc)
    else:
        raise AssertionError("Send must fail acceptance")


def test_acceptance_passes_cleanup_preserved_attachment() -> None:
    r = CleanupResult(
        upload_result="PASS",
        upload_staging_observed_before_cleanup=True,
        staged_file_name_hash="abc",
        composer_refocused_for_cleanup=True,
        cleanup_ctrl_a_backspace_sent=True,
        cleanup_attempted=True,
        cleanup_preserved_staged_attachment=True,
        result="PASS",
    )
    assert_acceptance(r)
