from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-broad-validation-checkpoint"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_33_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_parent_directory_created"] is False
    assert payload["profile_parent_filesystem_probe_performed"] is False
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


def test_l5_33_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l5_33_final_marker_dedicated_profile_passes_passively() -> None:
    payload = marker.build_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.33"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["profile_parent_preflight_slice_accepted"] is True
    assert payload["l5_28_profile_parent_preflight_contract_remains_accepted"] is True
    assert payload["l5_29_profile_parent_preflight_cli_readback_remains_accepted"] is True
    assert payload["l5_30_profile_parent_preflight_aggregate_gate_remains_accepted"] is True
    assert payload["l5_31_profile_parent_preflight_aggregate_cli_readback_remains_accepted"] is True
    assert payload["l5_32_profile_parent_preflight_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["next_patch"] == "L6.1 Live adapter Microsoft Edge executable discovery passive contract"
    _assert_passive(payload)


def test_l5_33_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = marker.build_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = marker.build_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["default_profile_candidate_detected"] is True
    assert default_payload["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["default_profile_path_rejected"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l5_32_summary"]["source_l5_31_summary"]["source_l5_30_summary"]["profile_parent_path_derived"] is False
    _assert_passive(missing_payload)


def test_l5_33_patchops_cli_json_readback_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L5.33"
    _assert_passive(payload)


def test_l5_33_doc_mentions_final_marker_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L5.33 Microsoft Edge supervised launch profile parent preflight final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "profile parent preflight slice accepted",
        "L5.28 profile parent preflight contract remains accepted",
        "L5.29 profile parent preflight CLI/readback remains accepted",
        "L5.30 profile parent preflight aggregate gate remains accepted",
        "L5.31 profile parent preflight aggregate CLI/readback remains accepted",
        "L5.32 profile parent preflight broad validation checkpoint remains accepted",
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "no Selenium import",
        "no browser start",
        "no click/download/paste/send/package-run side effect",
        "L6.1 Live adapter Microsoft Edge executable discovery passive contract",
    ]:
        assert phrase in text
