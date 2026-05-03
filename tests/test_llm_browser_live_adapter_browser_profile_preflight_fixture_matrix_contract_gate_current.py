from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_preflight_fixture_matrix_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_profile_fixture_matrix_contract_gate_payload_passes() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L2.5"
    assert payload["phase"] == "L2"
    assert payload["next_patch"] == "L2.6 Live adapter browser profile preflight fixture matrix contract gate CLI/readback"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["case_count"] == 6
    assert payload["missing_core_cases"] == []
    assert payload["invalid_cases"] == ["invalid_browser_send_request"]
    assert "opera_acknowledged_start_and_profile_request" in payload["requested_side_effect_cases"]
    assert "selenium" not in sys.modules


def test_l2_profile_fixture_matrix_contract_gate_check_names() -> None:
    payload = gate.build_contract_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}
    required = {
        "l2_profile_fixture_matrix_still_passes",
        "l2_profile_fixture_matrix_contract_gate_core_cases_present",
        "l2_profile_fixture_matrix_contract_gate_all_cases_pass",
        "l2_profile_fixture_matrix_contract_gate_blocks_startup",
        "l2_profile_fixture_matrix_contract_gate_creates_no_browser_session",
        "l2_profile_fixture_matrix_contract_gate_creates_no_profile_directory",
        "l2_profile_fixture_matrix_contract_gate_requested_side_effects_modelled_not_executed",
        "l2_profile_fixture_matrix_contract_gate_invalid_browser_reported_without_side_effects",
        "l2_profile_fixture_matrix_contract_gate_profile_paths_modelled_only",
        "l2_profile_fixture_matrix_contract_gate_payload_json_safe",
        "no_optional_browser_dependency_imports",
        "l2_profile_fixture_matrix_contract_gate_did_not_load_browser_optional_modules",
    }
    assert required.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required)


def test_l2_profile_fixture_matrix_contract_gate_json_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight_fixture_matrix_contract_gate",
            "--repo-root",
            str(PROJECT_ROOT),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["name"] == "llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate"
    assert payload["side_effects_performed"] == []
    assert payload["fixture_matrix"]["ok"] is True


def test_l2_profile_fixture_matrix_contract_gate_text_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight_fixture_matrix_contract_gate",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "PatchOps LLM browser profile preflight fixture matrix contract gate" in result.stdout
    assert "Status     : PASS" in result.stdout
    assert "BrowserRun : not started" in result.stdout
    assert "Profile    : created=false" in result.stdout
    assert "Next patch : L2.6 Live adapter browser profile preflight fixture matrix contract gate CLI/readback" in result.stdout
