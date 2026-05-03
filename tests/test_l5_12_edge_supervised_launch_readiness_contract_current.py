from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_readiness_contract as edge_contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-readiness"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_12_edge_readiness_contract_payload_is_passive_and_edge_first() -> None:
    payload = edge_contract.build_edge_supervised_launch_readiness_contract(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.12"
    assert payload["command_name"] == COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.13 Live adapter Microsoft Edge supervised launch readiness CLI/readback"

    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
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
        "l5_11_broad_validation_cli_readback_still_passes",
        "l5_12_edge_readiness_command_static_presence",
        "edge_is_first_supported_live_browser",
        "edge_readiness_contract_blocks_live_startup",
        "l5_12_artifacts_present",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_12_edge_readiness_contract_keeps_supervised_launch_user_review_boundary() -> None:
    payload = edge_contract.build_edge_supervised_launch_readiness_contract(PROJECT_ROOT)
    contract = payload["edge_readiness_contract"]

    assert contract["browser"] == "edge"
    assert contract["edge_is_first_supported_live_browser"] is True
    assert contract["launch_mode"] == "future_supervised_user_visible_launch"
    assert contract["current_patch_launches_browser"] is False
    assert contract["current_patch_imports_selenium"] is False
    assert contract["current_patch_creates_profile_directory"] is False
    assert contract["dedicated_profile_required_before_live_start"] is True
    assert contract["default_browser_profile_forbidden"] is True
    assert contract["manual_user_login_required"] is True
    assert contract["silent_auto_submit_default"] is False
    assert contract["browser_extension_required"] is False
    assert contract["localhost_patchops_server_required"] is False
    assert contract["download_click_allowed_in_this_patch"] is False
    assert contract["pasteback_insert_allowed_in_this_patch"] is False
    assert contract["package_run_allowed_from_adapter_in_this_patch"] is False
    assert "msedge.exe" in " ".join(contract["edge_executable_candidates"])


def test_l5_12_command_name_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l5_12_main_cli_readback_is_passive_json() -> None:
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
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L5.12"
    assert payload["l5_11_broad_validation_cli_readback"]["patch"] == "L5.11"
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_12_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_readiness_contract",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps L5.12 Microsoft Edge supervised-launch readiness contract" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-readiness" in stdout
    assert "Edge First      : True" in stdout
    assert "Browser Started : False" in stdout
    assert "Edge Started    : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.13 Live adapter Microsoft Edge supervised launch readiness CLI/readback" in stdout


def test_l5_12_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = edge_contract.build_edge_supervised_launch_readiness_contract(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_12_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.12 Microsoft Edge supervised launch readiness contract",
        "Microsoft Edge first",
        "Opera second",
        "browser-start-supervised-launch-edge-readiness",
        "L5.11",
        "dedicated profile required",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.13 Live adapter Microsoft Edge supervised launch readiness CLI/readback",
    ]
    for phrase in required:
        assert phrase in text