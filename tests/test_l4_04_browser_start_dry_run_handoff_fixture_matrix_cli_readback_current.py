from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-dry-run-handoff-fixtures"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l4_4_fixture_matrix_cli_command_is_registered() -> None:
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l4_4_fixture_matrix_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L4.3"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback"
    assert payload["case_count"] >= 4
    assert payload["dry_run_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []


def test_l4_4_fixture_matrix_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L4.3 Browser Start Dry-Run Handoff Fixture Matrix" in stdout
    assert "Status          : PASS" in stdout
    assert "Browser Started : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback" in stdout


def test_l4_4_fixture_matrix_cli_matches_module_json() -> None:
    module_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures", "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    cli_completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert module_completed.returncode == 0, module_completed.stderr
    assert cli_completed.returncode == 0, cli_completed.stderr
    module_payload = json.loads(module_completed.stdout)
    cli_payload = json.loads(cli_completed.stdout)
    assert cli_payload["name"] == module_payload["name"]
    assert cli_payload["patch"] == module_payload["patch"]
    assert cli_payload["status"] == module_payload["status"]
    assert cli_payload["case_count"] == module_payload["case_count"]
    assert cli_payload["side_effects_performed"] == module_payload["side_effects_performed"]
    assert cli_payload["filesystem_writes_performed"] == module_payload["filesystem_writes_performed"]


def test_l4_4_fixture_matrix_cli_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    commands = _commands()
    result = commands.main([COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"])
    assert result == 0
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l4_4_command_plan_stays_readback_only() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    command_text = "\n".join(payload["readback_commands"]).lower()
    assert "live_adapter_browser_start_dry_run_handoff_fixtures" in command_text
    assert "--browser edge" in command_text
    assert "--browser opera" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "selenium" not in command_text
    assert "webdriver" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l4_4_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_cli_readback.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "browser-start-dry-run-handoff-fixtures",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L4.5 Live adapter browser-start dry-run handoff fixture matrix contract gate",
    ]
    for phrase in required:
        assert phrase in text
