from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l7_08_candidate"
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
    assert payload["edge_executable_probe_permitted_by_phase"] is False
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
    assert "source_l7_08_summary" not in payload
    assert "source_l7_07_summary" not in payload


def test_l7_08_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l7_08_final_marker_dedicated_profile_passes_passively() -> None:
    payload = marker.build_edge_executable_probe_authorization_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L7.8"
    assert payload["phase"] == "L7"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l7_executable_probe_authorization_slice_accepted"] is True
    assert payload["l7_01_executable_probe_authorization_passive_contract_remains_accepted"] is True
    assert payload["l7_02_executable_probe_authorization_cli_readback_remains_accepted"] is True
    assert payload["l7_03_executable_probe_authorization_fixture_matrix_remains_accepted"] is True
    assert payload["l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l7_05_executable_probe_authorization_aggregate_gate_remains_accepted"] is True
    assert payload["l7_06_executable_probe_authorization_aggregate_cli_readback_remains_accepted"] is True
    assert payload["l7_07_executable_probe_authorization_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["edge_executable_probe_authorization_final_acceptance_marker_enforced"] is True
    assert payload["edge_executable_probe_authorized"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L8.1 Live adapter Microsoft Edge executable probe safety preflight passive contract"
    _assert_passive(payload)


def test_l7_08_no_auth_default_and_missing_profile_cases_are_passive() -> None:
    no_auth = marker.build_edge_executable_probe_authorization_final_acceptance_marker(PROJECT_ROOT, allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False)
    default_payload = marker.build_edge_executable_probe_authorization_final_acceptance_marker(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = marker.build_edge_executable_probe_authorization_final_acceptance_marker(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert no_auth["ok"] is True
    assert no_auth["edge_executable_probe_authorized"] is False
    _assert_passive(no_auth)
    assert default_payload["ok"] is True
    assert default_payload["source_l7_07_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l7_07_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l7_08_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L7.8"
    assert payload["edge_executable_probe_authorized"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    _assert_passive(payload)


def test_l7_08_doc_mentions_final_marker_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_probe_authorization_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L7.8 Microsoft Edge executable probe authorization final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L7 executable probe authorization slice accepted",
        "L7.1 executable probe authorization passive contract remains accepted",
        "L7.2 executable probe authorization CLI/readback remains accepted",
        "L7.3 executable probe authorization fixture matrix remains accepted",
        "L7.4 executable probe authorization fixture matrix CLI/readback remains accepted",
        "L7.5 executable probe authorization aggregate gate remains accepted",
        "L7.6 executable probe authorization aggregate CLI/readback remains accepted",
        "L7.7 executable probe authorization broad validation checkpoint remains accepted",
        "final acceptance marker enforced",
        "--allow-executable-probe",
        "authorization alone does not perform a probe",
        "executable probe remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L8.1 Live adapter Microsoft Edge executable probe safety preflight passive contract",
    ]:
        assert phrase in text
