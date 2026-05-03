from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_preflight as l14_04

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-preflight"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-launch-dry-run-plan-readback"


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


def test_l14_04_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l14_04_profile_preflight_is_passive_and_under_allowed_root() -> None:
    payload = l14_04.build_edge_dedicated_profile_lifecycle_preflight(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L14.4"
    assert payload["phase"] == "L14"
    assert payload["source_patch"] == "L14.3"
    assert payload["source_l13_complete"] is True
    assert payload["launch_authorization_granted_for_future_stage"] is True
    assert payload["dry_run_plan_readback_enforced"] is True
    assert payload["dry_run_plan_is_passive"] is True
    assert payload["dedicated_profile_lifecycle_preflight_enforced"] is True
    assert payload["profile_candidate_under_allowed_runtime_root"] is True
    assert payload["profile_lifecycle_steps_are_passive"] is True
    assert payload["profile_directory_creation_deferred"] is True
    assert str(payload["profile_candidate_path"]).endswith("data\\runtime\\browser_profiles\\edge_supervised_l14") or str(payload["profile_candidate_path"]).endswith("data/runtime/browser_profiles/edge_supervised_l14")
    assert all(item["filesystem_write_allowed"] is False for item in payload["profile_lifecycle_steps"])
    assert all(item["browser_launch_allowed"] is False for item in payload["profile_lifecycle_steps"])
    _assert_passive(payload)
    assert payload["next_patch"] == "L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback, still no launch"


def test_l14_04_rejects_profile_candidate_outside_allowed_root() -> None:
    payload = l14_04.build_edge_dedicated_profile_lifecycle_preflight(PROJECT_ROOT, profile_relative_path="../outside_profile")
    assert payload["ok"] is False
    assert payload["profile_candidate_under_allowed_runtime_root"] is False
    assert payload["profile_directory_created"] is False
    _assert_passive(payload)


def test_l14_04_cli_compact_json_is_parseable_and_passive() -> None:
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
    assert payload["patch"] == "L14.4"
    assert payload["profile_candidate_under_allowed_runtime_root"] is True
    assert payload["profile_directory_created"] is False
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l14_04_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_dedicated_profile_lifecycle_preflight.md").read_text(encoding="utf-8")
    for phrase in [
        "L14.4 Microsoft Edge dedicated profile lifecycle preflight",
        COMMAND,
        SOURCE_COMMAND,
        "L14.3 dry-run plan remains accepted",
        "dedicated profile lifecycle preflight enforced",
        "profile candidate under allowed runtime root",
        "profile lifecycle steps are passive",
        "profile directory creation deferred",
        "profile directory create allowed: false",
        "profile directory cleanup allowed: false",
        "profile directory delete allowed: false",
        "profile directory created: false",
        "profile directory mutated: false",
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
        "L14.5 Microsoft Edge dedicated profile lifecycle CLI/readback, still no launch",
    ]:
        assert phrase in text
