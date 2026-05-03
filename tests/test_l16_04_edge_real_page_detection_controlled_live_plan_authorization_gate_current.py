from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate as l16_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
L15_5_COMMAND = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"


def _assert_passive(payload: dict) -> None:
    assert payload["page_detection_execution_allowed"] is False
    assert payload["real_page_detection_active"] is False
    assert payload["real_page_detection_allowed"] is False
    assert payload["page_inspection_allowed"] is False
    assert payload["page_inspection_performed"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
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


def test_l16_04_default_readback_is_green_and_passive() -> None:
    payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.4"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_2_command_name"] == L16_2_COMMAND
    assert payload["l16_1_command_name"] == L16_1_COMMAND
    assert payload["l15_5_command_name"] == L15_5_COMMAND
    assert payload["source_patch"] == "L16.3"
    assert payload["controlled_live_plan_authorization_gate"] is True
    assert payload["source_l16_3_passive_plan_checkpoint_accepted"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["real_page_detection_execution_flag_present"] is False
    assert payload["real_page_detection_execution_token_present"] is False
    assert payload["real_page_detection_execution_authorized"] is False
    assert payload["execution_authorization_is_readback_only_in_l16_4"] is True
    assert payload["target_url_status"]["ok"] is True
    assert payload["metadata_only_detection_contract"]["allowed_observations"] == ["current_url", "page_title", "ready_state", "window_count"]
    assert "conversation_text" in payload["metadata_only_detection_contract"]["forbidden_observations"]
    assert payload["l16_4_complete"] is True
    assert payload["remaining_l16_4_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_passive(payload)


def test_l16_04_authorized_readback_is_still_passive() -> None:
    payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        PROJECT_ROOT,
        allow_real_page_detection_execution=True,
        authorization_token=TOKEN,
        target_url="https://chatgpt.com/",
    )
    assert payload["ok"] is True
    assert payload["real_page_detection_execution_flag_present"] is True
    assert payload["real_page_detection_execution_token_present"] is True
    assert payload["real_page_detection_execution_authorized"] is True
    assert payload["chatgpt_url_authorized_for_future_detection"] is True
    assert payload["page_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l16_04_rejects_non_allowlisted_target_without_browser_start() -> None:
    payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        PROJECT_ROOT,
        allow_real_page_detection_execution=True,
        authorization_token=TOKEN,
        target_url="https://example.com/",
    )
    assert payload["ok"] is False
    assert payload["target_url_status"]["ok"] is False
    assert payload["target_url_status"]["host"] == "example.com"
    _assert_passive(payload)


def test_l16_04_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_2_COMMAND in names
    assert L16_1_COMMAND in names
    assert L15_5_COMMAND in names


def test_l16_04_cli_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L16.4"
    assert payload["real_page_detection_execution_authorized"] is False
    assert payload["page_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l16_04_cli_authorized_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-real-page-detection-execution",
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
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["real_page_detection_execution_authorized"] is True
    assert payload["execution_authorization_is_readback_only_in_l16_4"] is True
    assert payload["page_detection_execution_allowed"] is False
    _assert_passive(payload)


def test_l16_04_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_04_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate",
        COMMAND,
        SOURCE_COMMAND,
        L16_2_COMMAND,
        L16_1_COMMAND,
        L15_5_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "controlled live plan authorization gate",
        "execution authorization is readback-only in L16.4",
        "real-page detection is still not active",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be authorized but not opened",
        "page detection execution allowed: false",
        "metadata-only detection contract",
        "current URL, page title, ready state, and window count only",
        "no DOM scraping",
        "no prompt text extraction",
        "no conversation reading",
        "no Microsoft Edge start",
        "no Selenium import",
        "no ChatGPT interaction",
        "no page inspection",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L16.5 Microsoft Edge first controlled real-page metadata detection proof",
    ]:
        assert phrase in text
