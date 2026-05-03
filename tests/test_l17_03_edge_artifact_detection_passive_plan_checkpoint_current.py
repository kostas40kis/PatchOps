from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_detection_passive_plan_checkpoint as l17_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint"

PASSIVE_FALSE_FIELDS = (
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_allowed",
    "artifact_detection_performed",
    "artifact_content_reading_performed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_performed",
    "click_download_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "page_metadata_detection_proven",
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


def test_l17_03_builds_passive_plan_checkpoint() -> None:
    payload = l17_03.build_edge_artifact_detection_passive_plan_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L17.3"
    assert payload["source_patch"] == "L17.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l17_2_cli_readback_checkpoint_accepted"] is True
    assert payload["l17_2_complete"] is True
    assert payload["l17_1_passive_preflight_gate_accepted"] is True
    assert payload["artifact_presence_definition_blocks_content_and_download"] is True
    assert payload["artifact_presence_definition_forbids_sensitive_observations"] is True
    assert payload["future_artifact_presence_plan_is_planned_not_executed"] is True
    assert payload["future_artifact_presence_plan_blocks_download_paste_send_package_run"] is True
    assert payload["download_workflow_remains_separate_future_stream"] is True
    assert payload["operator_review_required_before_live_artifact_detection"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L17.4 Microsoft Edge artifact detection controlled live authorization gate"
    _assert_passive(payload)


def test_l17_03_artifact_presence_definition_is_metadata_only() -> None:
    definition = l17_03.artifact_presence_definition()

    assert "metadata-only evidence" in definition["artifact_presence_means"]
    assert definition["content_reading_allowed"] is False
    assert definition["download_allowed"] is False
    assert definition["package_run_allowed"] is False
    assert definition["candidate_filename_rules"]["extension_must_be"] == ".zip"
    assert definition["candidate_filename_rules"]["recommended_pattern"] == "patch_*_patchops_bundle.zip"
    assert definition["candidate_filename_rules"]["reject_non_zip"] is True
    assert definition["candidate_filename_rules"]["reject_ambiguous_multiple_candidates"] is True
    for forbidden in ["conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_file_bytes"]:
        assert forbidden in definition["forbidden_future_observations"]
    for allowed in [
        "visible_filename_metadata_ending_dot_zip",
        "filename_pattern_metadata_patchops_bundle_zip",
        "download_control_accessible_name_metadata",
        "candidate_belongs_to_latest_assistant_reply",
    ]:
        assert allowed in definition["allowed_future_metadata_signals"]


def test_l17_03_future_plan_blocks_download_paste_send_package_run() -> None:
    plan = l17_03.future_artifact_presence_plan("https://chatgpt.com/")

    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l17_2_cli_readback_checkpoint_accepted"
    assert plan[1]["name"] == "require_l17_4_or_later_explicit_live_authorization_token"
    assert plan[2]["name"] == "open_allowlisted_chatgpt_url_only_with_dedicated_edge_profile"
    assert plan[2]["allowed_only_in_future_live_phase"] is True
    assert plan[3]["name"] == "observe_latest_assistant_reply_metadata_without_text_extraction"
    assert "conversation_text" in plan[3]["forbidden_future_observations"]
    assert "artifact_content" in plan[3]["forbidden_future_observations"]
    assert plan[-1]["auto_click"] is False
    assert plan[-1]["auto_download"] is False
    assert plan[-1]["auto_paste"] is False
    assert plan[-1]["auto_send"] is False
    assert plan[-1]["package_run"] is False


def test_l17_03_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L17.3"
    assert payload["source_l17_2_cli_readback_checkpoint_accepted"] is True
    assert payload["artifact_presence_definition_blocks_content_and_download"] is True
    assert payload["future_artifact_presence_plan_blocks_download_paste_send_package_run"] is True
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["chatgpt_url_opened"] is False
    _assert_passive(payload)


def test_l17_03_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l17_03.build_edge_artifact_detection_passive_plan_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l17_2_cli_readback_checkpoint_accepted"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l17_03_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l17_03_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_detection_passive_plan_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L17.3 Microsoft Edge artifact detection passive plan checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "passive plan checkpoint",
        "L17.2 CLI/readback checkpoint remains accepted",
        "safe future artifact-presence detection plan",
        "artifact presence means metadata-only evidence that a downloadable PatchOps zip candidate exists",
        "artifact presence does not mean reading artifact content",
        "artifact presence does not mean clicking a download control",
        "artifact presence does not mean downloading a file",
        "artifact presence does not mean running a package",
        "download workflow remains inactive",
        "artifact detection execution allowed: false",
        "artifact detection is not performed",
        "download workflow active: false",
        "PatchOps remains source of truth",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be selected but not opened",
        "no Microsoft Edge start",
        "no Selenium import",
        "no CDP use",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no artifact detection",
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L17.4 Microsoft Edge artifact detection controlled live authorization gate",
    ]:
        assert phrase in text
