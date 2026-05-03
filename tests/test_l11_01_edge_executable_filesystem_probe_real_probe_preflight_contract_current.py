from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_real_probe_preflight_contract as preflight

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-real-probe-preflight-contract"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-final-acceptance-marker"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l11_01_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["real_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
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
    assert "source_l11_01_summary" not in payload
    assert "source_l10_08_summary" not in payload


def test_l11_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l11_01_real_probe_preflight_not_ready_without_real_probe_flag() -> None:
    payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=False,
    )
    assert payload["ok"] is True
    assert payload["patch"] == "L11.1"
    assert payload["l10_explicit_activation_stack_accepted"] is True
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["real_filesystem_probe_preflight_ready"] is False
    _assert_passive(payload)


def test_l11_01_real_probe_flag_alone_is_not_ready() -> None:
    payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
        activate_executable_filesystem_probe=False,
        allow_real_filesystem_probe=True,
    )
    assert payload["ok"] is True
    assert payload["filesystem_probe_activation_ready"] is False
    assert payload["real_filesystem_probe_authorization_present"] is True
    assert payload["real_filesystem_probe_preflight_ready"] is False
    _assert_passive(payload)


def test_l11_01_real_probe_preflight_ready_but_execution_still_blocked() -> None:
    payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L11"
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["real_filesystem_probe_preflight_ready"] is True
    assert payload["real_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L11.2 Live adapter Microsoft Edge executable filesystem probe real-probe preflight CLI/readback"
    _assert_passive(payload)


def test_l11_01_default_and_missing_profile_cases_are_passive_when_real_preflight_ready() -> None:
    default_payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True)
    missing_payload = preflight.build_edge_executable_filesystem_probe_real_probe_preflight_contract(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l10_08_status"]["ok"] is True
    assert default_payload["real_filesystem_probe_preflight_ready"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l10_08_status"]["ok"] is True
    assert missing_payload["real_filesystem_probe_preflight_ready"] is True
    _assert_passive(missing_payload)


def test_l11_01_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L11.1"
    assert payload["real_filesystem_probe_preflight_ready"] is True
    assert payload["real_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l11_01_doc_mentions_real_probe_preflight_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_real_probe_preflight_contract.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L11.1 Microsoft Edge executable filesystem probe real-probe preflight contract",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L10 explicit activation stack accepted",
        "real-probe preflight contract enforced",
        "real filesystem probe requires a separate explicit preflight flag",
        "--allow-real-filesystem-probe",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "real-probe preflight readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L11.2 Live adapter Microsoft Edge executable filesystem probe real-probe preflight CLI/readback",
    ]:
        assert phrase in text
