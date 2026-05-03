from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_real_page_detection_passive_preflight_gate as l16_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
L15_4_COMMAND = "browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint"
L15_3_COMMAND = "browser-start-supervised-launch-edge-first-controlled-open-proof"
L15_2_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_PREFLIGHT_AUTHORIZED"


def _assert_passive(payload: dict) -> None:
    assert payload["real_page_detection_active"] is False
    assert payload["real_page_detection_allowed"] is False
    assert payload["page_inspection_allowed"] is False
    assert payload["page_inspection_performed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["live_open_smoke_executed"] is False
    assert payload["live_open_smoke_proven"] is False
    assert payload["browser_close_attempted"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
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


def test_l16_01_default_preflight_is_green_and_passive() -> None:
    payload = l16_01.build_edge_real_page_detection_passive_preflight_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.1"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l15_4_command_name"] == L15_4_COMMAND
    assert payload["l15_3_command_name"] == L15_3_COMMAND
    assert payload["l15_2_command_name"] == L15_2_COMMAND
    assert payload["l15_1_command_name"] == L15_1_COMMAND
    assert payload["source_patch"] == "L15.5"
    assert payload["passive_preflight_gate"] is True
    assert payload["source_l15_5_handoff_marker_accepted"] is True
    assert payload["source_l15_5_cli_readback_accepted"] is True
    assert payload["l15_live_start_stream_complete"] is True
    assert payload["l15_1_through_l15_4_accepted"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["real_page_detection_preflight_flag_present"] is False
    assert payload["real_page_detection_preflight_token_present"] is False
    assert payload["real_page_detection_preflight_authorized"] is False
    assert payload["target_url_allowlist_enforced"] is True
    assert payload["target_url_status"]["ok"] is True
    assert payload["chatgpt_url_selected_for_future_detection"] is True
    assert payload["l16_1_complete"] is True
    assert payload["remaining_l16_1_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_passive(payload)


def test_l16_01_authorized_preflight_is_still_passive() -> None:
    payload = l16_01.build_edge_real_page_detection_passive_preflight_gate(
        PROJECT_ROOT,
        allow_real_page_detection_preflight=True,
        authorization_token=TOKEN,
        target_url="https://chatgpt.com/",
    )
    assert payload["ok"] is True
    assert payload["real_page_detection_preflight_flag_present"] is True
    assert payload["real_page_detection_preflight_token_present"] is True
    assert payload["real_page_detection_preflight_authorized"] is True
    assert payload["target_url_status"]["ok"] is True
    assert payload["target_url_status"]["host"] == "chatgpt.com"
    _assert_passive(payload)


def test_l16_01_rejects_non_allowlisted_target_url_without_opening_browser() -> None:
    payload = l16_01.build_edge_real_page_detection_passive_preflight_gate(
        PROJECT_ROOT,
        allow_real_page_detection_preflight=True,
        authorization_token=TOKEN,
        target_url="https://example.com/",
    )
    assert payload["ok"] is False
    assert payload["target_url_status"]["ok"] is False
    assert payload["target_url_status"]["host"] == "example.com"
    _assert_passive(payload)


def test_l16_01_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L15_4_COMMAND in names
    assert L15_3_COMMAND in names
    assert L15_2_COMMAND in names
    assert L15_1_COMMAND in names


def test_l16_01_cli_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L16.1"
    assert payload["source_l15_5_handoff_marker_accepted"] is True
    assert payload["real_page_detection_active"] is False
    _assert_passive(payload)


def test_l16_01_cli_authorized_compact_json_is_still_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-real-page-detection-preflight",
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
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["real_page_detection_preflight_authorized"] is True
    assert payload["chatgpt_url_opened"] is False
    _assert_passive(payload)


def test_l16_01_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l16_01.build_edge_real_page_detection_passive_preflight_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_01_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.1 Microsoft Edge real-page detection passive preflight gate",
        COMMAND,
        SOURCE_COMMAND,
        L15_4_COMMAND,
        L15_3_COMMAND,
        L15_2_COMMAND,
        L15_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "passive preflight gate",
        "real-page detection is not active yet",
        "target URL allowlist",
        "ChatGPT URL may be selected but not opened",
        "no Microsoft Edge start",
        "no Selenium import",
        "no ChatGPT interaction",
        "no page inspection",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L16.2 Microsoft Edge real-page detection CLI/readback checkpoint",
    ]:
        assert phrase in text
