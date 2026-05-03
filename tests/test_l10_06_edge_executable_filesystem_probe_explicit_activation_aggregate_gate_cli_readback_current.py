from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l10_06_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_activation_no_auth",
    "activation_only",
    "live_and_probe_auth_without_activation",
    "all_gates_dedicated_profile",
    "all_gates_default_profile",
    "all_gates_missing_profile",
}


def _assert_passive(payload: dict) -> None:
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["fixture_activation_execution_allowed"] is False
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
    assert "source_l10_06_summary" not in payload
    assert "source_l10_05_summary" not in payload


def test_l10_06_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l10_06_activation_aggregate_readback_not_ready_without_all_gates() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=False),
    ]:
        payload = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(PROJECT_ROOT, **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L10.6"
        assert payload["l10_05_explicit_activation_aggregate_gate_remains_accepted"] is True
        assert payload["l10_explicit_activation_chain_accepted"] is True
        assert set(payload["edge_executable_filesystem_probe_activation_fixture_ids"]) == EXPECTED_IDS
        assert payload["filesystem_probe_activation_ready"] is False
        _assert_passive(payload)


def test_l10_06_all_gates_ready_but_execution_still_blocked() -> None:
    payload = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l10_01_explicit_activation_contract_remains_accepted"] is True
    assert payload["l10_02_explicit_activation_cli_readback_remains_accepted"] is True
    assert payload["l10_03_explicit_activation_fixture_matrix_remains_accepted"] is True
    assert payload["l10_04_explicit_activation_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["filesystem_probe_activation_all_three_gates_present"] is True
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L10.7 Live adapter Microsoft Edge executable filesystem probe explicit activation broad validation checkpoint"
    _assert_passive(payload)


def test_l10_06_default_and_missing_profile_cases_are_passive_when_all_gates_present() -> None:
    default_payload = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True)
    missing_payload = readback.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True, activate_executable_filesystem_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l10_05_status"]["ok"] is True
    assert default_payload["filesystem_probe_activation_ready"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l10_05_status"]["ok"] is True
    assert missing_payload["filesystem_probe_activation_ready"] is True
    _assert_passive(missing_payload)


def test_l10_06_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L10.6"
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l10_06_doc_mentions_activation_aggregate_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L10.6 Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L10.5 explicit activation aggregate gate remains accepted",
        "explicit activation aggregate gate CLI/readback enforced",
        "explicit activation aggregate gate enforced",
        "explicit activation fixture matrix CLI/readback enforced",
        "explicit activation modeled only",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "activation readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L10.7 Live adapter Microsoft Edge executable filesystem probe explicit activation broad validation checkpoint",
    ]:
        assert phrase in text
