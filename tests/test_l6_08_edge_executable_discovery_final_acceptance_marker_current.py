from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_discovery_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_08_candidate"
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
    assert payload["edge_executable_fixture_filesystem_probe_performed"] is False
    assert payload["edge_executable_fixture_path_selected"] is False
    assert payload["edge_executable_fixture_launch_attempted"] is False
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
    assert "source_l6_08_summary" not in payload
    assert "source_l6_07_summary" not in payload
    assert "source_l6_06_summary" not in payload


def test_l6_08_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l6_08_final_marker_dedicated_profile_passes_passively_and_compactly() -> None:
    payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L6.8"
    assert payload["phase"] == "L6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l6_executable_discovery_slice_accepted"] is True
    assert payload["l6_01_executable_discovery_passive_contract_remains_accepted"] is True
    assert payload["l6_02_executable_discovery_cli_readback_remains_accepted"] is True
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l6_05_executable_discovery_aggregate_gate_remains_accepted"] is True
    assert payload["l6_06_executable_discovery_aggregate_cli_readback_remains_accepted"] is True
    assert payload["l6_07_executable_discovery_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert payload["edge_executable_discovery_final_acceptance_marker_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_fixture_matrix_modeled"] is True
    assert payload["next_patch"] == "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract"
    assert payload["source_l6_07_status"]["patch"] == "L6.7"
    assert payload["source_l6_07_status"]["ok"] is True
    assert "source_chain_status" in payload
    _assert_passive(payload)


def test_l6_08_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l6_07_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l6_07_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l6_08_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L6.8"
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    _assert_passive(payload)


def test_l6_08_doc_mentions_final_marker_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_discovery_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L6.8 Microsoft Edge executable discovery final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L6 executable discovery slice accepted",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "L6.5 executable discovery aggregate gate remains accepted",
        "L6.6 executable discovery aggregate CLI/readback remains accepted",
        "L6.7 executable discovery broad validation checkpoint remains accepted",
        "nested source summaries remain pruned",
        "source_chain_status",
        "executable discovery final acceptance marker enforced",
        "Edge executable candidate paths remain modeled",
        "fixture matrix remains modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract",
    ]:
        assert phrase in text
