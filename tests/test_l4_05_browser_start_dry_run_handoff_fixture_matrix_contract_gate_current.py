from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_payload_passes() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.5"
    assert payload["phase"] == "L4"
    assert payload["source_matrix_patch"] == "L4.3"
    assert payload["next_patch"] == "L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback"
    assert payload["case_count"] >= 4
    assert payload["missing_case_ids"] == []
    assert payload["missing_repo_paths"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["l4_04_command_registered"] is True
    assert payload["dry_run_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_check_names() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}
    required = {
        "l4_dry_run_handoff_fixture_matrix_still_passes",
        "l4_dry_run_handoff_fixture_matrix_core_cases_present",
        "l4_dry_run_handoff_fixture_matrix_all_cases_match_expectations",
        "l4_dry_run_handoff_contract_gate_keeps_startup_blocked",
        "l4_dry_run_handoff_contract_gate_creates_no_browser_or_driver",
        "l4_dry_run_handoff_contract_gate_creates_no_profile_or_adapter_writes",
        "l4_dry_run_handoff_contract_gate_executes_no_side_effects",
        "l4_dry_run_handoff_contract_gate_requires_no_optional_browser_dependencies",
        "l4_dry_run_handoff_contract_gate_required_repo_paths_present",
        "l4_dry_run_handoff_contract_gate_doc_contains_boundary",
        "l4_dry_run_handoff_fixture_cli_command_registered",
        "l4_dry_run_handoff_contract_gate_command_plan_is_readback_only",
        "l4_dry_run_handoff_contract_gate_no_optional_browser_imports_present",
        "l4_dry_run_handoff_contract_gate_did_not_load_optional_browser_dependencies",
        "l4_dry_run_handoff_contract_gate_payload_json_safe",
    }
    assert required.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required)


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_module_json_cli() -> None:
    completed = subprocess.run(
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
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.5"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate",
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
    assert "Source Matrix   : L4.3 / PASS" in stdout
    assert "Browser Started : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "L4.4 CLI Present: True" in stdout
    assert "Next Patch      : L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback" in stdout


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_preserves_l4_4_cli_readback() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "browser-start-dry-run-handoff-fixtures",
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
    assert payload["patch"] == "L4.3"
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = gate.build_contract_gate(PROJECT_ROOT)
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert payload["ok"] is True
    assert imported == set()


def test_l4_5_dry_run_handoff_fixture_matrix_contract_gate_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L4.5 Live adapter browser-start dry-run handoff fixture matrix contract gate",
        "dry-run-only",
        "fixture matrix contract gate",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L4.6 Live adapter browser-start dry-run handoff fixture matrix contract gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in text
