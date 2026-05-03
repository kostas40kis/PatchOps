from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_first_controlled_open_proof as l15_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-first-controlled-open-proof"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"


def _assert_no_chat_or_artifact_side_effects(payload: dict) -> None:
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
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


def test_l15_03_dry_readback_requires_explicit_live_open_before_starting_edge() -> None:
    payload = l15_03.build_edge_first_controlled_open_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L15.3"
    assert payload["phase"] == "L15"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l15_1_command_name"] == L15_1_COMMAND
    assert payload["source_patch"] == "L15.2"
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["explicit_live_start_authorization_flag_required"] is True
    assert payload["explicit_live_start_authorization_token_required"] is True
    assert payload["explicit_live_open_execution_flag_required"] is True
    assert payload["live_start_operator_authorization_complete"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["execute_live_open_flag_present"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["live_open_smoke_executed"] is False
    assert payload["live_open_smoke_proven"] is False
    assert payload["profile_candidate_under_allowed_runtime_root"] is True
    assert payload["default_edge_profile_rejected"] is True
    assert payload["default_profile_use_allowed"] is False
    assert payload["open_url"] == "about:blank"
    assert payload["open_url_is_about_blank"] is True
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_no_chat_or_artifact_side_effects(payload)


def test_l15_03_bad_token_with_execute_flag_does_not_allow_launch() -> None:
    payload = l15_03.build_edge_first_controlled_open_proof(
        PROJECT_ROOT,
        allow_live_start=True,
        authorization_token="WRONG",
        execute_live_open=True,
    )
    assert payload["ok"] is True
    assert payload["explicit_live_start_authorization_flag_present"] is True
    assert payload["explicit_live_start_authorization_token_present"] is False
    assert payload["execute_live_open_flag_present"] is True
    assert payload["live_start_operator_authorization_complete"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["live_open_smoke_executed"] is True
    assert payload["live_open_smoke_proven"] is False
    _assert_no_chat_or_artifact_side_effects(payload)


def test_l15_03_non_blank_url_is_rejected_before_launch() -> None:
    payload = l15_03.build_edge_first_controlled_open_proof(
        PROJECT_ROOT,
        allow_live_start=True,
        authorization_token="PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED",
        execute_live_open=True,
        open_url="https://chatgpt.com/",
    )
    assert payload["ok"] is False
    assert payload["open_url_is_about_blank"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["chatgpt_url_opened"] is False
    _assert_no_chat_or_artifact_side_effects(payload)


def test_l15_03_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names
    assert L15_1_COMMAND in names


def test_l15_03_cli_dry_compact_json_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L15.3"
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["live_open_smoke_executed"] is False
    _assert_no_chat_or_artifact_side_effects(payload)


def test_l15_03_does_not_import_optional_browser_dependencies_in_dry_readback() -> None:
    before = set(sys.modules)
    payload = l15_03.build_edge_first_controlled_open_proof(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l15_03_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_first_controlled_open_proof.md").read_text(encoding="utf-8")
    for phrase in [
        "L15.3 first controlled Microsoft Edge open proof",
        COMMAND,
        SOURCE_COMMAND,
        L15_1_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "explicit live-start authorization flag required",
        "explicit live-start authorization token required",
        "explicit live-open execution flag required",
        "dedicated L14 profile candidate required",
        "default Microsoft Edge profile rejected",
        "open URL is about:blank",
        "Selenium is not imported",
        "no ChatGPT interaction",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "close only the Edge process/profile it started",
        "L15.4 Microsoft Edge first controlled open proof broad checkpoint",
    ]:
        assert phrase in text
