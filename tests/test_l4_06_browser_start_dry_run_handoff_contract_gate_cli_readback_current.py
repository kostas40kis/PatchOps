from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-dry-run-handoff-contract-gate"


def test_l4_6_dry_run_handoff_contract_gate_cli_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert "browser-start-dry-run-handoff" in names
    assert "browser-start-dry-run-handoff-fixtures" in names


def test_l4_6_dry_run_handoff_contract_gate_cli_json_readback_passes() -> None:
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
    assert payload["patch"] == "L4.5"
    assert payload["phase"] == "L4"
    assert payload["next_patch"] == "L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False


def test_l4_6_dry_run_handoff_contract_gate_cli_text_readback_is_operator_safe() -> None:
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
    assert "L4.5 Browser Start Dry-Run Handoff Fixture Matrix Contract Gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Browser Started : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback" in stdout
    forbidden = [
        "Starting browser",
        "webdriver",
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


def test_l4_6_dry_run_handoff_contract_gate_cli_preserves_module_readback() -> None:
    module_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate",
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
        "source_matrix_patch",
        "source_matrix_status",
        "browser_started",
        "profile_directory_created",
        "selenium_imported",
        "side_effects_performed",
        "filesystem_writes_performed",
    ]
    for key in comparable:
        assert cli_payload[key] == module_payload[key]


def test_l4_6_dry_run_handoff_contract_gate_cli_help_mentions_command() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0
    assert COMMAND in completed.stdout


def test_l4_6_dry_run_handoff_contract_gate_cli_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    from patchops.llm_browser import commands

    assert COMMAND in commands.llm_browser_command_names()
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l4_6_dry_run_handoff_contract_gate_cli_docs_are_present_and_passive() -> None:
    doc_path = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_contract_gate_cli_readback.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    required = [
        "L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback",
        COMMAND,
        "dry-run-only",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L4.7 Live adapter browser-start dry-run handoff L4 aggregate readiness gate",
    ]
    for phrase in required:
        assert phrase in text
