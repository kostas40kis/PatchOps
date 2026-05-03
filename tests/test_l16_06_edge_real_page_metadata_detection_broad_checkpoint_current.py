from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_broad_checkpoint as l16_06

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
L16_4_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"


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


def test_l16_06_dry_broad_checkpoint_is_green_and_passive() -> None:
    payload = l16_06.build_edge_real_page_metadata_detection_broad_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L16.6"
    assert payload["phase"] == "L16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l16_4_command_name"] == L16_4_COMMAND
    assert payload["l16_3_command_name"] == L16_3_COMMAND
    assert payload["l16_2_command_name"] == L16_2_COMMAND
    assert payload["l16_1_command_name"] == L16_1_COMMAND
    assert payload["source_patch"] == "L16.5"
    assert payload["broad_checkpoint"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["dry_metadata_checkpoint"] is True
    assert payload["explicit_live_metadata_checkpoint"] is False
    assert payload["l16_3_passive_plan_checkpoint_still_green"] is True
    assert payload["l16_4_authorization_gate_still_green"] is True
    assert payload["l16_5_dry_metadata_detection_readback_still_green"] is True
    assert payload["l16_5_live_metadata_detection_green_when_requested"] is True
    assert payload["l16_1_through_l16_5_accepted"] is True
    assert payload["page_detection_execution_allowed"] is False
    assert payload["real_page_detection_active"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["chatgpt_url_opened"] is False
    assert payload["page_metadata_detection_proven"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_no_forbidden_side_effects(payload)


def test_l16_06_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L16_4_COMMAND in names
    assert L16_3_COMMAND in names
    assert L16_2_COMMAND in names
    assert L16_1_COMMAND in names


def test_l16_06_cli_dry_compact_json_is_parseable() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L16.6"
    assert payload["l16_1_through_l16_5_accepted"] is True
    assert payload["page_detection_execution_allowed"] is False
    assert payload["browser_started"] is False
    _assert_no_forbidden_side_effects(payload)


def test_l16_06_does_not_import_optional_browser_dependencies_in_dry_checkpoint() -> None:
    before = set(sys.modules)
    payload = l16_06.build_edge_real_page_metadata_detection_broad_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l16_06_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_real_page_metadata_detection_broad_checkpoint.md").read_text(encoding="utf-8")
    for phrase in [
        "L16.6 Microsoft Edge real-page metadata detection broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        L16_4_COMMAND,
        L16_3_COMMAND,
        L16_2_COMMAND,
        L16_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "broad checkpoint",
        "dry metadata checkpoint",
        "explicit live metadata checkpoint",
        "L16.1 through L16.5 accepted",
        "target URL allowlist remains enforced",
        "ChatGPT URL may be opened only during explicit live checkpoint",
        "metadata-only page detection",
        "OS/window/process metadata only",
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
        "L16.7 Microsoft Edge real-page metadata detection final acceptance marker",
    ]:
        assert phrase in text
