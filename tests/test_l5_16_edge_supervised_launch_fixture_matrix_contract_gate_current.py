from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_fixture_matrix_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-fixtures-contract-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-fixtures-readback"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_16_edge_fixture_matrix_contract_gate_payload_is_passive_and_edge_first() -> None:
    payload = gate.build_edge_supervised_launch_fixture_matrix_contract_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.16"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.17 Live adapter Microsoft Edge supervised launch fixture matrix contract gate CLI/readback"

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
        "l5_15_edge_fixture_matrix_cli_readback_still_passes",
        "l5_15_source_command_still_registered",
        "l5_16_edge_fixture_matrix_contract_gate_command_registered",
        "edge_fixture_matrix_contract_gate_passes",
        "edge_remains_first_supported_live_browser",
        "l5_16_artifacts_present",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_16_contract_gate_enforces_fixture_cases_and_boundaries() -> None:
    payload = gate.build_edge_supervised_launch_fixture_matrix_contract_gate(PROJECT_ROOT)
    contract_gate = payload["edge_fixture_contract_gate"]

    assert contract_gate["ok"] is True
    assert contract_gate["status"] == "PASS"
    assert contract_gate["case_count"] == 6
    assert contract_gate["missing_case_ids"] == []
    assert contract_gate["unexpected_case_ids"] == []
    assert contract_gate["violations"] == []
    assert contract_gate["required_case_ids"] == list(gate.REQUIRED_CASE_IDS)
    assert contract_gate["edge_first_required"] is True
    assert contract_gate["dedicated_profile_required"] is True
    assert contract_gate["manual_user_login_required"] is True
    assert contract_gate["silent_auto_submit_must_remain_false"] is True
    assert contract_gate["no_extension_required"] is True
    assert contract_gate["no_localhost_server_required"] is True
    assert contract_gate["current_patch_must_remain_passive"] is True


def test_l5_16_preserves_l5_15_fixture_readback_and_l5_14_matrix() -> None:
    payload = gate.build_edge_supervised_launch_fixture_matrix_contract_gate(PROJECT_ROOT)
    l5_15 = payload["l5_15_edge_fixture_matrix_cli_readback"]
    cases = {case["case_id"]: case for case in payload["edge_fixture_cases"]}

    assert l5_15["patch"] == "L5.15"
    assert l5_15["ok"] is True
    assert l5_15["status"] == "PASS"
    assert set(cases) == set(gate.REQUIRED_CASE_IDS)
    for case in cases.values():
        assert case["browser"] == "edge"
        assert case["edge_first"] is True
        assert case["dedicated_profile_required"] is True
        assert case["manual_user_login_required"] is True
        assert case["default_profile_forbidden"] is True
        assert case["silent_auto_submit_default"] is False
        assert case["browser_extension_required"] is False
        assert case["localhost_patchops_server_required"] is False
        assert case["current_patch_launches_browser"] is False
        assert case["current_patch_imports_selenium"] is False
        assert case["current_patch_creates_profile_directory"] is False
        assert case["current_patch_clicks_download"] is False
        assert case["current_patch_pastes_or_sends"] is False
        assert case["current_patch_runs_package_from_adapter"] is False
        assert case["passive_only"] is True


def test_l5_16_command_name_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    assert SOURCE_COMMAND in commands.llm_browser_command_names()
    assert COMMAND in commands.llm_browser_command_names()
    subcommands = _subcommands(commands.build_parser())
    assert SOURCE_COMMAND in subcommands
    assert COMMAND in subcommands


def test_l5_16_main_cli_readback_is_passive_json() -> None:
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
    assert payload["patch"] == "L5.16"
    assert payload["l5_15_edge_fixture_matrix_cli_readback"]["patch"] == "L5.15"
    assert payload["edge_fixture_contract_gate"]["status"] == "PASS"
    assert payload["edge_fixture_contract_gate"]["case_count"] == 6
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_16_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix_contract_gate",
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
    assert "PatchOps L5.16 Microsoft Edge supervised-launch fixture matrix contract gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-fixtures-contract-gate" in stdout
    assert "Source Command  : browser-start-supervised-launch-edge-fixtures-readback" in stdout
    assert "Gate Status     : PASS" in stdout
    assert "Case Count      : 6" in stdout
    assert "Edge First      : True" in stdout
    assert "Browser Started : False" in stdout
    assert "Edge Started    : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.17 Live adapter Microsoft Edge supervised launch fixture matrix contract gate CLI/readback" in stdout


def test_l5_16_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = gate.build_edge_supervised_launch_fixture_matrix_contract_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_16_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.16 Microsoft Edge supervised launch fixture matrix contract gate",
        "browser-start-supervised-launch-edge-fixtures-contract-gate",
        "browser-start-supervised-launch-edge-fixtures-readback",
        "L5.15",
        "Microsoft Edge first",
        "Opera second",
        "edge_future_launch_user_visible",
        "edge_dedicated_profile_required",
        "edge_manual_login_required",
        "edge_no_silent_auto_submit",
        "edge_no_extension_no_localhost",
        "edge_no_current_side_effects",
        "dedicated profile required",
        "manual user login required",
        "silent auto-submit remains false",
        "contract gate",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.17 Live adapter Microsoft Edge supervised launch fixture matrix contract gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in text