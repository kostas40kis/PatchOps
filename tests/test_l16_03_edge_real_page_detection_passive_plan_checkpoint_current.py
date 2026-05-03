from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_real_page_detection_passive_plan_checkpoint as l16_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
L15_5_COMMAND = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"


def _assert_passive(payload: dict) -> None:
    assert payload["nested_cli_readbacks_performed"] is False
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


def test_l16_03_passive_plan_checkpoint_is_green_fast_and_passive() -> None:
    payload = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.3"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_1_command_name"] == L16_1_COMMAND
    assert payload["l15_5_command_name"] == L15_5_COMMAND
    assert payload["source_patch"] == "L16.2"
    assert payload["passive_plan_checkpoint"] is True
    assert payload["source_l16_2_cli_readback_checkpoint_surface_present"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["target_url_allowlist_enforced"] is True
    assert payload["target_url_status"]["ok"] is True
    assert payload["chatgpt_url_selected_for_future_detection"] is True
    assert payload["future_detection_plan_is_passive"] is True
    assert payload["future_detection_plan_is_metadata_only"] is True
    assert payload["l16_3_complete"] is True
    assert payload["remaining_l16_3_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert len(payload["future_detection_plan"]) == 6
    _assert_passive(payload)


def test_l16_03_rejects_non_allowlisted_future_target_without_browser_start() -> None:
    payload = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(
        PROJECT_ROOT,
        target_url="https://example.com/",
    )
    assert payload["ok"] is False
    assert payload["target_url_status"]["ok"] is False
    assert payload["target_url_status"]["host"] == "example.com"
    assert payload["browser_started"] is False
    assert payload["page_inspection_performed"] is False
    _assert_passive(payload)


def test_l16_03_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_1_COMMAND in names
    assert L15_5_COMMAND in names


def test_l16_03_cli_compact_json_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L16.3"
    assert payload["nested_cli_readbacks_performed"] is False
    assert payload["future_detection_plan_is_passive"] is True
    assert payload["future_detection_plan_is_metadata_only"] is True
    _assert_passive(payload)


def test_l16_03_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_03_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.3 Microsoft Edge real-page detection passive plan checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        L16_1_COMMAND,
        L15_5_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "passive plan checkpoint",
        "nested CLI readbacks are not performed",
        "real-page detection is still not active",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be planned but not opened",
        "page detected means URL/title/readiness metadata only",
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
        "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate",
    ]:
        assert phrase in text
