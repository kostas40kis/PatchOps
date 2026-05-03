from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l12_04_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_gates",
    "execution_flag_only",
    "real_ready_without_execution_flag",
    "execution_preflight_ready_dedicated_profile",
    "execution_preflight_ready_default_profile",
    "execution_preflight_ready_missing_profile",
}


def _assert_passive(payload: dict) -> None:
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["fixture_execution_preflight_execution_allowed"] is False
    assert payload["real_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_filesystem_probe_performed"] is False
    assert payload["fixture_path_selected"] is False
    assert payload["fixture_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert "source_l12_04_summary" not in payload
    assert "source_l12_03_summary" not in payload


def test_l12_04_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l12_04_fixture_matrix_readback_not_ready_without_all_required_gates() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False),
    ]:
        payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L12.4"
        assert payload["l12_03_execution_preflight_fixture_matrix_remains_accepted"] is True
        assert set(payload["execution_preflight_fixture_ids"]) == EXPECTED_IDS
        assert payload["execution_preflight_ready"] is False
        _assert_passive(payload)


def test_l12_04_execution_preflight_ready_but_execution_still_blocked() -> None:
    payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L12"
    assert payload["execution_preflight_ready"] is True
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate"
    _assert_passive(payload)


def test_l12_04_default_and_missing_profile_cases_are_passive_when_execution_preflight_ready() -> None:
    default_payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=True)
    missing_payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l12_03_status"]["ok"] is True
    assert default_payload["execution_preflight_ready"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l12_03_status"]["ok"] is True
    assert missing_payload["execution_preflight_ready"] is True
    _assert_passive(missing_payload)


def test_l12_04_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
            "--activate-executable-filesystem-probe",
            "--allow-real-filesystem-probe",
            "--allow-executable-filesystem-probe-execution",
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
    assert payload["patch"] == "L12.4"
    assert payload["execution_preflight_ready"] is True
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l12_04_doc_mentions_execution_preflight_fixture_matrix_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L12.4 Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L12.3 execution preflight fixture matrix remains accepted",
        "execution preflight fixture matrix CLI/readback enforced",
        "execution preflight fixture matrix enforced",
        "execution preflight CLI/readback enforced",
        "filesystem probe execution requires a separate explicit execution-preflight flag",
        "six execution preflight fixtures remain stable",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_preflight_ready_dedicated_profile",
        "execution_preflight_ready_default_profile",
        "execution_preflight_ready_missing_profile",
        "--allow-executable-filesystem-probe-execution",
        "--allow-real-filesystem-probe",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "execution preflight readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate",
    ]:
        assert phrase in text
