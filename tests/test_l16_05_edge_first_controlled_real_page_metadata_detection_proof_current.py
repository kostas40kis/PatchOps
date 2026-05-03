from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_first_controlled_real_page_metadata_detection_proof as l16_05

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"


def _assert_no_forbidden_side_effects(payload: dict) -> None:
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
    assert payload["auto_send_allowed"] is False


def test_l16_05_dry_readback_requires_explicit_execution_before_opening_chatgpt() -> None:
    payload = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.5"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_3_command_name"] == L16_3_COMMAND
    assert payload["l16_2_command_name"] == L16_2_COMMAND
    assert payload["l16_1_command_name"] == L16_1_COMMAND
    assert payload["source_patch"] == "L16.4"
    assert payload["first_controlled_real_page_metadata_detection_proof"] is True
    assert payload["source_l16_4_authorization_gate_accepted"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["real_page_detection_execution_authorized"] is False
    assert payload["execute_page_metadata_detection_flag_present"] is False
    assert payload["page_detection_execution_allowed"] is False
    assert payload["real_page_detection_active"] is False
    assert payload["page_inspection_allowed"] is False
    assert payload["page_inspection_performed"] is False
    assert payload["page_metadata_detection_performed"] is False
    assert payload["page_metadata_detection_proven"] is False
    assert payload["page_identity_metadata_detected"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["target_url_status"]["ok"] is True
    assert payload["dedicated_patchops_profile_allowed"] is True
    assert payload["default_edge_profile_rejected"] is True
    assert payload["default_profile_use_allowed"] is False
    assert payload["metadata_only_detection_contract"]["observation_source"] == "os_window_process_metadata_only"
    assert payload["current_url_observed"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_no_forbidden_side_effects(payload)


def test_l16_05_bad_token_with_execute_flag_does_not_open_chatgpt() -> None:
    payload = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(
        PROJECT_ROOT,
        allow_real_page_detection_execution=True,
        authorization_token="WRONG",
        execute_page_metadata_detection=True,
    )
    assert payload["ok"] is True
    assert payload["real_page_detection_execution_flag_present"] is True
    assert payload["real_page_detection_execution_token_present"] is False
    assert payload["real_page_detection_execution_authorized"] is False
    assert payload["execute_page_metadata_detection_flag_present"] is True
    assert payload["page_detection_execution_allowed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l16_05_rejects_non_allowlisted_target_without_browser_start() -> None:
    payload = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(
        PROJECT_ROOT,
        allow_real_page_detection_execution=True,
        authorization_token=TOKEN,
        execute_page_metadata_detection=True,
        target_url="https://example.com/",
    )
    assert payload["ok"] is False
    assert payload["target_url_status"]["ok"] is False
    assert payload["target_url_status"]["host"] == "example.com"
    assert payload["page_detection_execution_allowed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["browser_started"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l16_05_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_3_COMMAND in names
    assert L16_2_COMMAND in names
    assert L16_1_COMMAND in names


def test_l16_05_cli_dry_compact_json_is_parseable() -> None:
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
    assert payload["patch"] == "L16.5"
    assert payload["page_detection_execution_allowed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["browser_started"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l16_05_does_not_import_optional_browser_dependencies_in_dry_readback() -> None:
    before = set(sys.modules)
    payload = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_05_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_first_controlled_real_page_metadata_detection_proof.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.5 Microsoft Edge first controlled real-page metadata detection proof",
        COMMAND,
        SOURCE_COMMAND,
        L16_3_COMMAND,
        L16_2_COMMAND,
        L16_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "first controlled real-page metadata detection proof",
        "explicit execution authorization required",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be opened only with explicit authorization",
        "dedicated PatchOps runtime profile only",
        "default Microsoft Edge profile rejected",
        "metadata-only page detection",
        "OS/window/process metadata only",
        "requested URL, process count, window count, and window title only",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no Selenium import",
        "no CDP use",
        "no browser extension",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no git commit or git push",
        "L16.6 Microsoft Edge real-page metadata detection broad checkpoint",
    ]:
        assert phrase in text
