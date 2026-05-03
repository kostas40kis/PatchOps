from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_probe_safety_preflight_passive_contract as contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-final-acceptance-marker"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l8_01_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["preflight_alone_does_not_perform_probe"] is True
    assert payload["authorization_alone_does_not_perform_probe"] is True
    assert payload["fixture_probe_performed"] is False
    assert payload["fixture_executable_selected"] is False
    assert payload["fixture_executable_launch_attempted"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert "source_l8_01_summary" not in payload
    assert "source_l7_08_summary" not in payload


def test_l8_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l8_01_safety_preflight_without_probe_auth_is_modeled_and_blocked() -> None:
    payload = contract.build_edge_executable_probe_safety_preflight_passive_contract(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L8.1"
    assert payload["edge_executable_probe_safety_preflight_contract_enforced"] is True
    assert payload["edge_executable_probe_safety_preflight_modeled"] is True
    assert payload["preflight_authorization_present"] is False
    assert payload["edge_executable_probe_safety_preflight_passed"] is False
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["preflight_blocked_reason"].startswith("L8.1 models safety preflight only")
    _assert_passive(payload)


def test_l8_01_safety_preflight_with_probe_auth_passes_but_still_does_not_probe() -> None:
    payload = contract.build_edge_executable_probe_safety_preflight_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L8"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l7_08_executable_probe_authorization_final_marker_remains_accepted"] is True
    assert payload["l7_executable_probe_authorization_slice_accepted"] is True
    assert payload["preflight_authorization_present"] is True
    assert payload["edge_executable_probe_safety_preflight_passed"] is True
    assert payload["edge_executable_probe_safety_preflight_status"] == "MODELED_ONLY_BLOCKED_BY_PHASE"
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    assert payload["next_patch"] == "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback"
    _assert_passive(payload)


def test_l8_01_default_and_missing_profile_cases_are_passive_when_authorized() -> None:
    default_payload = contract.build_edge_executable_probe_safety_preflight_passive_contract(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = contract.build_edge_executable_probe_safety_preflight_passive_contract(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l7_08_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l7_08_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l8_01_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED_PROFILE),
            "--allow-executable-probe",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L8.1"
    assert payload["preflight_authorization_present"] is True
    assert payload["edge_executable_probe_preflight_allows_probe_execution"] is False
    _assert_passive(payload)


def test_l8_01_doc_mentions_safety_preflight_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L8.1 Microsoft Edge executable probe safety preflight passive contract",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L7.8 executable probe authorization final marker remains accepted",
        "L7 executable probe authorization slice accepted",
        "safety preflight contract enforced",
        "safety preflight modeled only",
        "preflight alone does not perform a probe",
        "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.",
        "--allow-executable-probe",
        "authorization can be present but probe execution remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback",
    ]:
        assert phrase in text
