from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-aggregate-gate"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_31_candidate"
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


def test_l5_31_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l5_31_aggregate_cli_readback_passes_passively() -> None:
    payload = readback.build_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.31"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["brief_validation_output_enabled"] is True
    assert payload["source_l5_30_summary"]["patch"] == "L5.30"
    assert payload["source_l5_30_summary"]["ok"] is True
    assert payload["source_l5_29_summary"]["patch"] == "L5.29"
    assert payload["source_l5_28_summary"]["patch"] == "L5.28"
    assert payload["next_patch"] == "L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint"
    _assert_passive(payload)


def test_l5_31_default_profile_and_missing_profile_stay_passive() -> None:
    default_payload = readback.build_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = readback.build_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l5_30_summary"]["default_profile_candidate_detected"] is True
    assert default_payload["source_l5_30_summary"]["default_profile_path_rejected"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l5_30_summary"]["profile_parent_path_derived"] is False
    _assert_passive(missing_payload)


def test_l5_31_patchops_cli_json_readback_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L5.31"
    _assert_passive(payload)


def test_l5_31_doc_mentions_brief_validation_and_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_aggregate_gate_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L5.31 Microsoft Edge supervised launch profile parent preflight aggregate gate CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "profile parent aggregate gate remains accepted",
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "no Selenium import",
        "no browser start",
        "no click/download/paste/send/package-run side effect",
        "L5.32 Live adapter Microsoft Edge supervised launch profile parent preflight broad validation checkpoint",
    ]:
        assert phrase in text
