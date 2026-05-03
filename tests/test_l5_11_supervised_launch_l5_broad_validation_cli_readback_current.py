from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-handoff-l5-broad-validation"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_11_broad_validation_cli_readback_payload_is_passive_and_edge_first() -> None:
    payload = readback.build_l5_broad_validation_cli_readback(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.11"
    assert payload["repair_patch"] == "L5.11c"
    assert payload["command_name"] == COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"][0] == "edge"
    assert payload["next_patch"] == "L5.12 Live adapter Microsoft Edge supervised launch readiness contract"

    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
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
    assert payload["executed_validation_commands"] == []
    assert payload["selenium_imported_by_readback"] is False

    required_checks = {
        "l5_10_broad_validation_checkpoint_still_passes",
        "l5_11_command_static_presence",
        "accepted_prior_passive_boundaries_are_read_back",
        "l5_11_artifacts_present",
        "edge_remains_first_priority",
        "selenium_not_imported_by_readback",
        "no_browser_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_11_preserves_l5_10_and_prior_passive_boundary_readbacks() -> None:
    payload = readback.build_l5_broad_validation_cli_readback(PROJECT_ROOT)

    assert payload["l5_10_broad_validation_checkpoint"]["patch"] == "L5.10"
    assert payload["l5_10_broad_validation_checkpoint"]["ok"] is True
    assert payload["l5_10_broad_validation_checkpoint"]["status"] == "PASS"

    boundaries = payload["accepted_prior_passive_boundaries"]
    assert [item["phase"] for item in boundaries] == ["L1", "L2", "L3", "L4"]
    for marker in boundaries:
        assert marker["browser_started"] is False
        assert marker["browser_session_created"] is False
        assert marker["profile_directory_created"] is False
        assert marker["side_effects_performed"] == []
        assert marker["send_or_submit_performed"] is False


def test_l5_11_command_name_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l5_11_main_cli_readback_is_passive_json() -> None:
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
    assert payload["patch"] == "L5.11"
    assert payload["repair_patch"] == "L5.11c"
    assert payload["l5_10_broad_validation_checkpoint"]["patch"] == "L5.10"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["selenium_imported_by_readback"] is False


def test_l5_11_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback",
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
    assert "PatchOps L5.11 browser-start supervised launch broad validation CLI/readback" in stdout
    assert "Repair Patch    : L5.11c" in stdout
    assert "Status          : PASS" in stdout
    assert "Command         : browser-start-supervised-launch-handoff-l5-broad-validation" in stdout
    assert "Edge First      : True" in stdout
    assert "Browser Started : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Filesystem      : writes=[]" in stdout
    assert "Adapter Writes  : []" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.12 Live adapter Microsoft Edge supervised launch readiness contract" in stdout


def test_l5_11_module_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = readback.build_l5_broad_validation_cli_readback(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_11_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback",
        "L5.11c direct-manifest repair",
        "browser-start-supervised-launch-handoff-l5-broad-validation",
        "L5.10 broad validation checkpoint",
        "L1.17",
        "L2.12d",
        "L3.12",
        "L4.12",
        "Microsoft Edge first",
        "Opera second",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L5.12 Live adapter Microsoft Edge supervised launch readiness contract",
    ]
    for phrase in required:
        assert phrase in text