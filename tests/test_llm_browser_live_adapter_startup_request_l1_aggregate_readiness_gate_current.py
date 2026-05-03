from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_l1_readiness_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_aggregate_readiness_gate_passes_without_side_effects() -> None:
    payload = gate.build_l1_aggregate_readiness_gate()
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.13"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["case_count"] >= 6

    for name in [
        "startup_request_contract_gate_passes",
        "fixture_matrix_passes",
        "fixture_matrix_contract_gate_passes",
        "l1_startup_request_core_fixture_cases_present",
        "l1_aggregate_blocks_startup",
        "l1_aggregate_creates_no_browser_session",
        "l1_aggregate_models_requested_side_effects_but_executes_none",
        "l1_aggregate_invalid_browser_reported_without_side_effects",
        "no_optional_browser_dependency_imports",
        "l1_aggregate_gate_did_not_load_browser_optional_modules",
    ]:
        assert checks[name]["ok"] is True


def test_l1_aggregate_readiness_gate_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_l1_readiness_gate", "--json", "--compact"],
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
    assert payload["startup_request_contract_gate"]["ok"] is True
    assert payload["fixture_matrix"]["ok"] is True
    assert payload["fixture_matrix_contract_gate"]["ok"] is True


def test_l1_aggregate_readiness_gate_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_l1_readiness_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser startup request L1 aggregate readiness gate" in completed.stdout
    assert "PatchOps LLM browser live adapter startup request L1 aggregate readiness gate" in completed.stdout
    assert "Status     : PASS" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout
    assert "Next patch : L1.14 Live adapter startup request L1 aggregate readiness gate CLI/readback" in completed.stdout
