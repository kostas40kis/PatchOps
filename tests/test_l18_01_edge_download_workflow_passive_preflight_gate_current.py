from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_download_workflow_passive_preflight_gate as l18_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-artifact-detection-final-acceptance-marker"
TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_PREFLIGHT_AUTHORIZED_READBACK_ONLY"


def _assert_no_download_browser_side_effects(payload: dict) -> None:
    for field in [
        "download_workflow_execution_allowed",
        "download_workflow_active",
        "download_workflow_allowed",
        "download_allowed",
        "download_performed",
        "downloaded_file_bytes_read",
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


def test_l18_01_default_readback_is_passive() -> None:
    payload = l18_01.build_edge_download_workflow_passive_preflight_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["patch"] == "L18.1"
    assert payload["source_patch"] == "L17.7"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["source_l17_7_artifact_detection_final_marker_accepted"] is True
    assert payload["l17_artifact_detection_stream_complete"] is True
    assert payload["download_workflow_preflight_requested"] is False
    assert payload["download_workflow_preflight_authorized"] is False
    assert payload["download_workflow_preflight_authorization_is_readback_only_in_l18_1"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["next_patch"] == "L18.2 Microsoft Edge download workflow CLI/readback checkpoint"
    _assert_no_download_browser_side_effects(payload)


def test_l18_01_authorized_readback_still_blocks_download() -> None:
    payload = l18_01.build_edge_download_workflow_passive_preflight_gate(
        PROJECT_ROOT,
        allow_download_workflow_preflight=True,
        authorization_token=TOKEN,
    )

    assert payload["ok"] is True
    assert payload["download_workflow_preflight_requested"] is True
    assert payload["download_workflow_preflight_authorized"] is True
    assert payload["download_workflow_preflight_readback"]["download_workflow_preflight_authorization_token_present"] is True
    _assert_no_download_browser_side_effects(payload)


def test_l18_01_wrong_token_does_not_authorize() -> None:
    payload = l18_01.build_edge_download_workflow_passive_preflight_gate(
        PROJECT_ROOT,
        allow_download_workflow_preflight=True,
        authorization_token="wrong-token",
    )
    assert payload["ok"] is True
    assert payload["download_workflow_preflight_requested"] is True
    assert payload["download_workflow_preflight_authorized"] is False
    _assert_no_download_browser_side_effects(payload)


def test_l18_01_cli_default_and_authorized_compact_json_smokes() -> None:
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
    assert default_payload["download_workflow_preflight_authorized"] is False
    _assert_no_download_browser_side_effects(default_payload)

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
            "--allow-download-workflow-preflight",
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
    assert authorized_payload["download_workflow_preflight_authorized"] is True
    _assert_no_download_browser_side_effects(authorized_payload)


def test_l18_01_rejects_disallowed_target_url_without_side_effects() -> None:
    payload = l18_01.build_edge_download_workflow_passive_preflight_gate(
        PROJECT_ROOT,
        target_url="http://example.test/",
        allow_download_workflow_preflight=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is False
    assert payload["target_url_allowed"] is False
    assert payload["source_l17_7_artifact_detection_final_marker_accepted"] is False
    _assert_no_download_browser_side_effects(payload)


def test_l18_01_command_registered() -> None:
    from patchops.llm_browser import commands

    names = tuple(commands.llm_browser_command_names())
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l18_01_doc_mentions_safety_contract() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_download_workflow_passive_preflight_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L18.1 Microsoft Edge download workflow passive preflight gate",
        COMMAND,
        SOURCE_COMMAND,
        TOKEN,
        "Microsoft Edge first",
        "Opera second",
        "download workflow passive preflight gate",
        "L17.7 artifact detection final marker remains accepted",
        "download workflow preflight authorization is readback-only",
        "download workflow execution allowed: false",
        "download workflow active: false",
        "download is not performed",
        "downloaded file bytes are not read",
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
        "L18.2 Microsoft Edge download workflow CLI/readback checkpoint",
    ]:
        assert phrase in text
