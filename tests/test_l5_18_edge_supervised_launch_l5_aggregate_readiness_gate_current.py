from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-l5-readiness"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_18_edge_l5_aggregate_readiness_gate_payload_is_passive_and_edge_first() -> None:
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.18"
    assert payload["command_name"] == COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback"

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
        "l5_11_through_l5_17_edge_patch_chain_still_passes",
        "edge_required_command_set_registered",
        "l5_18_edge_aggregate_readiness_command_registered",
        "edge_required_source_docs_tests_present",
        "edge_readiness_contract_still_blocks_live_startup",
        "edge_fixture_contract_gate_still_passes",
        "edge_stream_payloads_all_remain_passive",
        "edge_remains_first_supported_live_browser",
        "opera_remains_second_supported_live_browser",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_18_patch_chain_covers_l5_11_through_l5_17() -> None:
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    chain = payload["patch_status_chain"]
    expected = [
        ("L5.11", "l5_11_broad_validation_cli_readback"),
        ("L5.12", "edge_readiness_contract"),
        ("L5.13", "edge_readiness_cli_readback"),
        ("L5.14", "edge_fixture_matrix"),
        ("L5.15", "edge_fixture_matrix_cli_readback"),
        ("L5.16", "edge_fixture_matrix_contract_gate"),
        ("L5.17", "edge_fixture_matrix_contract_gate_cli_readback"),
    ]
    assert [(item["expected_patch"], item["label"]) for item in chain] == expected
    for item in chain:
        assert item["actual_patch"] == item["expected_patch"]
        assert item["ok"] is True
        assert item["status"] == "PASS"
        assert item["passive_ok"] is True


def test_l5_18_edge_contract_and_fixture_gate_boundaries_remain_intact() -> None:
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    edge_contract = payload["edge_readiness_contract_summary"]
    fixture_gate = payload["edge_fixture_contract_gate_summary"]

    assert edge_contract["browser"] == "edge"
    assert edge_contract["edge_is_first_supported_live_browser"] is True
    assert edge_contract["opera_is_second_supported_live_browser"] is True
    assert edge_contract["dedicated_profile_required_before_live_start"] is True
    assert edge_contract["default_browser_profile_forbidden"] is True
    assert edge_contract["manual_user_login_required"] is True
    assert edge_contract["silent_auto_submit_default"] is True
    assert edge_contract["browser_extension_required"] is True
    assert edge_contract["localhost_patchops_server_required"] is True
    assert edge_contract["current_patch_launches_browser"] is True
    assert edge_contract["current_patch_imports_selenium"] is True
    assert edge_contract["current_patch_creates_profile_directory"] is True
    assert edge_contract["download_click_allowed_in_this_patch"] is True
    assert edge_contract["pasteback_insert_allowed_in_this_patch"] is True
    assert edge_contract["package_run_allowed_from_adapter_in_this_patch"] is True

    assert fixture_gate["ok"] is True
    assert fixture_gate["status"] == "PASS"
    assert fixture_gate["case_count"] == 6
    assert fixture_gate["missing_case_ids"] == []
    assert fixture_gate["unexpected_case_ids"] == []
    assert fixture_gate["violations"] == []
    assert fixture_gate["edge_first_required"] is True
    assert fixture_gate["dedicated_profile_required"] is True
    assert fixture_gate["manual_user_login_required"] is True
    assert fixture_gate["silent_auto_submit_must_remain_false"] is True
    assert fixture_gate["no_extension_required"] is True
    assert fixture_gate["no_localhost_server_required"] is True
    assert fixture_gate["current_patch_must_remain_passive"] is True


def test_l5_18_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    command_names = set(commands.llm_browser_command_names())
    for command in gate.REQUIRED_COMMANDS:
        assert command in command_names
    subcommands = _subcommands(commands.build_parser())
    for command in gate.REQUIRED_COMMANDS:
        assert command in subcommands


def test_l5_18_main_cli_readback_is_passive_json() -> None:
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
    assert payload["patch"] == "L5.18"
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert payload["edge_fixture_contract_gate_summary"]["status"] == "PASS"
    assert len(payload["patch_status_chain"]) == 7


def test_l5_18_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate",
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
    assert "PatchOps L5.18 Microsoft Edge supervised-launch L5 aggregate readiness gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-l5-readiness" in stdout
    assert "Browser Priority: ['edge', 'opera']" in stdout
    assert "L5.11: ok=True status=PASS passive=True" in stdout
    assert "L5.17: ok=True status=PASS passive=True" in stdout
    assert "Browser Started : False" in stdout
    assert "Edge Started    : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback" in stdout


def test_l5_18_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_18_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.18 Microsoft Edge supervised launch L5 aggregate readiness gate",
        "browser-start-supervised-launch-edge-l5-readiness",
        "L5.11",
        "L5.12",
        "L5.13",
        "L5.14",
        "L5.15",
        "L5.16",
        "L5.17",
        "Microsoft Edge first",
        "Opera second",
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
        "L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in text


def test_l5_18a_uses_accepted_l5_11_builder_name() -> None:
    module_path = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py"
    text = module_path.read_text(encoding="utf-8")
    assert "build_l5_broad_validation_cli_readback(root)" in text
    assert "build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)" not in text


def test_l5_18b_legacy_l5_11_missing_edge_process_field_is_passive() -> None:
    payload = gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(PROJECT_ROOT)
    l5_11_summary = payload["patch_summaries"]["l5_11_broad_validation_cli_readback"]
    assert l5_11_summary["patch"] == "L5.11"
    assert l5_11_summary["ok"] is True
    assert l5_11_summary["status"] == "PASS"
    assert l5_11_summary["passive_ok"] is True
    assert l5_11_summary["passive_state"]["edge_process_started"] is True
    assert payload["patch_status_chain"][0]["passive_ok"] is True
    assert payload["ok"] is True
    assert payload["status"] == "PASS"


def test_l5_18b_aggregate_module_keeps_l5_18a_builder_name_repair() -> None:
    module_path = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py"
    text = module_path.read_text(encoding="utf-8")
    assert "build_l5_broad_validation_cli_readback(root)" in text
    assert "build_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback(root)" not in text
    assert 'payload.get("edge_process_started", False) is False' in text

