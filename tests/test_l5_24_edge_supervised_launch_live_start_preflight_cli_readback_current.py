from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_live_start_preflight_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-preflight-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-preflight"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_24_preflight_cli_readback_payload_is_passive_and_edge_first() -> None:
    payload = readback.build_edge_supervised_launch_live_start_preflight_cli_readback(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.24"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.25 Live adapter Microsoft Edge supervised launch explicit authorization argument gate"

    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["selenium_imported_by_readback"] is False

    required_checks = {
        "l5_23_edge_live_start_preflight_contract_still_passes",
        "l5_23_edge_live_start_preflight_contract_remains_passive",
        "l5_23_source_command_still_registered",
        "l5_24_live_start_preflight_readback_command_registered",
        "edge_l5_required_command_set_registered",
        "edge_l5_required_source_docs_tests_present",
        "edge_l5_docs_contain_cli_readback_boundary",
        "l5_24_command_plan_is_readback_only",
        "adapter_logic_executes_no_validation_commands",
        "edge_live_start_authorization_gate_still_required",
        "edge_live_start_dedicated_profile_gate_still_required",
        "edge_live_start_manual_login_and_no_auto_submit_still_required",
        "edge_remains_first_supported_live_browser",
        "opera_remains_second_supported_live_browser",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_24_wraps_accepted_l5_23_preflight_contract() -> None:
    payload = readback.build_edge_supervised_launch_live_start_preflight_cli_readback(PROJECT_ROOT)
    summary = payload["l5_23_summary"]
    source = payload["l5_23_edge_live_start_preflight_contract"]

    assert summary["ok"] is True
    assert summary["status"] == "PASS"
    assert summary["patch"] == "L5.23"
    assert summary["command_name"] == SOURCE_COMMAND
    assert summary["explicit_operator_authorization_required"] is True
    assert summary["authorization_flag_required"] == "--allow-live-start"
    assert summary["profile_dir_argument_required"] == "--profile-dir"
    assert summary["dedicated_profile_required"] is True
    assert summary["default_profile_forbidden"] is True
    assert summary["manual_user_login_required"] is True
    assert summary["silent_auto_submit_default"] is False
    assert summary["browser_started"] is False
    assert summary["edge_process_started"] is False
    assert summary["browser_session_created"] is False
    assert summary["profile_directory_created"] is False
    assert summary["filesystem_writes_performed"] == []
    assert summary["adapter_filesystem_writes_performed"] == []
    assert summary["side_effects_performed"] == []
    assert source["ok"] is True
    assert source["status"] == "PASS"
    assert source["patch"] == "L5.23"


def test_l5_24_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    names = set(commands.llm_browser_command_names())
    subcommands = _subcommands(commands.build_parser())
    for command in readback.REQUIRED_COMMANDS:
        assert command in names
        assert command in subcommands


def test_l5_24_command_plan_is_readback_only() -> None:
    payload = readback.build_edge_supervised_launch_live_start_preflight_cli_readback(PROJECT_ROOT)
    state = payload["command_plan_state"]
    plan = payload["command_plan"]

    assert state["ok"] is True
    assert state["forbidden_present"] == []
    assert state["missing_fragments"] == []
    assert state["executed_by_adapter_logic"] == []
    assert payload["executed_validation_commands"] == []
    assert len(plan) == 5
    assert any("compileall patchops/llm_browser tests" in command for command in plan)
    assert any("test_l5_23_edge_supervised_launch_live_start_preflight_contract_current.py" in command for command in plan)
    assert any("test_l5_24_edge_supervised_launch_live_start_preflight_cli_readback_current.py" in command for command in plan)
    assert any("live_adapter_edge_supervised_launch_live_start_preflight_cli_readback" in command for command in plan)
    assert any(COMMAND in command for command in plan)
    assert any("git status --short --branch" in command for command in plan)


def test_l5_24_main_cli_readback_is_passive_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L5.24"
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["l5_23_summary"]["status"] == "PASS"
    assert payload["l5_23_summary"]["explicit_operator_authorization_required"] is True
    assert payload["doc_state"]["ok"] is True


def test_l5_24_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_live_start_preflight_cli_readback",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps L5.24 Microsoft Edge supervised-launch live-start preflight CLI/readback" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-live-start-preflight-readback" in stdout
    assert "Source Command  : browser-start-supervised-launch-edge-live-start-preflight" in stdout
    assert "Browser Priority: ['edge', 'opera']" in stdout
    assert "L5.23 Status    : L5.23 / PASS" in stdout
    assert "Authorization   : required=True flag=--allow-live-start" in stdout
    assert "Profile         : dedicated=True default_forbidden=True" in stdout
    assert "Manual Login    : True" in stdout
    assert "Silent Submit   : False" in stdout
    assert "Browser Started : False" in stdout
    assert "Edge Started    : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.25 Live adapter Microsoft Edge supervised launch explicit authorization argument gate" in stdout


def test_l5_24_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = readback.build_edge_supervised_launch_live_start_preflight_cli_readback(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_24_docs_are_present_and_passive() -> None:
    payload = readback.build_edge_supervised_launch_live_start_preflight_cli_readback(PROJECT_ROOT)
    doc_state = payload["doc_state"]
    assert doc_state["ok"] is True
    assert doc_state["missing_docs"] == []
    assert doc_state["missing_phrases"] == {}

    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_live_start_preflight_cli_readback.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.24 Microsoft Edge supervised launch live-start preflight CLI/readback",
        "browser-start-supervised-launch-edge-live-start-preflight-readback",
        "browser-start-supervised-launch-edge-live-start-preflight",
        "Microsoft Edge first",
        "Opera second",
        "explicit operator authorization required",
        "dedicated profile required",
        "default profile forbidden",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.25 Live adapter Microsoft Edge supervised launch explicit authorization argument gate",
    ]
    for phrase in required:
        assert phrase in text