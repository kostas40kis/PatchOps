from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_broad_checkpoint as l19_06

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-validation-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof"

PASSIVE_FALSE_FIELDS = (
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


def test_l19_06_builds_broad_checkpoint() -> None:
    payload = l19_06.build_edge_downloaded_file_validation_broad_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L19.6"
    assert payload["source_patch"] == "L19.5"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l19_1_through_l19_5_remain_accepted"] is True
    assert payload["metadata_only_downloaded_file_validation_proof_remains_accepted"] is True
    assert payload["default_metadata_proof_readback_remains_passive"] is True
    assert payload["authorized_positive_metadata_proof_readback_remains_passive"] is True
    assert payload["negative_metadata_fixture_remains_rejected_without_side_effects"] is True
    assert payload["forbidden_metadata_keys_remain_rejected_without_side_effects"] is True
    assert payload["downloaded_file_metadata_validation_ready_from_positive_metadata"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L19.7 Microsoft Edge downloaded-file validation final acceptance marker"
    _assert_passive(payload)


def test_l19_06_source_summaries_are_compact_and_safe() -> None:
    payload = l19_06.build_edge_downloaded_file_validation_broad_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_positive_summary"]
    negative = payload["negative_metadata_summary"]
    forbidden = payload["forbidden_metadata_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L19.5"
    assert default["downloaded_file_metadata_validation_classification_performed"] is False
    assert default["downloaded_file_metadata_validation_ready"] is False
    assert default["downloaded_file_bytes_read"] is False
    assert default["downloaded_archive_opened"] is False
    assert default["browser_started"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L19.5"
    assert authorized["downloaded_file_metadata_validation_classification_performed"] is True
    assert authorized["downloaded_file_metadata_validation_ready"] is True
    assert authorized["downloaded_file_bytes_read"] is False
    assert authorized["downloaded_archive_opened"] is False
    assert authorized["browser_started"] is False

    assert negative["downloaded_file_metadata_validation_ready"] is False
    assert "candidate_extension_metadata_is_not_zip" in negative["blocking_reasons"]
    assert negative["file_bytes_read"] is False
    assert negative["archive_opened"] is False
    assert negative["package_run_performed"] is False

    assert forbidden["downloaded_file_metadata_validation_ready"] is False
    assert forbidden["forbidden_metadata_keys_present"] == ["file_exists", "file_hash"]
    assert "forbidden_metadata_keys_present" in forbidden["blocking_reasons"]
    assert forbidden["file_bytes_read"] is False
    assert forbidden["archive_opened"] is False
    assert forbidden["package_run_performed"] is False


def test_l19_06_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L19.6"
    assert payload["l19_1_through_l19_5_remain_accepted"] is True
    assert payload["metadata_only_downloaded_file_validation_proof_remains_accepted"] is True
    assert payload["downloaded_file_metadata_validation_ready_from_positive_metadata"] is True
    assert payload["downloaded_file_validation_execution_allowed"] is False
    assert payload["downloaded_file_validation_active"] is False
    assert payload["downloaded_file_validation_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l19_06_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l19_06.build_edge_downloaded_file_validation_broad_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l19_1_through_l19_5_remain_accepted"] is False
    _assert_passive(payload)


def test_l19_06_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l19_06_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_validation_broad_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L19.6 Microsoft Edge downloaded-file validation broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED",
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file validation broad checkpoint",
        "broad passive checkpoint",
        "L19.1 through L19.5 remain accepted",
        "metadata-only downloaded-file validation proof remains accepted",
        "default metadata proof readback remains passive",
        "authorized positive metadata proof readback remains passive",
        "negative metadata fixture remains rejected without side effects",
        "forbidden metadata keys remain rejected without side effects",
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
        "pasteback remains inactive",
        "package-run from browser remains inactive",
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
        "L19.7 Microsoft Edge downloaded-file validation final acceptance marker",
    ]:
        assert phrase in text
