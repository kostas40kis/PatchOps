from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_detection_broad_checkpoint as l17_06

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-detection-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-presence-metadata-proof"


def _assert_no_browser_download_content_side_effects(payload: dict) -> None:
    for field in [
        "artifact_detection_execution_allowed",
        "live_artifact_detection_execution_allowed",
        "artifact_presence_detection_execution_allowed",
        "artifact_detection_active",
        "artifact_detection_allowed",
        "artifact_detection_performed",
        "artifact_presence_detection_performed",
        "real_page_inspection_performed",
        "live_browser_artifact_detection_active",
        "live_browser_artifact_detection_performed",
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
    ]:
        assert payload[field] is False, field


def test_l17_06_builds_broad_checkpoint() -> None:
    payload = l17_06.build_edge_artifact_detection_broad_checkpoint(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L17.6"
    assert payload["source_patch"] == "L17.5"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l17_1_through_l17_5_remain_accepted"] is True
    assert payload["metadata_only_artifact_presence_proof_remains_accepted"] is True
    assert payload["metadata_only_broad_checkpoint"] is True
    assert payload["source_l17_5_default_readback_ok"] is True
    assert payload["source_l17_5_authorized_positive_readback_ok"] is True
    assert payload["source_l17_4_controlled_live_authorization_gate_accepted"] is True
    assert payload["source_l17_3_passive_plan_checkpoint_accepted"] is True
    assert payload["artifact_presence_metadata_classification_validated"] is True
    assert payload["artifact_presence_detection_scope"] == "synthetic_or_operator_supplied_metadata_only"
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L17.7 Microsoft Edge artifact detection final acceptance marker"
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_06_cli_compact_json_smoke() -> None:
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
    assert payload["patch"] == "L17.6"
    assert payload["l17_1_through_l17_5_remain_accepted"] is True
    assert payload["metadata_only_artifact_presence_proof_remains_accepted"] is True
    assert payload["source_l17_5_authorized_summary"]["artifact_presence_detected_from_metadata"] is True
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_06_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l17_06.build_edge_artifact_detection_broad_checkpoint(
        PROJECT_ROOT,
        target_url="http://example.test/",
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["l17_1_through_l17_5_remain_accepted"] is False
    _assert_no_browser_download_content_side_effects(payload)


def test_l17_06_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l17_06_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_detection_broad_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L17.6 Microsoft Edge artifact detection broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "broad passive checkpoint",
        "L17.1 through L17.5 remain accepted",
        "metadata-only artifact-presence proof remains accepted",
        "metadata-only broad checkpoint",
        "live browser artifact detection remains inactive",
        "artifact detection execution allowed: false",
        "real page inspection performed: false",
        "artifact content reading performed: false",
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
        "no artifact content reading",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L17.7 Microsoft Edge artifact detection final acceptance marker",
    ]:
        assert phrase in text
