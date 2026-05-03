from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_7_aggregate_readiness_gate_passes_without_side_effects() -> None:
    payload = gate.build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L4"
    assert payload["patch"] == "L4.7"
    assert payload["next_patch"] == "L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback"
    assert payload["source_contract_patch"] == "L4.1"
    assert payload["source_fixture_matrix_patch"] == "L4.3"
    assert payload["source_contract_gate_patch"] == "L4.5"
    assert payload["missing_repo_paths"] == []
    assert payload["missing_cli_commands"] == []
    assert payload["missing_fixture_case_ids"] == []
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
    assert payload["executed_validation_commands"] == []

    required_checks = {
        "l4_01_edge_dry_run_handoff_contract_still_passes",
        "l4_01_opera_dry_run_handoff_contract_still_passes",
        "l4_03_dry_run_handoff_fixture_matrix_still_passes",
        "l4_03_required_fixture_cases_present",
        "l4_05_dry_run_handoff_contract_gate_still_passes",
        "l4_cli_readback_commands_remain_registered",
        "l4_required_source_docs_tests_present",
        "l4_command_plan_is_readback_only",
        "l4_aggregate_keeps_all_live_side_effects_blocked",
        "l4_aggregate_no_optional_browser_dependency_imports_present",
        "l4_aggregate_did_not_load_optional_browser_dependencies",
        "l4_aggregate_payload_json_safe",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l4_7_aggregate_readiness_gate_required_cli_commands_present() -> None:
    payload = gate.build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert "browser-start-dry-run-handoff" in payload["required_cli_commands"]
    assert "browser-start-dry-run-handoff-fixtures" in payload["required_cli_commands"]
    assert "browser-start-dry-run-handoff-contract-gate" in payload["required_cli_commands"]
    assert payload["missing_cli_commands"] == []


def test_l4_7_aggregate_readiness_gate_module_json_cli() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate",
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
    assert payload["patch"] == "L4.7"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["selenium_imported"] is False


def test_l4_7_aggregate_readiness_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate",
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
    assert "L4.7 Browser Start Dry-Run Handoff Aggregate Readiness Gate" in stdout
    assert "Status          : PASS" in stdout
    assert "Source Contract : L4.1 / PASS" in stdout
    assert "Source Matrix   : L4.3 / PASS" in stdout
    assert "Source Gate     : L4.5 / PASS" in stdout
    assert "Browser Started : False" in stdout
    assert "Profile Created : False" in stdout
    assert "Selenium Import : False" in stdout
    assert "Next Patch      : L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback" in stdout
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


def test_l4_7_aggregate_readiness_gate_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = gate.build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate(PROJECT_ROOT)
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert payload["ok"] is True
    assert imported == set()


def test_l4_7_aggregate_readiness_gate_docs_are_present_and_passive() -> None:
    doc_path = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    required = [
        "L4.7 Live adapter browser-start dry-run handoff L4 aggregate readiness gate",
        "aggregate readiness gate",
        "dry-run-only",
        "L4.1",
        "L4.3",
        "L4.5",
        "L4.6",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in text
