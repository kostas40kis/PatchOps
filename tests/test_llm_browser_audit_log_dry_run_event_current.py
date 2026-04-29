from __future__ import annotations

from pathlib import Path

from patchops.llm_browser.audit_log import event_from_dry_run_result
from patchops.llm_browser.chat_page_contract import snapshot_from_html
from patchops.llm_browser.dry_run_orchestrator import dry_run_orchestrate_once


def _html_with_bundle(filename: str = "patch_d0_25_wire_audit_log_into_cli_patchops_bundle.zip") -> str:
    return f"""
    <article data-message-author-role="assistant">
      <a href="/downloads/{filename}?download=1">{filename}</a>
    </article>
    <textarea id="prompt-textarea"></textarea>
    """


def test_event_from_dry_run_result_is_compact_and_structured() -> None:
    result = dry_run_orchestrate_once(snapshot_from_html(_html_with_bundle()), browser="edge")

    event = event_from_dry_run_result(result, source="unit-test")
    payload = event.to_payload()

    assert payload["event_type"] == "dry_run_result"
    assert payload["source"] == "unit-test"
    assert payload["status"] == "UNKNOWN"
    assert payload["artifact_filename"] == "patch_d0_25_wire_audit_log_into_cli_patchops_bundle.zip"
    assert payload["state"] == "DOWNLOADING"
    assert payload["metadata"]["ok"] is False
    assert payload["metadata"]["blocked"] is False
    assert payload["metadata"]["planned_actions"] == [
        "would_acquire_run_lock",
        "scan_latest_assistant_reply_for_patchops_bundle",
        "would_click_download_candidate_and_wait_for_stable_file",
    ]
    assert payload["metadata"]["side_effects_performed"] == []
    assert "text" not in payload
