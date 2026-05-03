from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_final_acceptance_marker as l16_07

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-real-page-metadata-detection-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
L16_5_COMMAND = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
L16_4_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"


def _assert_passive(payload: dict) -> None:
    assert payload["artifact_detection_active"] is False
    assert payload["artifact_detection_allowed"] is False
    assert payload["download_workflow_active"] is False
    assert payload["download_workflow_allowed"] is False
    assert payload["pasteback_workflow_active"] is False
    assert payload["auto_send_allowed"] is False
    assert payload["real_page_detection_active"] is False
    assert payload["page_detection_execution_allowed"] is False
    assert payload["page_inspection_performed"] is False
    assert payload["page_metadata_detection_performed"] is False
    assert payload["page_metadata_detection_proven"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_close_attempted"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["cdp_used"] is False
    assert payload["remote_debugging_port_used"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["dom_scraping_performed"] is False
    assert payload["prompt_text_extraction_performed"] is False
    assert payload["conversation_reading_performed"] is False
    assert payload["artifact_detection_performed"] is False
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False


def test_l16_07_final_marker_is_green_and_passive() -> None:
    payload = l16_07.build_edge_real_page_metadata_detection_final_acceptance_marker(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.7"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_5_command_name"] == L16_5_COMMAND
    assert payload["l16_4_command_name"] == L16_4_COMMAND
    assert payload["l16_3_command_name"] == L16_3_COMMAND
    assert payload["l16_2_command_name"] == L16_2_COMMAND
    assert payload["l16_1_command_name"] == L16_1_COMMAND
    assert payload["source_patch"] == "L16.6"
    assert payload["final_acceptance_marker"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["l16_1_through_l16_6_accepted"] is True
    assert payload["l16_metadata_detection_stream_complete"] is True
    assert payload["metadata_only_page_detection_accepted"] is True
    assert payload["os_window_process_metadata_only_accepted"] is True
    assert payload["l16_7_complete"] is True
    assert payload["remaining_l16_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert len(payload["accepted_l16_sequence"]) == 7
    _assert_passive(payload)


def test_l16_07_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_5_COMMAND in names
    assert L16_4_COMMAND in names
    assert L16_3_COMMAND in names
    assert L16_2_COMMAND in names
    assert L16_1_COMMAND in names


def test_l16_07_cli_compact_json_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L16.7"
    assert payload["l16_metadata_detection_stream_complete"] is True
    assert payload["artifact_detection_active"] is False
    assert payload["download_workflow_active"] is False
    _assert_passive(payload)


def test_l16_07_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l16_07.build_edge_real_page_metadata_detection_final_acceptance_marker(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_07_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.7 Microsoft Edge real-page metadata detection final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        L16_5_COMMAND,
        L16_4_COMMAND,
        L16_3_COMMAND,
        L16_2_COMMAND,
        L16_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "final acceptance marker",
        "L16.1 through L16.6 accepted",
        "L16 metadata detection stream complete",
        "artifact detection is not active yet",
        "download workflow is not active yet",
        "metadata-only page detection accepted",
        "OS/window/process metadata only accepted",
        "no Microsoft Edge start",
        "no Selenium import",
        "no CDP use",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L17.1 Microsoft Edge artifact detection passive preflight gate",
    ]:
        assert phrase in text
