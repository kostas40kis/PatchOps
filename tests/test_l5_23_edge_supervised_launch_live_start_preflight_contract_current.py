from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_live_start_preflight_contract as preflight

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-preflight"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-l5-broad-validation-readback"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_23_live_start_preflight_payload_is_passive_and_edge_first() -> None:
    payload = preflight.build_edge_supervised_launch_live_start_preflight_contract(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.23"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback"

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
        "l5_22_edge_l5_broad_validation_readback_still_passes",
        "l5_22_edge_l5_broad_validation_readback_remains_passive",
        "l5_22_source_command_still_registered",
        "l5_23_live_start_preflight_command_registered",
        "edge_l5_required_command_set_registered",
        "edge_l5_required_source_docs_tests_present",
        "edge_l5_docs_contain_preflight_boundary",
        "edge_live_start_preflight_contract_is_explicit",
        "edge_live_start_requires_explicit_operator_authorization",
        "edge_live_start_requires_dedicated_profile",
        "edge_live_start_keeps_default_profile_forbidden",
        "edge_live_start_keeps_manual_login_required",
        "edge_live_start_keeps_silent_auto_submit_false",
        "edge_live_start_requires_no_localhost_or_extension",
        "selenium_not_imported_by_preflight_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_23_wraps_accepted_l5_22_broad_validation_readback() -> None:
    payload = preflight.build_edge_supervised_launch_live_start_preflight_contract(PROJECT_ROOT)
    summary = payload["l5_22_summary"]
    source = payload["l5_22_edge_l5_broad_validation_readback"]

    assert summary["ok"] is True
    assert summary["status"] == "PASS"
    assert summary["patch"] == "L5.22"
    assert summary["command_name"] == SOURCE_COMMAND
    assert summary["l5_21_patch"] == "L5.21"
    assert summary["l5_21_status"] == "PASS"
    assert summary["l5_20_patch"] == "L5.20"
    assert summary["l5_20_status"] == "PASS"
    assert summary["l5_19_chain_length"] == 7
    assert summary["doc_state_ok"] is True
    assert summary["browser_started"] is False
    assert summary["edge_process_started"] is False
    assert summary["browser_session_created"] is False
    assert summary["profile_directory_created"] is False
    assert summary["filesystem_writes_performed"] == []
    assert summary["adapter_filesystem_writes_performed"] == []
    assert summary["side_effects_performed"] == []
    assert source["ok"] is True
    assert source["status"] == "PASS"
    assert source["patch"] == "L5.22"


def test_l5_23_live_start_preflight_contract_is_explicit() -> None:
    payload = preflight.build_edge_supervised_launch_live_start_preflight_contract(PROJECT_ROOT)
    contract = payload["live_start_preflight_contract"]

    assert contract["browser"] == "edge"
    assert contract["browser_priority"] == ["edge", "opera"]
    assert contract["edge_first"] is True
    assert contract["opera_second"] is True
    assert contract["explicit_operator_authorization_required"] is True
    assert contract["authorization_flag_required"] == "--allow-live-start"
    assert contract["profile_dir_argument_required"] == "--profile-dir"
    assert contract["dedicated_profile_required"] is True
    assert contract["default_profile_forbidden"] is True
    assert contract["manual_user_login_required"] is True
    assert contract["silent_auto_submit_default"] is False
    assert contract["silent_auto_submit_must_remain_false"] is True
    assert contract["browser_extension_required"] is False
    assert contract["localhost_patchops_server_required"] is False
    assert contract["current_patch_launches_browser"] is False
    assert contract["current_patch_imports_selenium"] is False
    assert contract["current_patch_creates_profile_directory"] is False
    assert contract["current_patch_creates_driver"] is False
    assert contract["current_patch_creates_browser_session"] is False
    assert contract["download_click_allowed_in_this_patch"] is False
    assert contract["pasteback_insert_allowed_in_this_patch"] is False
    assert contract["send_or_submit_allowed_in_this_patch"] is False
    assert contract["package_run_allowed_from_adapter_in_this_patch"] is False
    assert contract["edge_executable_candidates"] == list(preflight.EDGE_EXECUTABLE_CANDIDATES)
    assert contract["preflight_checks_modelled_only"] is True
    assert contract["filesystem_probe_required_in_this_patch"] is False


def test_l5_23_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    names = set(commands.llm_browser_command_names())
    subcommands = _subcommands(commands.build_parser())
    for command in preflight.REQUIRED_COMMANDS:
        assert command in names
        assert command in subcommands


def test_l5_23_main_cli_readback_is_passive_json() -> None:
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
    assert payload["patch"] == "L5.23"
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
    assert payload["l5_22_summary"]["status"] == "PASS"
    assert payload["doc_state"]["ok"] is True
    assert payload["live_start_preflight_contract"]["explicit_operator_authorization_required"] is True


def test_l5_23_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_live_start_preflight_contract",
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
    assert "PatchOps L5.23 Microsoft Edge supervised-launch live-start preflight contract" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-live-start-preflight" in stdout
    assert "Source Command  : browser-start-supervised-launch-edge-l5-broad-validation-readback" in stdout
    assert "Browser Priority: ['edge', 'opera']" in stdout
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
    assert "Next Patch      : L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback" in stdout


def test_l5_23_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = preflight.build_edge_supervised_launch_live_start_preflight_contract(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_23_docs_are_present_and_passive() -> None:
    payload = preflight.build_edge_supervised_launch_live_start_preflight_contract(PROJECT_ROOT)
    doc_state = payload["doc_state"]
    assert doc_state["ok"] is True
    assert doc_state["missing_docs"] == []
    assert doc_state["missing_phrases"] == {}

    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_live_start_preflight_contract.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.23 Microsoft Edge supervised launch live-start preflight contract",
        "browser-start-supervised-launch-edge-live-start-preflight",
        "browser-start-supervised-launch-edge-l5-broad-validation-readback",
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
        "L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback",
    ]
    for phrase in required:
        assert phrase in text