from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint as l20_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-plan-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-cli-readback-checkpoint"

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


def test_l20_03_builds_passive_plan_checkpoint() -> None:
    payload = l20_03.build_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L20.3"
    assert payload["source_patch"] == "L20.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l20_2_cli_readback_checkpoint_accepted"] is True
    assert payload["l20_2_complete"] is True
    assert payload["l20_1_passive_preflight_gate_accepted"] is True
    assert payload["filesystem_validation_candidate_definition_blocks_l20_3_filesystem_file_read_archive_package_run"] is True
    assert payload["future_filesystem_validation_plan_is_planned_not_executed"] is True
    assert payload["future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate"
    _assert_passive(payload)


def test_l20_03_candidate_definition_blocks_filesystem_execution() -> None:
    definition = l20_03.filesystem_validation_candidate_definition()

    assert "metadata-only path evidence" in definition["candidate_means"]
    assert definition["future_candidate_path_rules"]["extension_must_be"] == ".zip"
    assert definition["future_candidate_path_rules"]["recommended_pattern"] == "patch_*_patchops_bundle.zip"
    assert definition["future_candidate_path_rules"]["path_must_be_metadata_only_in_l20_3"] is True
    assert definition["future_candidate_path_rules"]["path_must_not_be_default_edge_profile"] is True
    assert definition["future_validation_stages"]["existence_check_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["stat_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["hash_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["archive_open_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["archive_listing_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["archive_extract_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["manifest_read_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["file_byte_read_allowed_in_l20_3"] is False
    assert definition["future_validation_stages"]["package_run_allowed_in_l20_3"] is False


def test_l20_03_future_plan_blocks_file_read_archive_package_run() -> None:
    plan = l20_03.future_filesystem_validation_plan()

    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l20_2_cli_readback_checkpoint_accepted"
    assert plan[1]["name"] == "require_l20_4_or_later_explicit_filesystem_validation_authorization_token"
    assert plan[2]["path_metadata_only"] is True
    assert plan[3]["file_exists_check_allowed_in_l20_3"] is False
    assert plan[3]["read_file_bytes"] is False
    assert plan[4]["file_stat_allowed_in_l20_3"] is False
    assert plan[4]["archive_open"] is False
    assert plan[4]["manifest_read"] is False
    assert plan[5]["file_hash_allowed_in_l20_3"] is False
    assert plan[5]["file_byte_read_allowed_in_l20_3"] is False
    assert plan[6]["archive_open_in_l20_3"] is False
    assert plan[6]["archive_listing_in_l20_3"] is False
    assert plan[6]["archive_extract_in_l20_3"] is False
    assert plan[6]["manifest_read_in_l20_3"] is False
    assert plan[6]["package_run_in_l20_3"] is False
    assert plan[-1]["filesystem_validation_execution_allowed"] is False
    assert plan[-1]["real_file_exists_check_performed"] is False
    assert plan[-1]["real_file_stat_performed"] is False
    assert plan[-1]["real_file_hash_performed"] is False
    assert plan[-1]["downloaded_file_bytes_read"] is False
    assert plan[-1]["downloaded_archive_opened"] is False
    assert plan[-1]["downloaded_manifest_read"] is False
    assert plan[-1]["package_run"] is False
    assert plan[-1]["pasteback"] is False
    assert plan[-1]["auto_send"] is False


def test_l20_03_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L20.3"
    assert payload["source_l20_2_cli_readback_checkpoint_accepted"] is True
    assert payload["future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run"] is True
    assert payload["filesystem_validation_execution_allowed"] is False
    assert payload["filesystem_validation_active"] is False
    assert payload["filesystem_validation_performed"] is False
    assert payload["real_file_exists_check_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["downloaded_archive_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l20_03_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l20_03.build_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l20_2_cli_readback_checkpoint_accepted"] is False
    _assert_passive(payload)


def test_l20_03_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l20_03_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L20.3 Microsoft Edge downloaded-file filesystem validation passive plan checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "downloaded-file filesystem validation passive plan checkpoint",
        "passive plan checkpoint",
        "L20.2 CLI/readback checkpoint remains accepted",
        "safe future real-filesystem validation plan",
        "future filesystem validation candidate path must remain metadata-only in L20.3",
        "filesystem validation plan does not check whether a file exists",
        "filesystem validation plan does not stat a file",
        "filesystem validation plan does not hash a file",
        "filesystem validation plan does not read downloaded file bytes",
        "filesystem validation plan does not open a downloaded archive",
        "filesystem validation plan does not list downloaded archive contents",
        "filesystem validation plan does not extract a downloaded archive",
        "filesystem validation plan does not read a downloaded manifest",
        "filesystem validation plan does not run a package",
        "filesystem validation execution allowed: false",
        "filesystem validation active: false",
        "filesystem validation is not performed",
        "real filesystem validation remains inactive",
        "real file existence check remains inactive",
        "real file stat remains inactive",
        "real file hash remains inactive",
        "archive validation remains inactive",
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
        "L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate",
    ]:
        assert phrase in text
