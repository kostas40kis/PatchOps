from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_detection_controlled_live_authorization_gate as l17_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint"
TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_LIVE_AUTHORIZED_READBACK_ONLY"

PASSIVE_FALSE_FIELDS = (
    "live_artifact_detection_execution_allowed",
    "artifact_detection_execution_allowed",
    "artifact_presence_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_allowed",
    "artifact_detection_performed",
    "artifact_presence_detection_performed",
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


def test_l17_04_builds_default_passive_live_authorization_gate() -> None:
    payload = l17_04.build_edge_artifact_detection_controlled_live_authorization_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L17.4"
    assert payload["source_patch"] == "L17.3"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l17_3_passive_plan_checkpoint_accepted"] is True
    assert payload["l17_3_complete"] is True
    assert payload["passive_readback_only_in_l17_4"] is True
    assert payload["live_artifact_detection_authorization_requested"] is False
    assert payload["live_artifact_detection_authorization_token_present"] is False
    assert payload["live_artifact_detection_authorized_for_future_phase"] is False
    assert payload["live_artifact_detection_authorization_is_readback_only_in_l17_4"] is True
    assert payload["live_artifact_detection_execution_allowed"] is False
    assert payload["artifact_presence_detection_execution_allowed"] is False
    assert payload["requires_dedicated_edge_runtime_profile_in_future_live_phase"] is True
    assert payload["default_microsoft_edge_profile_allowed"] is False
    assert payload["future_live_authorization_plan_is_planned_not_executed"] is True
    assert payload["future_live_authorization_plan_blocks_detection_download_send_package_run"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L17.5 Microsoft Edge first controlled artifact-presence metadata proof"
    _assert_passive(payload)


def test_l17_04_authorized_readback_still_blocks_execution() -> None:
    payload = l17_04.build_edge_artifact_detection_controlled_live_authorization_gate(
        PROJECT_ROOT,
        allow_live_artifact_detection_authorization=True,
        authorization_token=TOKEN,
    )

    assert payload["ok"] is True
    assert payload["live_artifact_detection_authorization_requested"] is True
    assert payload["live_artifact_detection_authorization_token_present"] is True
    assert payload["live_artifact_detection_authorized_for_future_phase"] is True
    assert payload["live_artifact_detection_authorization_is_readback_only_in_l17_4"] is True
    assert payload["live_artifact_detection_execution_allowed"] is False
    assert payload["artifact_presence_detection_execution_allowed"] is False
    assert payload["artifact_detection_execution_allowed"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["artifact_detection_performed"] is False
    assert payload["artifact_presence_detection_performed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["chatgpt_url_opened"] is False
    _assert_passive(payload)


def test_l17_04_wrong_token_does_not_authorize_future_phase() -> None:
    payload = l17_04.build_edge_artifact_detection_controlled_live_authorization_gate(
        PROJECT_ROOT,
        allow_live_artifact_detection_authorization=True,
        authorization_token="wrong-token",
    )

    assert payload["ok"] is True
    assert payload["live_artifact_detection_authorization_requested"] is True
    assert payload["live_artifact_detection_authorization_token_present"] is False
    assert payload["live_artifact_detection_authorized_for_future_phase"] is False
    assert payload["live_artifact_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l17_04_authorization_plan_requires_profile_and_blocks_execution() -> None:
    plan = l17_04.future_live_authorization_gate_plan("https://chatgpt.com/")
    assert all(item["status"] == "planned_not_executed" for item in plan)
    assert plan[0]["name"] == "confirm_l17_3_passive_plan_checkpoint_accepted"
    assert plan[1]["name"] == "require_explicit_live_artifact_detection_authorization_flag"
    assert plan[2]["required_authorization_token"] == TOKEN
    assert plan[3]["default_microsoft_edge_profile_allowed"] is False
    assert plan[4]["allowed_only_in_future_l17_5_or_later"] is True
    assert plan[-1]["artifact_detection_execution_allowed"] is False
    assert plan[-1]["auto_click"] is False
    assert plan[-1]["auto_download"] is False
    assert plan[-1]["auto_paste"] is False
    assert plan[-1]["auto_send"] is False
    assert plan[-1]["package_run"] is False


def test_l17_04_cli_default_and_authorized_compact_json_smokes() -> None:
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
    assert len(default_completed.stdout) < 90000
    default_payload = json.loads(default_completed.stdout)
    assert default_payload["ok"] is True
    assert default_payload["patch"] == "L17.4"
    assert default_payload["live_artifact_detection_authorized_for_future_phase"] is False
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
            "--allow-live-artifact-detection-authorization",
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
    assert authorized_payload["patch"] == "L17.4"
    assert authorized_payload["live_artifact_detection_authorized_for_future_phase"] is True
    assert authorized_payload["live_artifact_detection_execution_allowed"] is False
    assert authorized_payload["artifact_detection_active"] is False
    assert authorized_payload["download_workflow_active"] is False
    assert authorized_payload["browser_started"] is False
    assert authorized_payload["edge_process_started"] is False
    _assert_passive(authorized_payload)


def test_l17_04_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l17_04.build_edge_artifact_detection_controlled_live_authorization_gate(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_live_artifact_detection_authorization=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l17_3_passive_plan_checkpoint_accepted"] is False
    assert payload["live_artifact_detection_authorized_for_future_phase"] is True
    assert payload["live_artifact_detection_execution_allowed"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)


def test_l17_04_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l17_04_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_detection_controlled_live_authorization_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L17.4 Microsoft Edge artifact detection controlled live authorization gate",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "controlled live authorization gate",
        "passive/readback-only in L17.4",
        "L17.3 passive plan checkpoint remains accepted",
        "explicit future live authorization token",
        "live artifact detection authorization is readback-only",
        "live artifact detection execution allowed: false",
        "artifact detection execution allowed: false",
        "artifact detection is not performed",
        "artifact presence detection is not performed",
        "download workflow active: false",
        "download workflow remains inactive",
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
        "no artifact detection",
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L17.5 Microsoft Edge first controlled artifact-presence metadata proof",
    ]:
        assert phrase in text

# PATCHOPS L17.4A SOURCE PASSIVE COMPATIBILITY REPAIR START

def test_l17_04_uses_l17_3_compatible_source_passive_field_set() -> None:
    payload = l17_04.build_edge_artifact_detection_controlled_live_authorization_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["source_l17_3_passive_plan_checkpoint_accepted"] is True
    assert payload["source_l17_3_summary"]["ok"] is True
    assert payload["source_l17_3_summary"]["patch"] == "L17.3"
    assert payload["source_l17_3_summary"]["l17_3_complete"] is True
    assert payload["live_artifact_detection_execution_allowed"] is False
    assert payload["artifact_presence_detection_execution_allowed"] is False
    assert payload["artifact_presence_detection_performed"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_passive(payload)
# PATCHOPS L17.4A SOURCE PASSIVE COMPATIBILITY REPAIR END
