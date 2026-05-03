from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l7_04_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_probe_auth_dedicated_profile",
    "live_auth_without_probe_auth",
    "probe_auth_dedicated_profile",
    "probe_auth_default_profile",
    "probe_auth_missing_profile",
}


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
    assert "source_l7_04_summary" not in payload
    assert "source_l7_03_summary" not in payload


def test_l7_04_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l7_04_fixture_matrix_readback_dedicated_profile_passes_passively() -> None:
    payload = readback.build_edge_executable_probe_authorization_fixture_matrix_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L7.4"
    assert payload["phase"] == "L7"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l7_03_executable_probe_authorization_fixture_matrix_remains_accepted"] is True
    assert payload["edge_executable_probe_authorization_fixture_matrix_cli_readback_enforced"] is True
    assert payload["edge_executable_probe_authorization_fixture_count"] >= 5
    assert set(payload["edge_executable_probe_authorization_fixture_ids"]) == EXPECTED_IDS
    assert all(f["expected_probe_performed"] is False for f in payload["edge_executable_probe_authorization_fixture_matrix"])
    assert payload["next_patch"] == "L7.5 Live adapter Microsoft Edge executable probe authorization aggregate gate"
    _assert_passive(payload)


def test_l7_04_no_auth_default_and_missing_profile_cases_are_passive() -> None:
    no_auth = readback.build_edge_executable_probe_authorization_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False)
    default_payload = readback.build_edge_executable_probe_authorization_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = readback.build_edge_executable_probe_authorization_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert no_auth["ok"] is True
    assert no_auth["edge_executable_probe_authorized"] is False
    _assert_passive(no_auth)
    assert default_payload["ok"] is True
    assert default_payload["source_l7_03_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l7_03_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l7_04_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L7.4"
    assert payload["edge_executable_probe_authorized"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    _assert_passive(payload)


def test_l7_04_doc_mentions_fixture_matrix_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L7.4 Microsoft Edge executable probe authorization fixture matrix CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L7.3 executable probe authorization fixture matrix remains accepted",
        "fixture matrix CLI/readback enforced",
        "no_probe_auth_dedicated_profile",
        "live_auth_without_probe_auth",
        "probe_auth_dedicated_profile",
        "probe_auth_default_profile",
        "probe_auth_missing_profile",
        "--allow-executable-probe",
        "authorization alone does not perform a probe",
        "executable probe remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L7.5 Live adapter Microsoft Edge executable probe authorization aggregate gate",
    ]:
        assert phrase in text
