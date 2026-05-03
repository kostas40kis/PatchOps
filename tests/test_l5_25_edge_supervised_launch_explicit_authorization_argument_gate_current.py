from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_explicit_authorization_argument_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-preflight-readback"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_25_authorization_gate_payload_without_flag_blocks_startup() -> None:
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT, allow_live_start=False)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.25"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.26 Live adapter Microsoft Edge supervised launch dedicated profile argument gate"

    assert payload["explicit_operator_authorization_required"] is True
    assert payload["explicit_operator_authorization_present"] is False
    assert payload["authorization_flag_required"] == "--allow-live-start"
    assert payload["authorization_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
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
        "l5_24_edge_live_start_preflight_cli_readback_still_passes",
        "l5_24_edge_live_start_preflight_cli_readback_remains_passive",
        "l5_24_source_command_still_registered",
        "l5_25_authorization_gate_command_registered",
        "edge_l5_required_command_set_registered",
        "edge_l5_required_source_docs_tests_present",
        "edge_l5_docs_contain_authorization_gate_boundary",
        "l5_25_command_plan_is_readback_only",
        "adapter_logic_executes_no_validation_commands",
        "authorization_argument_gate_is_enforced",
        "missing_authorization_blocks_startup",
        "present_authorization_still_cannot_start_edge_in_l5_25",
        "edge_remains_first_supported_live_browser",
        "opera_remains_second_supported_live_browser",
        "selenium_not_imported_by_authorization_gate",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_25_authorization_gate_payload_with_flag_is_authorized_but_still_passive() -> None:
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT, allow_live_start=True)
    auth = payload["authorization_gate"]

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["explicit_operator_authorization_present"] is True
    assert payload["startup_authorized"] is True
    assert payload["live_start_requested"] is True
    assert payload["authorization_gate_status"] == "AUTHORIZED_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE"
    assert auth["authorization_present_is_still_blocked_by_current_passive_phase"] is True
    assert auth["phase_allows_live_start"] is False

    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_25_wraps_accepted_l5_24_preflight_cli_readback() -> None:
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT)
    summary = payload["l5_24_summary"]
    source = payload["l5_24_edge_live_start_preflight_cli_readback"]

    assert summary["ok"] is True
    assert summary["status"] == "PASS"
    assert summary["patch"] == "L5.24"
    assert summary["command_name"] == SOURCE_COMMAND
    assert summary["l5_23_patch"] == "L5.23"
    assert summary["l5_23_status"] == "PASS"
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
    assert source["patch"] == "L5.24"


def test_l5_25_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    names = set(commands.llm_browser_command_names())
    subcommands = _subcommands(commands.build_parser())
    for command in gate.REQUIRED_COMMANDS:
        assert command in names
        assert command in subcommands


def test_l5_25_command_plan_is_readback_only() -> None:
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT)
    state = payload["command_plan_state"]
    plan = payload["command_plan"]

    assert state["ok"] is True
    assert state["forbidden_present"] == []
    assert state["missing_fragments"] == []
    assert state["executed_by_adapter_logic"] == []
    assert payload["executed_validation_commands"] == []
    assert len(plan) == 6
    assert any("compileall patchops/llm_browser tests" in command for command in plan)
    assert any("test_l5_24_edge_supervised_launch_live_start_preflight_cli_readback_current.py" in command for command in plan)
    assert any("test_l5_25_edge_supervised_launch_explicit_authorization_argument_gate_current.py" in command for command in plan)
    assert any("live_adapter_edge_supervised_launch_explicit_authorization_argument_gate" in command for command in plan)
    assert any(COMMAND in command for command in plan)
    assert any("--allow-live-start" in command for command in plan)
    assert any("git status --short --branch" in command for command in plan)


def test_l5_25_main_cli_without_flag_blocks_startup_json() -> None:
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
    assert payload["patch"] == "L5.25"
    assert payload["explicit_operator_authorization_present"] is False
    assert payload["authorization_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_25_main_cli_with_flag_still_does_not_start_edge_json() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
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
    assert payload["patch"] == "L5.25"
    assert payload["explicit_operator_authorization_present"] is True
    assert payload["authorization_gate_status"] == "AUTHORIZED_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE"
    assert payload["startup_authorized"] is True
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is True
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_25_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_explicit_authorization_argument_gate",
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps L5.25 Microsoft Edge supervised-launch explicit authorization argument gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-live-start-authorization-gate" in stdout
    assert "Source Command  : browser-start-supervised-launch-edge-live-start-preflight-readback" in stdout
    assert "Auth Required   : True" in stdout
    assert "Auth Present    : True" in stdout
    assert "Auth Flag       : --allow-live-start" in stdout
    assert "Gate Status     : AUTHORIZED_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE" in stdout
    assert "Startup Allowed : False" in stdout
    assert "Live Performed  : False" in stdout
    assert "Browser Started : False" in stdout
    assert "Edge Started    : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.26 Live adapter Microsoft Edge supervised launch dedicated profile argument gate" in stdout


def test_l5_25_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT, allow_live_start=True)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_25_docs_are_present_and_passive() -> None:
    payload = gate.build_edge_supervised_launch_explicit_authorization_argument_gate(PROJECT_ROOT)
    doc_state = payload["doc_state"]
    assert doc_state["ok"] is True
    assert doc_state["missing_docs"] == []
    assert doc_state["missing_phrases"] == {}

    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_explicit_authorization_argument_gate.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.25 Microsoft Edge supervised launch explicit authorization argument gate",
        "browser-start-supervised-launch-edge-live-start-authorization-gate",
        "browser-start-supervised-launch-edge-live-start-preflight-readback",
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "explicit operator authorization required",
        "explicit operator authorization present",
        "authorization missing keeps startup blocked",
        "authorization present is still blocked by the current passive phase",
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
        "L5.26 Live adapter Microsoft Edge supervised launch dedicated profile argument gate",
    ]
    for phrase in required:
        assert phrase in text