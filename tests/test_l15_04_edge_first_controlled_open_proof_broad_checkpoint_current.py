from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_first_controlled_open_proof_broad_checkpoint as l15_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-first-controlled-open-proof"
L15_2_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"


def _assert_no_chat_artifact_side_effects(payload: dict) -> None:
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["chatgpt_url_opened"] is False
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


def test_l15_04_dry_broad_checkpoint_is_green_and_passive() -> None:
    payload = l15_04.build_edge_first_controlled_open_proof_broad_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L15.4"
    assert payload["phase"] == "L15"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l15_2_command_name"] == L15_2_COMMAND
    assert payload["l15_1_command_name"] == L15_1_COMMAND
    assert payload["source_patch"] == "L15.3"
    assert payload["broad_checkpoint"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["dry_checkpoint"] is True
    assert payload["explicit_live_checkpoint"] is False
    assert payload["l15_1_authorization_gate_still_green"] is True
    assert payload["l15_2_cli_readback_still_green"] is True
    assert payload["l15_3_dry_readback_still_green"] is True
    assert payload["l15_3_cli_dry_readback_still_green"] is True
    assert payload["l15_3_live_checkpoint_green_when_requested"] is True
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["live_open_smoke_executed"] is False
    assert payload["live_open_smoke_proven"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_no_chat_artifact_side_effects(payload)


def test_l15_04_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L15_2_COMMAND in names
    assert L15_1_COMMAND in names


def test_l15_04_cli_dry_compact_json_is_parseable() -> None:
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
    assert payload["patch"] == "L15.4"
    assert payload["l15_1_authorization_gate_still_green"] is True
    assert payload["l15_2_cli_readback_still_green"] is True
    assert payload["l15_3_dry_readback_still_green"] is True
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    _assert_no_chat_artifact_side_effects(payload)


def test_l15_04_does_not_import_optional_browser_dependencies_in_dry_checkpoint() -> None:
    before = set(sys.modules)
    payload = l15_04.build_edge_first_controlled_open_proof_broad_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l15_04_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_first_controlled_open_proof_broad_checkpoint.md").read_text(encoding="utf-8")
    for phrase in [
        "L15.4 Microsoft Edge first controlled open proof broad checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        L15_2_COMMAND,
        L15_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "broad checkpoint",
        "dry checkpoint",
        "explicit live checkpoint",
        "about:blank only",
        "dedicated L14 profile only",
        "default Microsoft Edge profile rejected",
        "Selenium is not imported",
        "no ChatGPT interaction",
        "no artifact detection",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L15.5 Microsoft Edge live-start handoff marker before real-page detection",
    ]:
        assert phrase in text
