from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_final_acceptance_marker as final_marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-broad-validation-checkpoint"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_08_candidate"
EXISTING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_08.exe"
MISSING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-08.exe"


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
    assert payload["forbidden_optional_imports_observed"] == []
    assert payload["no_executable_launch_attempted_by_final_marker"] is True


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


def _payload(**kwargs: object) -> dict:
    return final_marker.build_edge_executable_filesystem_probe_execution_final_acceptance_marker(PROJECT_ROOT, **kwargs)


def test_l13_08_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l13_08_not_ready_cases_do_not_probe_and_keep_l13_stack_accepted() -> None:
    cases = [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_filesystem_probe_execution=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True),
    ]
    for kwargs in cases:
        payload = _payload(**kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L13.8"
        assert payload["source_patch"] == "L13.7"
        assert payload["source_l13_07_broad_checkpoint_remains_accepted"] is True
        assert payload["l13_07_broad_checkpoint_remains_accepted"] is True
        assert payload["l13_06_aggregate_gate_readback_remains_accepted"] is True
        assert payload["l13_05_aggregate_gate_remains_accepted"] is True
        assert payload["l13_04_fixture_matrix_readback_remains_accepted"] is True
        assert payload["l13_03_execution_fixture_matrix_remains_accepted"] is True
        assert payload["l13_stack_acceptance_markers_present"] is True
        assert payload["final_acceptance_marker_enforced"] is True
        assert payload["l13_final_acceptance_marker"] is True
        assert payload["l13_complete"] is True
        assert payload["remaining_l13_patches"] == []
        assert payload["edge_executable_filesystem_probe_performed"] is False
        assert payload["edge_executable_path_selected"] is False
        assert payload["edge_executable_selected_path"] is None
        assert payload["filesystem_probe_only_when_l12_execution_preflight_ready"] is True
        assert payload["executed_validation_commands"] == []
        _assert_truthful_selection(payload)
        _assert_no_launch_side_effects(payload)


def test_l13_08_ready_case_probes_observes_fixture_and_marks_l13_complete() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    payload = _payload(
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
    assert payload["patch"] == "L13.8"
    assert payload["source_patch"] == "L13.7"
    assert payload["source_l13_07_status"]["patch"] == "L13.7"
    assert payload["source_l13_07_broad_checkpoint_remains_accepted"] is True
    assert payload["l13_stack_acceptance_markers_present"] is True
    assert payload["final_acceptance_marker_enforced"] is True
    assert payload["l13_final_acceptance_marker"] is True
    assert payload["l13_complete"] is True
    assert payload["remaining_l13_patches"] == []
    assert "L13.8 execution final acceptance marker" in payload["accepted_l13_sequence"]
    assert payload["edge_executable_filesystem_probe_performed"] is True
    assert payload["filesystem_probe_only_when_l12_execution_preflight_ready"] is True
    fixture_candidate = _candidate_for(payload, EXISTING_FIXTURE)
    assert fixture_candidate is not None
    assert fixture_candidate.get("exists") is True
    assert fixture_candidate.get("is_file") is True
    assert payload["truthful_selected_path_existing_reported_candidate"] is True
    assert payload["required_repo_paths"]["ok"] is True
    _assert_truthful_selection(payload)
    _assert_no_launch_side_effects(payload)
    assert payload["next_frontier"] == "L13 complete; choose the next Microsoft Edge browser-runner frontier after the L13.8 report is reviewed"


def test_l13_08_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert len(completed.stdout) < 170000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L13.8"
    assert payload["source_patch"] == "L13.7"
    assert payload["l13_complete"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is True
    assert payload["truthful_selected_path_existing_reported_candidate"] is True
    _assert_truthful_selection(payload)
    _assert_no_launch_side_effects(payload)


def test_l13_08_doc_mentions_final_acceptance_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L13.8 Microsoft Edge executable filesystem probe execution final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "Microsoft Edge first",
        "Opera second",
        "L13.7 broad validation checkpoint remains accepted",
        "L13.6 aggregate gate CLI/readback remains accepted",
        "L13.5 aggregate gate remains accepted",
        "L13.4 fixture matrix CLI/readback remains accepted",
        "L13.3 execution fixture matrix remains accepted",
        "L13.2 execution CLI/readback remains accepted",
        "L13.1 execution contract remains accepted",
        "final acceptance marker enforced",
        "L13 final acceptance marker",
        "L13 complete",
        "remaining L13 patches: none",
        "preserve the L13.1/L13.1a truthful-selection contract",
        "read-only filesystem probe",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "selected path, if any, is an existing reported candidate",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no executable launch attempted",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no git commit or git push",
        "no localhost PatchOps server",
        "no browser extension",
        "next Microsoft Edge browser-runner frontier",
    ]:
        assert phrase in text
