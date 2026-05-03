from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-handoff-l5-readiness"


def test_l5_8_supervised_launch_l5_readiness_cli_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert "browser-start-supervised-launch-handoff" in names
    assert "browser-start-supervised-launch-handoff-fixtures" in names
    assert "browser-start-supervised-launch-handoff-contract-gate" in names


def test_l5_8_supervised_launch_l5_readiness_cli_json_readback_passes() -> None:
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
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.7"
    assert payload["phase"] == "L5"
    assert payload["next_patch"] == "L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback"
    assert payload["source_patches"]["L5.1"]["status"] == "PASS"
    assert payload["source_patches"]["L5.2"]["registered"] is True
    assert payload["source_patches"]["L5.3"]["status"] == "PASS"
    assert payload["source_patches"]["L5.4"]["registered"] is True
    assert payload["source_patches"]["L5.5"]["status"] == "PASS"
    assert payload["source_patches"]["L5.6"]["registered"] is True
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []


def test_l5_8_supervised_launch_l5_readiness_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L5.7 Browser Start Supervised Launch Handoff L5 Aggregate Readiness Gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Patch           : L5.7" in stdout
    assert "Browser Started : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback" in stdout
    forbidden = [
        "Starting browser",
        "selenium webdriver",
        "click_download",
        "paste_to_composer",
        "send_or_submit",
        "run-package ",
        "git commit",
        "git push",
    ]
    lowered = stdout.lower()
    for fragment in forbidden:
        assert fragment.lower() not in lowered


def test_l5_8_supervised_launch_l5_readiness_cli_preserves_module_readback() -> None:
    module_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate",
            "--repo-root",
            str(PROJECT_ROOT),
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
    module_payload = json.loads(module_completed.stdout)
    cli_payload = json.loads(cli_completed.stdout)
    comparable = [
        "ok",
        "status",
        "patch",
        "phase",
        "browser_started",
        "browser_session_created",
        "driver_created",
        "profile_directory_created",
        "selenium_imported",
        "side_effects_performed",
        "filesystem_writes_performed",
        "executed_validation_commands",
        "next_patch",
    ]
    for key in comparable:
        assert cli_payload[key] == module_payload[key]


def test_l5_8_supervised_launch_l5_readiness_cli_help_mentions_command() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    assert COMMAND in completed.stdout


def test_l5_8_supervised_launch_l5_readiness_cli_does_not_import_selenium() -> None:
    code = (
        "import json, sys; "
        "before=set(sys.modules); "
        "from patchops.llm_browser import commands; "
        "after=set(sys.modules); "
        "print(json.dumps({'selenium': 'selenium' in (after-before), 'webdriver_manager': 'webdriver_manager' in (after-before), 'names': commands.llm_browser_command_names()}))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selenium"] is False
    assert payload["webdriver_manager"] is False
    assert COMMAND in payload["names"]
