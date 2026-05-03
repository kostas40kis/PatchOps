from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-l5-readiness-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-l5-readiness"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_19_edge_l5_aggregate_readiness_cli_readback_payload_is_passive_and_edge_first() -> None:
    payload = readback.build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.19"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.20 Live adapter Microsoft Edge supervised launch L5 documentation checkpoint"

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
        "l5_18_edge_l5_aggregate_readiness_gate_still_passes",
        "l5_18_patch_chain_l5_11_through_l5_17_still_passes",
        "l5_18_source_command_still_registered",
        "l5_19_edge_l5_aggregate_readback_command_registered",
        "edge_required_command_set_registered",
        "l5_19_artifacts_present",
        "edge_aggregate_readiness_remains_passive",
        "edge_remains_first_supported_live_browser",
        "opera_remains_second_supported_live_browser",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_19_wraps_accepted_l5_18_aggregate_gate() -> None:
    payload = readback.build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(PROJECT_ROOT)
    aggregate = payload["edge_l5_aggregate_readiness_summary"]
    source_payload = payload["l5_18_edge_l5_aggregate_readiness_gate"]

    assert aggregate["ok"] is True
    assert aggregate["status"] == "PASS"
    assert aggregate["patch"] == "L5.18"
    assert aggregate["command_name"] == SOURCE_COMMAND
    assert aggregate["edge_first"] is True
    assert aggregate["browser_priority"] == ["edge", "opera"]
    assert aggregate["chain_length"] == 7
    assert aggregate["missing_repo_paths"] == []
    assert aggregate["selenium_imported_by_readback"] is False
    assert aggregate["startup_authorized"] is False
    assert aggregate["startup_allowed"] is False
    assert aggregate["browser_started"] is False
    assert aggregate["edge_process_started"] is False
    assert aggregate["browser_session_created"] is False
    assert aggregate["driver_created"] is False
    assert aggregate["profile_directory_created"] is False
    assert aggregate["side_effects_performed"] == []
    assert aggregate["adapter_filesystem_writes_performed"] == []
    assert aggregate["filesystem_writes_performed"] == []

    assert source_payload["ok"] is True
    assert source_payload["status"] == "PASS"
    assert source_payload["patch"] == "L5.18"
    assert source_payload["next_patch"] == "L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback"


def test_l5_19_patch_chain_covers_l5_11_through_l5_17() -> None:
    payload = readback.build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(PROJECT_ROOT)
    chain = payload["edge_l5_aggregate_readiness_summary"]["patch_status_chain"]
    expected = list(readback.REQUIRED_PATCH_STATUS_CHAIN)
    assert [(item["expected_patch"], item["label"]) for item in chain] == expected
    for item, (expected_patch, _expected_label) in zip(chain, expected):
        assert item["actual_patch"] == expected_patch
        assert item["ok"] is True
        assert item["status"] == "PASS"
        assert item["passive_ok"] is True


def test_l5_19_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    command_names = set(commands.llm_browser_command_names())
    for command in readback.REQUIRED_COMMANDS:
        assert command in command_names
    subcommands = _subcommands(commands.build_parser())
    for command in readback.REQUIRED_COMMANDS:
        assert command in subcommands


def test_l5_19_main_cli_readback_is_passive_json() -> None:
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
    assert payload["patch"] == "L5.19"
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert payload["edge_l5_aggregate_readiness_summary"]["status"] == "PASS"
    assert len(payload["edge_l5_aggregate_readiness_summary"]["patch_status_chain"]) == 7


def test_l5_19_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback",
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
    assert "PatchOps L5.19 Microsoft Edge supervised-launch L5 aggregate readiness gate CLI/readback" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-edge-l5-readiness-readback" in stdout
    assert "Source Command  : browser-start-supervised-launch-edge-l5-readiness" in stdout
    assert "Aggregate Patch : L5.18" in stdout
    assert "Aggregate Status: PASS" in stdout
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
    assert "Next Patch      : L5.20 Live adapter Microsoft Edge supervised launch L5 documentation checkpoint" in stdout


def test_l5_19_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = readback.build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_19_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.19 Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback",
        "browser-start-supervised-launch-edge-l5-readiness-readback",
        "browser-start-supervised-launch-edge-l5-readiness",
        "L5.18",
        "L5.11",
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
        "L5.20 Live adapter Microsoft Edge supervised launch L5 documentation checkpoint",
    ]
    for phrase in required:
        assert phrase in text