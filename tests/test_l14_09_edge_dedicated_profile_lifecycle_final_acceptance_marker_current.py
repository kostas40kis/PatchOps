from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker as l14_09

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-broad-validation-checkpoint"


def _assert_passive(payload: dict) -> None:
    assert payload["profile_directory_create_allowed"] is False
    assert payload["profile_directory_cleanup_allowed"] is False
    assert payload["profile_directory_delete_allowed"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_directory_mutated"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_process_launch_authorized"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["broad_validation_commands_executed_by_checkpoint"] is False


def test_l14_09_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l14_09_final_marker_completes_l14_and_remains_passive() -> None:
    payload = l14_09.build_edge_dedicated_profile_lifecycle_final_acceptance_marker(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L14.9"
    assert payload["phase"] == "L14"
    assert payload["source_patch"] == "L14.8"
    assert payload["source_l13_complete"] is True
    assert payload["l14_08_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["l14_final_acceptance_marker_enforced"] is True
    assert payload["l14_stack_acceptance_markers_present"] is True
    assert payload["l14_final_acceptance_marker"] is True
    assert payload["l14_complete"] is True
    assert payload["remaining_l14_patches"] == []
    assert "L14.9 dedicated profile lifecycle final acceptance marker" in payload["accepted_l14_sequence"]
    assert payload["profile_final_marker_truthful"] is True
    assert payload["profile_final_marker_is_passive"] is True
    assert payload["profile_candidate_under_allowed_runtime_root"] is True
    assert payload["profile_lifecycle_steps_are_passive"] is True
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["source_l14_08_status"]["profile_created"] is False
    _assert_passive(payload)
    assert payload["next_frontier"] == "L14 complete; choose the next Microsoft Edge browser-runner frontier after the L14.9 report is reviewed"


def test_l14_09_rejects_disallowed_profile_path_and_stays_passive() -> None:
    payload = l14_09.build_edge_dedicated_profile_lifecycle_final_acceptance_marker(PROJECT_ROOT, profile_relative_path="../outside_profile")
    assert payload["ok"] is False
    assert payload["l14_complete"] is False
    assert payload["profile_candidate_under_allowed_runtime_root"] is False
    assert payload["profile_final_marker_truthful"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_directory_mutated"] is False
    _assert_passive(payload)


def test_l14_09_cli_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L14.9"
    assert payload["l14_complete"] is True
    assert payload["remaining_l14_patches"] == []
    assert payload["profile_final_marker_truthful"] is True
    assert payload["profile_final_marker_is_passive"] is True
    assert payload["profile_directory_created"] is False
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l14_09_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker.md").read_text(encoding="utf-8")
    for phrase in [
        "L14.9 Microsoft Edge dedicated profile lifecycle final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "L14.8 broad validation checkpoint remains accepted",
        "L14 final acceptance marker enforced",
        "L14 stack acceptance markers present",
        "L14 complete",
        "remaining L14 patches: none",
        "profile final marker truthful",
        "profile final marker is passive",
        "profile broad checkpoint truthful",
        "profile broad checkpoint is passive",
        "profile aggregate CLI/readback truthful",
        "profile aggregate CLI/readback is passive",
        "profile candidate under allowed runtime root",
        "profile lifecycle steps are passive",
        "profile directory creation deferred",
        "profile directory create allowed: false",
        "profile directory cleanup allowed: false",
        "profile directory delete allowed: false",
        "profile directory created: false",
        "profile directory mutated: false",
        "filesystem writes performed: none",
        "launch execution allowed: false",
        "Microsoft Edge first",
        "Opera second",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no click/download/paste/send/package-run side effect",
        "no git commit or git push",
        "no localhost PatchOps server",
        "no browser extension",
        "next Microsoft Edge browser-runner frontier",
    ]:
        assert phrase in text
