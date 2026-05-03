from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-contract"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l9_02_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
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
    assert "source_l9_02_summary" not in payload
    assert "source_l9_01_summary" not in payload


def test_l9_02_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l9_02_no_auth_readback_ok_preflight_false_contract_not_ready() -> None:
    payload = readback.build_edge_executable_filesystem_probe_cli_readback(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L9.2"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l9_01_executable_filesystem_probe_passive_contract_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_cli_readback_enforced"] is True
    assert payload["edge_executable_probe_safety_preflight_passed"] is False
    assert payload["edge_executable_filesystem_probe_contract_ready"] is False
    assert payload["edge_executable_candidate_path_labels_modeled"] is True
    assert payload["edge_executable_candidate_path_count"] >= 3
    _assert_passive(payload)


def test_l9_02_authorized_readback_contract_ready_but_filesystem_probe_stays_blocked() -> None:
    payload = readback.build_edge_executable_filesystem_probe_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L9"
    assert payload["edge_executable_probe_safety_preflight_passed"] is True
    assert payload["edge_executable_filesystem_probe_contract_ready"] is True
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L9.3 Live adapter Microsoft Edge executable filesystem probe fixture matrix"
    _assert_passive(payload)


def test_l9_02_default_and_missing_profile_cases_are_passive_when_authorized() -> None:
    default_payload = readback.build_edge_executable_filesystem_probe_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = readback.build_edge_executable_filesystem_probe_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l9_01_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l9_01_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l9_02_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L9.2"
    assert payload["edge_executable_filesystem_probe_contract_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l9_02_doc_mentions_filesystem_probe_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L9.2 Microsoft Edge executable filesystem probe CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L9.1 executable filesystem probe passive contract remains accepted",
        "filesystem probe CLI/readback enforced",
        "filesystem probe contract enforced",
        "filesystem probe modeled only",
        "filesystem probe readback can report contract_ready=true while filesystem probe remains blocked",
        "candidate path labels modeled only",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "preflight readback can succeed while preflight_passed is false",
        "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.",
        "--allow-executable-probe",
        "authorization can be present but filesystem probe execution remains blocked by phase",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L9.3 Live adapter Microsoft Edge executable filesystem probe fixture matrix",
    ]:
        assert phrase in text
