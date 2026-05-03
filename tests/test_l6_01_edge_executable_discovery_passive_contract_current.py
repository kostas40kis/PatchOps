from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_discovery_passive_contract as contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-discovery-contract"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_01_candidate"
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


def test_l6_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l6_01_edge_executable_contract_dedicated_profile_passes_passively() -> None:
    payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L6.1"
    assert payload["phase"] == "L6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l5_33_profile_parent_preflight_final_marker_remains_accepted"] is True
    assert payload["profile_parent_preflight_slice_accepted"] is True
    assert payload["edge_executable_discovery_contract_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_candidate_count"] >= 3
    assert all("msedge.exe" in candidate.lower() for candidate in payload["edge_executable_candidates"])
    assert payload["next_patch"] == "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback"
    _assert_passive(payload)


def test_l6_01_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = contract.build_edge_executable_discovery_passive_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l5_33_summary"]["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["default_profile_candidate_detected"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l5_33_summary"]["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["profile_parent_path_derived"] is False
    _assert_passive(missing_payload)


def test_l6_01_patchops_cli_json_readback_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L6.1"
    _assert_passive(payload)


def test_l6_01_doc_mentions_executable_discovery_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_discovery_passive_contract.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L6.1 Microsoft Edge executable discovery passive contract",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "L5.33 profile parent preflight final marker remains accepted",
        "Edge executable candidate paths modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L6.2 Live adapter Microsoft Edge executable discovery CLI/readback",
    ]:
        assert phrase in text
