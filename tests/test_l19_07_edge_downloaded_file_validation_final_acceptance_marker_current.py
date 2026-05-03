from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_final_acceptance_marker as l19_07

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-validation-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-validation-broad-checkpoint"

PASSIVE_FALSE_FIELDS = (
    "real_filesystem_validation_active",
    "real_file_existence_check_active",
    "real_file_stat_active",
    "real_file_hash_active",
    "archive_validation_active",
    "controlled_downloaded_file_validation_execution_allowed",
    "downloaded_file_metadata_validation_execution_allowed",
    "downloaded_file_metadata_validation_active",
    "downloaded_file_validation_execution_allowed",
    "downloaded_file_validation_active",
    "downloaded_file_validation_performed",
    "downloaded_file_exists_check_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
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


def test_l19_07_builds_final_acceptance_marker() -> None:
    payload = l19_07.build_edge_downloaded_file_validation_final_acceptance_marker(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L19.7"
    assert payload["source_patch"] == "L19.6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l19_6_broad_checkpoint_accepted"] is True
    assert payload["l19_1_through_l19_6_remain_accepted"] is True
    assert payload["l19_downloaded_file_validation_stream_complete"] is True
    assert payload["downloaded_file_validation_stream_completion_is_metadata_readback_only"] is True
    assert payload["metadata_only_downloaded_file_validation_proof_accepted"] is True
    assert payload["downloaded_file_metadata_validation_ready_from_positive_metadata"] is True
    assert payload["real_filesystem_validation_remains_inactive"] is True
    assert payload["real_file_existence_check_remains_inactive"] is True
    assert payload["real_file_stat_remains_inactive"] is True
    assert payload["real_file_hash_remains_inactive"] is True
    assert payload["archive_validation_remains_inactive"] is True
    assert payload["pasteback_remains_inactive"] is True
    assert payload["package_run_from_browser_remains_inactive"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["remaining_l19_patches"] == []
    assert payload["next_patch"] == "L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate"
    _assert_passive(payload)


def test_l19_07_source_summary_remains_safe() -> None:
    payload = l19_07.build_edge_downloaded_file_validation_final_acceptance_marker(PROJECT_ROOT)
    source = payload["source_l19_6_summary"]

    assert source["ok"] is True
    assert source["patch"] == "L19.6"
    assert source["l19_6_complete"] is True
    assert source["l19_1_through_l19_5_remain_accepted"] is True
    assert source["metadata_only_downloaded_file_validation_proof_remains_accepted"] is True
    assert source["downloaded_file_metadata_validation_ready_from_positive_metadata"] is True
    assert source["downloaded_file_validation_execution_allowed"] is False
    assert source["downloaded_file_validation_active"] is False
    assert source["downloaded_file_validation_performed"] is False
    assert source["downloaded_file_exists_check_performed"] is False
    assert source["downloaded_file_stat_performed"] is False
    assert source["downloaded_file_hash_performed"] is False
    assert source["downloaded_file_bytes_read"] is False
    assert source["downloaded_archive_opened"] is False
    assert source["downloaded_archive_contents_listed"] is False
    assert source["downloaded_archive_extracted"] is False
    assert source["downloaded_manifest_read"] is False
    assert source["browser_started"] is False
    assert source["edge_process_started"] is False
    assert source["package_run_performed_by_adapter"] is False


def test_l19_07_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L19.7"
    assert payload["l19_downloaded_file_validation_stream_complete"] is True
    assert payload["downloaded_file_validation_stream_completion_is_metadata_readback_only"] is True
    assert payload["real_filesystem_validation_active"] is False
    assert payload["downloaded_file_validation_execution_allowed"] is False
    assert payload["downloaded_file_validation_active"] is False
    assert payload["downloaded_file_validation_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l19_07_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l19_07.build_edge_downloaded_file_validation_final_acceptance_marker(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l19_6_broad_checkpoint_accepted"] is False
    assert payload["l19_downloaded_file_validation_stream_complete"] is False
    _assert_passive(payload)


def test_l19_07_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l19_07_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_validation_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L19.7 Microsoft Edge downloaded-file validation final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file validation final acceptance marker",
        "L19.1 through L19.6 remain accepted",
        "L19 downloaded-file validation stream complete",
        "downloaded-file validation stream completion is metadata/readback-only",
        "metadata-only downloaded-file validation proof accepted",
        "real filesystem validation remains inactive",
        "real file existence check remains inactive",
        "real file stat remains inactive",
        "real file hash remains inactive",
        "archive validation remains inactive",
        "manifest read remains inactive",
        "file-byte read remains inactive",
        "pasteback remains inactive",
        "package-run from browser remains inactive",
        "downloaded-file validation execution allowed: false",
        "downloaded-file validation active: false",
        "downloaded-file validation is not performed",
        "downloaded file existence check is not performed",
        "downloaded file stat is not performed",
        "downloaded file hash is not performed",
        "downloaded file bytes are not read",
        "downloaded archive is not opened",
        "downloaded archive contents are not listed",
        "downloaded archive is not extracted",
        "downloaded manifest is not read",
        "download workflow remains inactive",
        "real browser download remains inactive",
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
        "no click/download/file-read/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate",
    ]:
        assert phrase in text
