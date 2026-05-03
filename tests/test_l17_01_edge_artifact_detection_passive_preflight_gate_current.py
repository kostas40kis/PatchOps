from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_artifact_detection_passive_preflight_gate as l17_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-real-page-metadata-detection-final-acceptance-marker"
L16_6_COMMAND = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
L16_5_COMMAND = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_PREFLIGHT_AUTHORIZED"


def _assert_passive(payload: dict) -> None:
    assert payload["artifact_detection_execution_allowed"] is False
    assert payload["artifact_detection_active"] is False
    assert payload["artifact_detection_allowed"] is False
    assert payload["artifact_detection_performed"] is False
    assert payload["artifact_content_reading_performed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_workflow_allowed"] is False
    assert payload["download_performed"] is False
    assert payload["click_download_performed"] is False
    assert payload["pasteback_workflow_active"] is False
    assert payload["auto_send_allowed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["page_inspection_performed"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["cdp_used"] is False
    assert payload["remote_debugging_port_used"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["dom_scraping_performed"] is False
    assert payload["prompt_text_extraction_performed"] is False
    assert payload["conversation_reading_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False


def test_l17_01_default_preflight_is_green_and_passive() -> None:
    payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L17.1"
    assert payload["phase"] == "L17"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_6_command_name"] == L16_6_COMMAND
    assert payload["l16_5_command_name"] == L16_5_COMMAND
    assert payload["source_patch"] == "L16.7"
    assert payload["passive_preflight_gate"] is True
    assert payload["source_l16_7_final_marker_accepted"] is True
    assert payload["l16_metadata_detection_stream_complete"] is True
    assert payload["metadata_only_page_detection_accepted"] is True
    assert payload["artifact_detection_preflight_flag_present"] is False
    assert payload["artifact_detection_preflight_token_present"] is False
    assert payload["artifact_detection_preflight_authorized"] is False
    assert payload["artifact_detection_preflight_is_readback_only_in_l17_1"] is True
    assert payload["future_artifact_detection_plan_is_passive"] is True
    assert payload["future_artifact_detection_plan_blocks_download"] is True
    assert payload["patchops_remains_source_of_truth"] is True
    assert payload["target_url_status"]["ok"] is True
    assert payload["l17_1_complete"] is True
    assert payload["remaining_l17_1_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_passive(payload)


def test_l17_01_authorized_preflight_is_still_passive() -> None:
    payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(
        PROJECT_ROOT,
        allow_artifact_detection_preflight=True,
        authorization_token=TOKEN,
        target_url="https://chatgpt.com/",
    )
    assert payload["ok"] is True
    assert payload["artifact_detection_preflight_flag_present"] is True
    assert payload["artifact_detection_preflight_token_present"] is True
    assert payload["artifact_detection_preflight_authorized"] is True
    assert payload["artifact_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l17_01_rejects_non_allowlisted_target_without_browser_start() -> None:
    payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(
        PROJECT_ROOT,
        allow_artifact_detection_preflight=True,
        authorization_token=TOKEN,
        target_url="https://example.com/",
    )
    assert payload["ok"] is False
    assert payload["target_url_status"]["ok"] is False
    assert payload["target_url_status"]["host"] == "example.com"
    _assert_passive(payload)


def test_l17_01_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_6_COMMAND in names
    assert L16_5_COMMAND in names


def test_l17_01_cli_default_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L17.1"
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    _assert_passive(payload)


def test_l17_01_cli_authorized_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-artifact-detection-preflight",
            "--authorization-token",
            TOKEN,
            "--target-url",
            "https://chatgpt.com/",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["artifact_detection_preflight_authorized"] is True
    assert payload["artifact_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l17_01_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l17_01.build_edge_artifact_detection_passive_preflight_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l17_01_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md").read_text(encoding="utf-8")
    for phrase in [
        "L17.1 Microsoft Edge artifact detection passive preflight gate",
        COMMAND,
        SOURCE_COMMAND,
        L16_6_COMMAND,
        L16_5_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "passive preflight gate",
        "L16 metadata detection stream complete",
        "artifact detection is not active yet",
        "artifact detection preflight authorization is readback-only",
        "artifact detection execution allowed: false",
        "download workflow is not active yet",
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
        "L17.2 Microsoft Edge artifact detection CLI/readback checkpoint",
    ]:
        assert phrase in text
