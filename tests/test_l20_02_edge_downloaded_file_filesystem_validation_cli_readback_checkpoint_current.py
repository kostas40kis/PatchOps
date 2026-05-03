from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint as l20_02

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-cli-readback-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate"

PASSIVE_FALSE_FIELDS = (
    "filesystem_validation_execution_allowed",
    "filesystem_validation_active",
    "filesystem_validation_performed",
    "real_filesystem_validation_active",
    "real_file_existence_check_active",
    "real_file_stat_active",
    "real_file_hash_active",
    "real_file_exists_check_performed",
    "real_file_stat_performed",
    "real_file_hash_performed",
    "archive_validation_active",
    "archive_validation_performed",
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


def test_l20_02_builds_passive_cli_readback_checkpoint() -> None:
    payload = l20_02.build_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L20.2"
    assert payload["source_patch"] == "L20.1"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l20_1_passive_preflight_gate_accepted"] is True
    assert payload["l20_1_default_compact_readback_ok"] is True
    assert payload["l20_1_authorized_compact_readback_ok"] is True
    assert payload["default_filesystem_validation_preflight_authorized"] is False
    assert payload["authorized_filesystem_validation_preflight_authorized"] is True
    assert payload["filesystem_validation_preflight_authorization_remains_readback_only"] is True
    assert payload["avoid_nested_cli_validation_cascades"] is True
    assert payload["one_shallow_l20_2_compact_cli_smoke"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L20.3 Microsoft Edge downloaded-file filesystem validation passive plan checkpoint"
    _assert_passive(payload)


def test_l20_02_source_readbacks_are_compact_and_passive() -> None:
    payload = l20_02.build_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint(PROJECT_ROOT)
    default = payload["source_default_summary"]
    authorized = payload["source_authorized_summary"]

    assert default["ok"] is True
    assert default["patch"] == "L20.1"
    assert default["filesystem_validation_preflight_authorized"] is False
    assert default["filesystem_validation_execution_allowed"] is False
    assert default["filesystem_validation_active"] is False
    assert default["filesystem_validation_performed"] is False
    assert default["real_filesystem_validation_active"] is False
    assert default["real_file_exists_check_performed"] is False
    assert default["real_file_stat_performed"] is False
    assert default["real_file_hash_performed"] is False
    assert default["downloaded_file_bytes_read"] is False
    assert default["downloaded_archive_opened"] is False
    assert default["downloaded_manifest_read"] is False
    assert default["browser_started"] is False
    assert default["edge_process_started"] is False

    assert authorized["ok"] is True
    assert authorized["patch"] == "L20.1"
    assert authorized["filesystem_validation_preflight_authorized"] is True
    assert authorized["filesystem_validation_execution_allowed"] is False
    assert authorized["filesystem_validation_active"] is False
    assert authorized["filesystem_validation_performed"] is False
    assert authorized["real_filesystem_validation_active"] is False
    assert authorized["real_file_exists_check_performed"] is False
    assert authorized["real_file_stat_performed"] is False
    assert authorized["real_file_hash_performed"] is False
    assert authorized["downloaded_file_bytes_read"] is False
    assert authorized["downloaded_archive_opened"] is False
    assert authorized["downloaded_manifest_read"] is False
    assert authorized["browser_started"] is False
    assert authorized["edge_process_started"] is False


def test_l20_02_cli_compact_json_smoke_is_shallow() -> None:
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
    assert payload["patch"] == "L20.2"
    assert payload["l20_1_default_compact_readback_ok"] is True
    assert payload["l20_1_authorized_compact_readback_ok"] is True
    assert payload["filesystem_validation_execution_allowed"] is False
    assert payload["filesystem_validation_active"] is False
    assert payload["filesystem_validation_performed"] is False
    assert payload["real_file_exists_check_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l20_02_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l20_02.build_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l20_1_authorized_compact_readback_ok"] is False
    _assert_passive(payload)


def test_l20_02_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l20_02_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L20.2 Microsoft Edge downloaded-file filesystem validation CLI/readback checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY",
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file filesystem validation CLI/readback checkpoint",
        "passive CLI/readback checkpoint",
        "L20.1 passive preflight gate remains accepted",
        "default compact readback remains passive",
        "authorized compact readback remains passive",
        "filesystem validation preflight authorization remains readback-only",
        "filesystem validation execution allowed: false",
        "filesystem validation active: false",
        "filesystem validation is not performed",
        "real filesystem validation remains inactive",
        "real file existence check remains inactive",
        "real file stat remains inactive",
        "real file hash remains inactive",
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
        "avoid nested CLI validation cascades",
        "one shallow L20.2 compact CLI smoke",
        "L20.3 Microsoft Edge downloaded-file filesystem validation passive plan checkpoint",
    ]:
        assert phrase in text
