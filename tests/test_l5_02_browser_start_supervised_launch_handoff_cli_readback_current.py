from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

COMMAND = "browser-start-supervised-launch-handoff"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_02_supervised_launch_handoff_cli_command_is_registered() -> None:
    commands = _commands()
    assert COMMAND in commands.llm_browser_command_names()
    assert COMMAND in _subcommands(commands.build_parser())


def test_l5_02_cli_json_readback_is_passive_for_edge() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--operator-decision",
            "review_only",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L5.1"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L5.2 Live adapter browser-start supervised launch handoff CLI/readback"
    assert payload["browser"] == "edge"
    assert payload["operator_decision"] == "review_only"
    assert payload["modelled_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_driver_session_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []


def test_l5_02_cli_json_readback_is_passive_for_opera_prepare_only() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "opera",
            "--operator-decision",
            "prepare_only",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["browser"] == "opera"
    assert payload["operator_decision"] == "prepare_only"
    assert payload["handoff_request"]["modelled_only"] is True
    assert payload["handoff_request"]["startup_allowed"] is False
    assert payload["handoff_request"]["live_driver_session_allowed"] is False
    assert payload["handoff_request"]["profile_directory_creation_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_l5_02_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--operator-decision",
            "review_only",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L5.1 Browser Start Supervised Launch Handoff Contract" in stdout
    assert "Status              : PASS" in stdout
    assert "Browser Started     : False" in stdout
    assert "Startup Allowed     : False" in stdout
    assert "Selenium Imported   : False" in stdout
    assert "Next Patch          : L5.2 Live adapter browser-start supervised launch handoff CLI/readback" in stdout


def test_l5_02_cli_matches_module_json() -> None:
    module_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract",
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--operator-decision",
            "review_only",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    cli_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--operator-decision",
            "review_only",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert module_completed.returncode == 0, module_completed.stderr
    assert cli_completed.returncode == 0, cli_completed.stderr
    assert json.loads(cli_completed.stdout) == json.loads(module_completed.stdout)


def test_l5_02_cli_does_not_import_selenium_or_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    commands = _commands()
    result = commands.main([
        COMMAND,
        "--repo-root",
        str(PROJECT_ROOT),
        "--browser",
        "edge",
        "--operator-decision",
        "review_only",
        "--json",
        "--compact",
    ])
    assert result == 0
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l5_02_command_plan_stays_readback_only() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--operator-decision",
            "review_only",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    command_plan = "\n".join(payload["handoff_readback_commands"]).lower()
    forbidden = (
        "git commit",
        "git push",
        "run-package",
        "llm-browser open",
        "open --browser",
        "run-once",
        "watch-downloads",
        "start_browser",
        "webdriver",
        "selenium",
        "click_download",
        "paste_to_composer",
        "send_message",
        "send_or_submit",
    )
    assert all(fragment not in command_plan for fragment in forbidden)
