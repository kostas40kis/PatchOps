
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_l2_readiness_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_profile_aggregate_readiness_gate_passes_without_side_effects() -> None:
    payload = gate.build_browser_profile_l2_aggregate_readiness_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L2.7"
    assert payload["phase"] == "L2"
    assert payload["next_patch"] == "L2.8 Live adapter browser profile preflight L2 aggregate readiness gate CLI/readback"
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
    assert payload["profile_preflight"]["ok"] is True
    assert payload["fixture_matrix"]["ok"] is True
    assert payload["fixture_matrix_contract_gate"]["ok"] is True

    required = {
        "l2_profile_preflight_contract_still_passes",
        "l2_profile_fixture_matrix_still_passes",
        "l2_profile_fixture_matrix_contract_gate_still_passes",
        "l2_profile_l2_aggregate_core_cases_present",
        "l2_profile_l2_aggregate_all_upstream_surfaces_pass",
        "l2_profile_l2_aggregate_blocks_startup",
        "l2_profile_l2_aggregate_creates_no_browser_session",
        "l2_profile_l2_aggregate_creates_no_profile_directory",
        "l2_profile_l2_aggregate_models_requested_side_effects_but_executes_none",
        "l2_profile_l2_aggregate_invalid_browser_reported_without_side_effects",
        "l2_profile_l2_aggregate_profile_paths_modelled_only",
        "l2_profile_l2_aggregate_payload_json_safe",
        "no_optional_browser_dependency_imports",
        "l2_profile_l2_aggregate_did_not_load_browser_optional_modules",
    }
    assert required.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required)


def test_l2_profile_aggregate_readiness_gate_case_names_are_preserved() -> None:
    payload = gate.build_l2_aggregate_readiness_gate(PROJECT_ROOT)
    assert set(payload["case_names"]) == {
        "default_edge_no_acknowledgements",
        "opera_acknowledged_start_and_profile_request",
        "edge_acknowledged_profile_only_request",
        "invalid_browser_send_request",
        "custom_profile_root_and_name",
        "opera_optional_dependency_flag",
    }
    assert "opera_acknowledged_start_and_profile_request" in payload["requested_side_effect_cases"]
    assert "custom_profile_root_and_name" in payload["profile_paths_by_case"]
    assert payload["profile_paths_by_case"]["custom_profile_root_and_name"]


def test_l2_profile_aggregate_readiness_gate_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate",
            "--repo-root",
            str(PROJECT_ROOT),
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
    assert payload["patch"] == "L2.7"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["profile_preflight"]["ok"] is True
    assert payload["fixture_matrix"]["ok"] is True
    assert payload["fixture_matrix_contract_gate"]["ok"] is True


def test_l2_profile_aggregate_readiness_gate_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps LLM browser profile preflight L2 aggregate readiness gate" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight L2 aggregate readiness gate" in stdout
    assert "Status     : PASS" in stdout
    assert "Patch      : L2.7" in stdout
    assert "Cases      : 6" in stdout
    assert "Startup    : allowed=false" in stdout
    assert "BrowserRun : not started" in stdout
    assert "Profile    : created=false" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "l2_profile_l2_aggregate_blocks_startup: PASS" in stdout
    assert "Next patch : L2.8 Live adapter browser profile preflight L2 aggregate readiness gate CLI/readback" in stdout


def test_l2_profile_aggregate_readiness_gate_imports_no_browser_optional_modules() -> None:
    before = set(sys.modules)
    payload = gate.build_profile_preflight_l2_aggregate_readiness_gate(PROJECT_ROOT)
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    assert payload["ok"] is True
    assert not any(name.split(".", 1)[0] in forbidden_roots for name in newly_loaded)
    assert "selenium" not in sys.modules
