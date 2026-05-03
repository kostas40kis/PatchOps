from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_fixture_matrix_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_fixture_matrix_contract_gate_passes_without_side_effects() -> None:
    payload = gate.build_startup_request_fixture_matrix_contract_gate()
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.11"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["case_count"] >= 6
    assert "opera_all_side_effect_flags" in payload["case_names"]
    assert "invalid_browser_send_request" in payload["case_names"]

    expected_checks = [
        "fixture_matrix_payload_contract",
        "fixture_matrix_core_cases",
        "all_fixture_decisions_block_startup",
        "all_fixture_decisions_create_no_browser_session",
        "requested_side_effects_modelled_not_executed",
        "fixture_matrix_invalid_browser_reported_without_side_effects",
        "fixture_matrix_json_safe",
        "startup_request_contract_gate_still_passes",
        "no_optional_browser_dependency_imports",
        "fixture_matrix_contract_gate_did_not_load_browser_optional_modules",
        "fixture_matrix_has_core_cases",
        "fixture_matrix_readback_payload",
        "fixture_matrix_payload_contract_json_safe",
        "fixture_matrix_cases_block_startup",
        "fixture_matrix_cases_create_no_browser_session",
        "fixture_matrix_requested_side_effects_modelled_not_executed",
        "invalid_browser_fixture_reported_without_side_effects",
        "fixture_gate_did_not_load_browser_optional_modules",
    ]
    for name in expected_checks:
        assert checks[name]["ok"] is True


def test_fixture_matrix_contract_gate_json_cli_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_fixture_matrix_contract_gate",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["matrix"]["ok"] is True
    assert payload["upstream_contract_gate"]["ok"] is True


def test_fixture_matrix_contract_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_fixture_matrix_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser startup request fixture matrix contract gate" in completed.stdout
    assert "PatchOps LLM browser live adapter startup request fixture matrix contract gate" in completed.stdout
    assert "Status     : PASS" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout
    assert "fixture_matrix_has_core_cases: PASS" in completed.stdout
    assert "fixture_gate_did_not_load_browser_optional_modules: PASS" in completed.stdout
    assert "Next patch : L1.12 Live adapter startup request fixture matrix contract gate CLI/readback" in completed.stdout
