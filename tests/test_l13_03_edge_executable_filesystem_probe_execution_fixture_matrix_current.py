from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix as matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_03_candidate"
EXISTING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_03.exe"
MISSING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-03.exe"
EXPECTED_IDS = {
    "no_gates",
    "execution_flag_only",
    "real_ready_without_execution_flag",
    "execution_ready_missing_extra_candidate",
    "execution_ready_fixture_observed",
}


def _assert_no_launch_side_effects(payload: dict) -> None:
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
    assert "source_l13_03_summary" not in payload
    assert "source_l13_02_summary" not in payload


def _candidate_for(payload: dict, path: Path) -> dict | None:
    expected = str(path)
    for item in payload.get("edge_executable_probe_candidates", []) or []:
        if item.get("path") == expected:
            return item
    return None


def _assert_truthful_selection(payload: dict) -> None:
    selected = payload.get("edge_executable_selected_path")
    if payload["edge_executable_path_selected"]:
        assert any(
            item.get("path") == selected and item.get("exists") is True and item.get("is_file") is True
            for item in payload.get("edge_executable_probe_candidates", []) or []
        )
    else:
        assert selected is None


def test_l13_03_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l13_03_fixture_matrix_not_ready_cases_do_not_probe() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False),
    ]:
        payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(PROJECT_ROOT, extra_candidates=[str(MISSING_FIXTURE)], **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L13.3"
        assert payload["l13_02_execution_cli_readback_remains_accepted"] is True
        assert set(payload["execution_fixture_ids"]) == EXPECTED_IDS
        assert payload["edge_executable_filesystem_probe_performed"] is False
        assert payload["edge_executable_path_selected"] is False
        _assert_no_launch_side_effects(payload)


def test_l13_03_fixture_matrix_ready_case_probes_and_observes_fixture_without_launch() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE), str(EXISTING_FIXTURE)],
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L13"
    assert payload["execution_preflight_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is True
    fixture_candidate = _candidate_for(payload, EXISTING_FIXTURE)
    assert fixture_candidate is not None
    assert fixture_candidate.get("exists") is True
    assert fixture_candidate.get("is_file") is True
    _assert_truthful_selection(payload)
    assert payload["next_patch"] == "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback"
    _assert_no_launch_side_effects(payload)


def test_l13_03_patchops_cli_json_readback_is_parseable_compact_and_no_launch_side_effects() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
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
            "--extra-candidate",
            str(MISSING_FIXTURE),
            "--extra-candidate",
            str(EXISTING_FIXTURE),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 95000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L13.3"
    assert payload["edge_executable_filesystem_probe_performed"] is True
    fixture_candidate = _candidate_for(payload, EXISTING_FIXTURE)
    assert fixture_candidate is not None
    assert fixture_candidate.get("exists") is True
    assert fixture_candidate.get("is_file") is True
    _assert_truthful_selection(payload)
    _assert_no_launch_side_effects(payload)


def test_l13_03_doc_mentions_execution_fixture_matrix_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L13.3 Microsoft Edge executable filesystem probe execution fixture matrix",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L13.2 execution CLI/readback remains accepted",
        "L13.1 execution contract remains accepted",
        "execution fixture matrix enforced",
        "execution CLI/readback enforced",
        "execution contract enforced",
        "read-only filesystem probe",
        "small allowlisted Microsoft Edge executable candidate list",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "selected path, if any, is an existing reported candidate",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_ready_missing_extra_candidate",
        "execution_ready_fixture_observed",
        "--allow-executable-filesystem-probe-execution",
        "--allow-real-filesystem-probe",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no executable launch attempted",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback",
    ]:
        assert phrase in text
