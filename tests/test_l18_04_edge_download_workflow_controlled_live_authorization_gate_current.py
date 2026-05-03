from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_download_workflow_controlled_live_authorization_gate as l18_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint"
TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_WORKFLOW_LIVE_AUTHORIZED_READBACK_ONLY"

PASSIVE_FALSE_FIELDS = (
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


def test_l18_04_builds_default_live_authorization_gate() -> None:
    payload = l18_04.build_edge_download_workflow_controlled_live_authorization_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["patch"] == "L18.4"
    assert payload["source_patch"] == "L18.3"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l18_3_passive_plan_checkpoint_accepted"] is True
    assert payload["l18_3_complete"] is True
    assert payload["live_download_authorization_requested"] is False
    assert payload["live_download_authorization_token_present"] is False
    assert payload["live_download_authorized_for_future_phase"] is False
    assert payload["live_download_authorization_is_readback_only_in_l18_4"] is True
    assert payload["future_live_download_plan_is_planned_not_executed"] is True
    assert payload["future_live_download_plan_blocks_click_download_file_read_paste_send_package_run"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L18.5 Microsoft Edge first controlled download metadata proof"
    _assert_passive(payload)


def test_l18_04_authorized_readback_still_blocks_download_execution() -> None:
    payload = l18_04.build_edge_download_workflow_controlled_live_authorization_gate(
        PROJECT_ROOT,
        allow_live_download_authorization=True,
        authorization_token=TOKEN,
    )

    assert payload["ok"] is True
    assert payload["live_download_authorization_requested"] is True
    assert payload["live_download_authorization_token_present"] is True
    assert payload["live_download_authorized_for_future_phase"] is True
    assert payload["live_download_authorization_is_readback_only_in_l18_4"] is True
    assert payload["live_download_execution_allowed"] is False
    assert payload["download_workflow_execution_allowed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_allowed"] is False
    assert payload["download_performed"] is False
    assert payload["downloaded_file_bytes_read"] is False
    assert payload["click_download_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l18_04_wrong_token_does_not_authorize_future_phase() -> None:
    payload = l18_04.build_edge_download_workflow_controlled_live_authorization_gate(
        PROJECT_ROOT,
        allow_live_download_authorization=True,
        authorization_token="wrong-token",
    )
    assert payload["ok"] is True
    assert payload["live_download_authorization_requested"] is True
    assert payload["live_download_authorization_token_present"] is False
    assert payload["live_download_authorized_for_future_phase"] is False
    assert payload["live_download_execution_allowed"] is False
    _assert_passive(payload)


def test_l18_04_authorization_plan_requires_profile_and_blocks_execution() -> None:
    plan = l18_04.future_live_download_authorization_gate_plan("https://chatgpt.com/")
    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l18_3_passive_plan_checkpoint_accepted"
    assert plan[1]["name"] == "require_explicit_live_download_authorization_flag"
    assert plan[2]["required_authorization_token"] == TOKEN
    assert plan[3]["default_microsoft_edge_profile_allowed"] is False
    assert plan[4]["allowed_only_in_future_l18_5_or_later"] is True
    assert plan[-1]["live_download_execution_allowed"] is False
    assert plan[-1]["download_workflow_execution_allowed"] is False
    assert plan[-1]["auto_click"] is False
    assert plan[-1]["auto_download"] is False
    assert plan[-1]["read_downloaded_file_bytes"] is False
    assert plan[-1]["auto_paste"] is False
    assert plan[-1]["auto_send"] is False
    assert plan[-1]["package_run"] is False


def test_l18_04_cli_default_and_authorized_compact_json_smokes() -> None:
    default_completed = subprocess.run(
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
    assert default_completed.returncode == 0, default_completed.stderr
    default_payload = json.loads(default_completed.stdout)
    assert default_payload["ok"] is True
    assert default_payload["patch"] == "L18.4"
    assert default_payload["live_download_authorized_for_future_phase"] is False
    _assert_passive(default_payload)

    authorized_completed = subprocess.run(
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
            "--allow-live-download-authorization",
            "--authorization-token",
            TOKEN,
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert authorized_completed.returncode == 0, authorized_completed.stderr
    assert len(authorized_completed.stdout) < 90000
    authorized_payload = json.loads(authorized_completed.stdout)
    assert authorized_payload["ok"] is True
    assert authorized_payload["patch"] == "L18.4"
    assert authorized_payload["live_download_authorized_for_future_phase"] is True
    assert authorized_payload["live_download_execution_allowed"] is False
    assert authorized_payload["download_workflow_active"] is False
    assert authorized_payload["download_performed"] is False
    assert authorized_payload["browser_started"] is False
    assert authorized_payload["edge_process_started"] is False
    _assert_passive(authorized_payload)


def test_l18_04_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l18_04.build_edge_download_workflow_controlled_live_authorization_gate(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_live_download_authorization=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l18_3_passive_plan_checkpoint_accepted"] is False
    assert payload["live_download_authorized_for_future_phase"] is True
    assert payload["live_download_execution_allowed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l18_04_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l18_04_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_download_workflow_controlled_live_authorization_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L18.4 Microsoft Edge download workflow controlled live authorization gate",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "download workflow controlled live authorization gate",
        "passive/readback-only in L18.4",
        "L18.3 passive plan checkpoint remains accepted",
        "explicit future live download authorization token",
        "live download authorization is readback-only",
        "live download execution allowed: false",
        "download workflow execution allowed: false",
        "download workflow active: false",
        "download is not performed",
        "downloaded file bytes are not read",
        "download staging directory is not created",
        "artifact content reading performed: false",
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
        "L18.5 Microsoft Edge first controlled download metadata proof",
    ]:
        assert phrase in text
