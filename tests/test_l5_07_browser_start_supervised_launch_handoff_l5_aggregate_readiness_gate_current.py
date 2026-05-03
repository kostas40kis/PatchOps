from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l5_7_supervised_launch_aggregate_readiness_gate_passes() -> None:
    payload = gate.build_l5_aggregate_readiness_gate(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.7"
    assert payload["phase"] == "L5"
    assert payload["next_patch"] == "L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback"
    assert payload["missing_commands"] == []
    assert payload["missing_repo_paths"] == []
    assert payload["missing_l5_07_paths"] == []
    assert payload["missing_doc_phrases"] == []

    sources = payload["source_patches"]
    assert sources["L5.1"]["status"] == "PASS"
    assert sources["L5.1"]["ok"] is True
    assert sources["L5.2"]["registered"] is True
    assert sources["L5.3"]["status"] == "PASS"
    assert sources["L5.3"]["ok"] is True
    assert sources["L5.4"]["registered"] is True
    assert sources["L5.5"]["status"] == "PASS"
    assert sources["L5.5"]["ok"] is True
    assert sources["L5.6"]["registered"] is True


def test_l5_7_supervised_launch_aggregate_readiness_gate_is_passive() -> None:
    payload = gate.build_l5_aggregate_readiness_gate(PROJECT_ROOT)

    assert payload["modelled_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_driver_session_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["executed_validation_commands"] == []


def test_l5_7_supervised_launch_aggregate_readiness_gate_check_names_are_stable() -> None:
    payload = gate.build_l5_aggregate_readiness_gate(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    required = {
        "l5_01_supervised_launch_handoff_contract_still_passes",
        "l5_02_supervised_launch_handoff_cli_command_registered",
        "l5_03_supervised_launch_handoff_fixture_matrix_still_passes",
        "l5_04_supervised_launch_handoff_fixture_matrix_cli_command_registered",
        "l5_05_supervised_launch_handoff_contract_gate_still_passes",
        "l5_06_supervised_launch_handoff_contract_gate_cli_command_registered",
        "l5_aggregate_required_command_set_registered",
        "l5_aggregate_required_repo_paths_present",
        "l5_aggregate_l5_07_artifacts_present",
        "l5_aggregate_doc_contains_boundary_and_next_patch",
        "l5_aggregate_readback_command_plan_is_passive",
        "l5_aggregate_did_not_load_optional_browser_dependencies",
        "l5_aggregate_keeps_startup_blocked",
        "l5_aggregate_creates_no_browser_session_or_driver",
        "l5_aggregate_creates_no_profile_directory_or_adapter_writes",
        "l5_aggregate_executes_no_side_effects",
        "l5_aggregate_payload_json_safe",
    }
    assert required.issubset(checks)
    assert all(check["ok"] for check in checks.values())


def test_l5_7_supervised_launch_aggregate_readiness_gate_module_json_smoke() -> None:
    completed = subprocess.run(
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
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.7"
    assert payload["missing_commands"] == []
    assert payload["browser_started"] is False
    assert payload["selenium_imported"] is False


def test_l5_7_supervised_launch_aggregate_readiness_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate",
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


def test_l5_7_supervised_launch_aggregate_readiness_gate_payload_json_safe() -> None:
    payload = gate.build_l5_aggregate_readiness_gate(PROJECT_ROOT)
    json.dumps(payload, sort_keys=True)
