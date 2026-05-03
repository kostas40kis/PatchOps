from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_download_workflow_final_acceptance_marker as l18_07

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-download-workflow-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-download-workflow-broad-checkpoint"

PASSIVE_FALSE_FIELDS = (
    "downloaded_file_validation_active",
    "downloaded_file_validation_performed",
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "downloaded_file_bytes_read",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
    "real_page_inspection_performed",
    "live_browser_artifact_detection_active",
    "live_browser_artifact_detection_performed",
    "live_browser_download_workflow_active",
    "live_browser_download_workflow_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "selenium_required",
    "selenium_imported_by_readback",
    "cdp_used",
    "remote_debugging_port_used",
    "browser_session_created",
    "driver_created",
    "dom_scraping_performed",
    "prompt_text_extraction_performed",
    "conversation_reading_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "localhost_patchops_server_started",
    "browser_extension_used",
    "git_commit_executed",
    "git_push_executed",
)


def _assert_passive(payload: dict) -> None:
    for field in PASSIVE_FALSE_FIELDS:
        assert payload[field] is False, field


def test_l18_07_builds_final_acceptance_marker() -> None:
    payload = l18_07.build_edge_download_workflow_final_acceptance_marker(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L18.7"
    assert payload["source_patch"] == "L18.6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l18_6_broad_checkpoint_accepted"] is True
    assert payload["l18_1_through_l18_6_remain_accepted"] is True
    assert payload["l18_download_workflow_stream_complete"] is True
    assert payload["download_workflow_stream_completion_is_metadata_only"] is True
    assert payload["metadata_only_download_readiness_proof_accepted"] is True
    assert payload["download_metadata_classification_validated"] is True
    assert payload["downloaded_file_validation_is_next_separate_stream"] is True
    assert payload["real_browser_download_remains_inactive"] is True
    assert payload["pasteback_remains_inactive"] is True
    assert payload["package_run_from_browser_remains_inactive"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["remaining_l18_patches"] == []
    assert payload["next_patch"] == "L19.1 Microsoft Edge downloaded-file validation passive preflight gate"
    _assert_passive(payload)


def test_l18_07_cli_compact_json_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--target-url",
            "https://chatgpt.com/",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 90000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L18.7"
    assert payload["l18_download_workflow_stream_complete"] is True
    assert payload["downloaded_file_validation_is_next_separate_stream"] is True
    _assert_passive(payload)


def test_l18_07_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l18_07.build_edge_download_workflow_final_acceptance_marker(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l18_6_broad_checkpoint_accepted"] is False
    assert payload["l18_download_workflow_stream_complete"] is False
    _assert_passive(payload)


def test_l18_07_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l18_07_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_download_workflow_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L18.7 Microsoft Edge download workflow final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "final acceptance marker",
        "L18.1 through L18.6 remain accepted",
        "L18 download workflow stream complete",
        "metadata-only download readiness proof accepted",
        "download workflow stream completion is metadata-only",
        "real browser download remains inactive",
        "downloaded-file validation is the next separate stream",
        "pasteback remains inactive",
        "package-run from browser remains inactive",
        "live browser download workflow remains inactive",
        "download workflow execution allowed: false",
        "download workflow active: false",
        "download is not performed",
        "downloaded file bytes are not read",
        "download staging directory is not created",
        "artifact content reading performed: false",
        "PatchOps remains source of truth",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be selected but not opened",
        "dedicated Microsoft Edge runtime profile remains required for future live phases",
        "never use the default Microsoft Edge profile",
        "no Microsoft Edge start",
        "no Selenium import",
        "no CDP use",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L19.1 Microsoft Edge downloaded-file validation passive preflight gate",
    ]:
        assert phrase in text
