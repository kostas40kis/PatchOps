from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_download_workflow_passive_plan_checkpoint as l18_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint"

PASSIVE_FALSE_FIELDS = (
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


def test_l18_03_builds_passive_plan_checkpoint() -> None:
    payload = l18_03.build_edge_download_workflow_passive_plan_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L18.3"
    assert payload["source_patch"] == "L18.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l18_2_cli_readback_checkpoint_accepted"] is True
    assert payload["l18_2_complete"] is True
    assert payload["l18_1_passive_preflight_gate_accepted"] is True
    assert payload["download_candidate_definition_blocks_download_file_read_package_run"] is True
    assert payload["future_download_plan_is_planned_not_executed"] is True
    assert payload["future_download_plan_blocks_click_download_file_read_paste_send_package_run"] is True
    assert payload["download_staging_path_metadata_only"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L18.4 Microsoft Edge download workflow controlled live authorization gate"
    _assert_passive(payload)


def test_l18_03_download_candidate_definition_is_metadata_only() -> None:
    definition = l18_03.download_candidate_definition()

    assert "metadata-only evidence" in definition["download_candidate_means"]
    assert definition["candidate_filename_rules"]["extension_must_be"] == ".zip"
    assert definition["candidate_filename_rules"]["recommended_pattern"] == "patch_*_patchops_bundle.zip"
    assert definition["candidate_filename_rules"]["reject_non_zip"] is True
    assert definition["candidate_filename_rules"]["reject_ambiguous_multiple_candidates"] is True
    assert definition["future_download_staging_rules"]["staging_path_is_metadata_only_in_l18_3"] is True
    assert definition["future_download_staging_rules"]["create_staging_directory_allowed_in_l18_3"] is False
    assert definition["future_download_staging_rules"]["read_downloaded_file_bytes_allowed_in_l18_3"] is False
    assert definition["future_download_staging_rules"]["run_downloaded_package_allowed_in_l18_3"] is False
    for forbidden in ["clicking a download control", "downloading a file", "reading downloaded file bytes", "reading artifact content", "running a package"]:
        assert forbidden in definition["download_candidate_does_not_mean"]


def test_l18_03_future_plan_blocks_download_file_read_package_run() -> None:
    plan = l18_03.future_download_workflow_plan("https://chatgpt.com/")

    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l18_2_cli_readback_checkpoint_accepted"
    assert plan[1]["name"] == "require_l18_4_or_later_explicit_download_authorization_token"
    assert plan[2]["candidate_source"] == "accepted_l17_metadata_only_artifact_presence_stream"
    assert plan[3]["download_staging_path_is_metadata_only"] is True
    assert plan[3]["create_directory"] is False
    assert plan[3]["read_file_bytes"] is False
    assert plan[4]["allowed_only_in_future_l18_4_or_later"] is True
    assert plan[-1]["download_performed_in_l18_3"] is False
    assert plan[-1]["downloaded_file_bytes_read_in_l18_3"] is False
    assert plan[-1]["package_run"] is False
    assert plan[-1]["pasteback"] is False
    assert plan[-1]["auto_send"] is False


def test_l18_03_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L18.3"
    assert payload["source_l18_2_cli_readback_checkpoint_accepted"] is True
    assert payload["future_download_plan_blocks_click_download_file_read_paste_send_package_run"] is True
    assert payload["download_workflow_execution_allowed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l18_03_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l18_03.build_edge_download_workflow_passive_plan_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l18_2_cli_readback_checkpoint_accepted"] is False
    assert payload["download_workflow_execution_allowed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l18_03_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l18_03_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_download_workflow_passive_plan_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L18.3 Microsoft Edge download workflow passive plan checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "download workflow passive plan checkpoint",
        "passive plan checkpoint",
        "L18.2 CLI/readback checkpoint remains accepted",
        "safe future download workflow plan",
        "download candidate means metadata-only evidence for a PatchOps zip artifact selected by the accepted L17 stream",
        "download plan does not click a download control",
        "download plan does not download a file",
        "download plan does not read downloaded file bytes",
        "download plan does not read artifact content",
        "download plan does not run a package",
        "download workflow execution allowed: false",
        "download workflow active: false",
        "download is not performed",
        "downloaded file bytes are not read",
        "download staging path is planned metadata only",
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
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L18.4 Microsoft Edge download workflow controlled live authorization gate",
    ]:
        assert phrase in text
