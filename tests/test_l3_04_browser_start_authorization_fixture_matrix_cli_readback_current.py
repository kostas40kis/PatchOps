from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-authorization-fixtures"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l3_4_fixture_matrix_cli_command_is_registered() -> None:
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l3_4_fixture_matrix_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L3.3"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L3.4 Live adapter browser-start authorization fixture matrix CLI/readback"
    assert payload["case_count"] >= 5
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["forbidden_optional_browser_imports_loaded"] == []


def test_l3_4_fixture_matrix_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L3.3 Browser Start Authorization Fixture Matrix" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : started=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Next patch : L3.4 Live adapter browser-start authorization fixture matrix CLI/readback" in stdout


def test_l3_4_fixture_matrix_cli_matches_module_json() -> None:
    module_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_browser_start_authorization_fixtures", "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
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
    assert cli_payload["case_ids"] == module_payload["case_ids"]
    assert cli_payload["side_effects_performed"] == module_payload["side_effects_performed"]


def test_l3_4_fixture_matrix_cli_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    commands = _commands()
    result = commands.main([COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"])
    assert result == 0
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l3_4_fixture_matrix_cli_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_authorization_fixture_matrix_cli_readback.md"
    runner = PROJECT_ROOT / "docs" / "llm_browser_runner.md"
    assert canonical.exists()
    assert runner.exists()
    canonical_text = canonical.read_text(encoding="utf-8")
    runner_text = runner.read_text(encoding="utf-8")
    required = [
        "browser-start-authorization-fixtures",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L3.5 Live adapter browser-start authorization fixture matrix contract gate",
    ]
    for phrase in required:
        assert phrase in canonical_text
    assert "PATCHOPS_L3_04_BROWSER_START_AUTHORIZATION_FIXTURE_MATRIX_CLI_READBACK_START" in runner_text
    assert "browser-start-authorization-fixtures" in runner_text
