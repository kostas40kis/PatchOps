from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_authorization_fixture_matrix_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l3_5_fixture_matrix_contract_gate_payload_passes() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L3.5"
    assert payload["phase"] == "L3"
    assert payload["next_patch"] == "L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback"
    assert payload["startup_authorized"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["case_count"] == 5
    assert payload["missing_case_ids"] == []
    assert payload["missing_repo_paths"] == []
    assert "unsupported_browser_rejected" in payload["invalid_cases"]
    assert "shared_profile_rejected" in payload["invalid_cases"]
    assert "opera_ack_all_permission_flags_modelled_only" in payload["side_effect_request_cases"]
    assert "download_paste_send_side_effects_blocked" in payload["side_effect_request_cases"]
    assert "selenium" not in sys.modules


def test_l3_5_fixture_matrix_contract_gate_check_names() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}
    required = {
        "l3_browser_start_authorization_fixture_matrix_still_passes",
        "l3_browser_start_authorization_fixture_matrix_core_cases_present",
        "l3_browser_start_authorization_fixture_matrix_all_expectations_met",
        "l3_browser_start_authorization_contract_gate_blocks_startup",
        "l3_browser_start_authorization_contract_gate_creates_no_browser_session",
        "l3_browser_start_authorization_contract_gate_creates_no_profile_directory",
        "l3_browser_start_authorization_contract_gate_requested_side_effects_modelled_not_executed",
        "l3_browser_start_authorization_contract_gate_invalid_requests_blocked_without_side_effects",
        "l3_browser_start_authorization_contract_gate_payload_json_safe",
        "l3_browser_start_authorization_contract_gate_required_repo_paths_present",
        "l3_browser_start_authorization_contract_gate_no_optional_browser_dependency_imports_present",
        "l3_browser_start_authorization_contract_gate_did_not_load_optional_browser_dependencies",
    }
    assert required.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required)


def test_l3_5_fixture_matrix_contract_gate_json_module_cli() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate",
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
    assert payload["patch"] == "L3.5"
    assert payload["case_count"] == 5
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []


def test_l3_5_fixture_matrix_contract_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate",
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
    assert "L3.5 Browser Start Authorization Fixture Matrix Contract Gate" in stdout
    assert "Patch      : L3.5" in stdout
    assert "Status     : PASS" in stdout
    assert "Startup    : authorized=false" in stdout
    assert "Browser    : started=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Next patch : L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback" in stdout


def test_l3_5_fixture_matrix_contract_gate_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    payload = gate.build_contract_gate(PROJECT_ROOT)
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert payload["ok"] is True
    assert imported == set()


def test_l3_5_fixture_matrix_contract_gate_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate.md"
    runner = PROJECT_ROOT / "docs" / "llm_browser_runner.md"
    assert canonical.exists()
    assert runner.exists()
    canonical_text = canonical.read_text(encoding="utf-8")
    runner_text = runner.read_text(encoding="utf-8")
    required = [
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in canonical_text
    assert "PATCHOPS_L3_05_BROWSER_START_AUTHORIZATION_FIXTURE_MATRIX_CONTRACT_GATE_START" in runner_text
    assert "live_adapter_browser_start_authorization_fixture_matrix_contract_gate" in runner_text
