from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-parent-preflight-contract"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_29_candidate"


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


def test_l5_29_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l5_29_dedicated_profile_parent_preflight_cli_readback_passes_passively() -> None:
    payload = readback.build_edge_supervised_launch_profile_parent_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.29"
    assert payload["phase"] == "L5"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["next_patch"] == "L5.30 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate"
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["source_l5_28_summary"]["ok"] is True
    assert payload["source_l5_28_summary"]["status"] == "PASS"
    assert payload["source_l5_28_summary"]["patch"] == "L5.28"
    assert payload["profile_parent_preflight_status"] == "BLOCKED_PROFILE_PARENT_PREFLIGHT_MODEL_ONLY"
    assert payload["profile_parent_path_derived"] is True
    assert str(payload["profile_parent_path"]).endswith("browser_profiles")
    assert payload["profile_parent_probe_required_before_future_live_start"] is True
    assert payload["profile_parent_must_exist_before_future_live_start"] is True
    _assert_passive(payload)

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["l5_28_profile_parent_preflight_contract_still_passes"]["ok"] is True
    assert checks["l5_28_profile_parent_preflight_contract_remains_passive"]["ok"] is True
    assert checks["l5_29_profile_parent_preflight_readback_command_registered"]["ok"] is True
    assert checks["profile_parent_preflight_cli_readback_is_passive"]["ok"] is True
    assert checks["profile_parent_path_is_derived_by_source_contract"]["ok"] is True
    assert checks["profile_parent_filesystem_probe_stays_false"]["ok"] is True
    assert checks["profile_parent_directory_stays_uncreated"]["ok"] is True
    assert checks["no_browser_profile_or_adapter_side_effects"]["ok"] is True


def test_l5_29_default_profile_readback_still_rejected_before_parent_preflight() -> None:
    payload = readback.build_edge_supervised_launch_profile_parent_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["profile_parent_preflight_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
    assert payload["profile_parent_path_derived"] is True
    assert payload["profile_parent_filesystem_probe_performed"] is False
    assert payload["profile_parent_directory_created"] is False
    _assert_passive(payload)


def test_l5_29_missing_authorization_and_missing_profile_readbacks_are_passive() -> None:
    no_auth = readback.build_edge_supervised_launch_profile_parent_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
    )
    missing_profile = readback.build_edge_supervised_launch_profile_parent_preflight_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )

    assert no_auth["ok"] is True
    assert no_auth["profile_parent_preflight_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert no_auth["profile_parent_path_derived"] is True
    _assert_passive(no_auth)

    assert missing_profile["ok"] is True
    assert missing_profile["profile_parent_preflight_status"] == "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
    assert missing_profile["profile_parent_path_derived"] is False
    assert missing_profile["profile_parent_path"] is None
    _assert_passive(missing_profile)


def test_l5_29_module_cli_json_readback_passes_without_side_effects() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback",
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
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.29"
    assert payload["command_name"] == COMMAND
    _assert_passive(payload)


def test_l5_29_patchops_cli_json_readback_passes_without_side_effects() -> None:
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
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.29"
    assert payload["command_name"] == COMMAND
    assert payload["source_l5_28_summary"]["patch"] == "L5.28"
    _assert_passive(payload)


def test_l5_29_doc_contract_mentions_safety_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_profile_parent_preflight_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    required = [
        "L5.29 Microsoft Edge supervised launch profile parent preflight CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "profile parent preflight CLI/readback",
        "profile parent path derived",
        "profile parent filesystem probe not performed",
        "profile parent directory not created",
        "default Microsoft Edge profile remains forbidden",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.30 Live adapter Microsoft Edge supervised launch profile parent preflight aggregate gate",
    ]
    for phrase in required:
        assert phrase in text
