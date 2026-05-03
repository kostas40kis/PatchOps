from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_launch_dry_run_plan_readback as l14_03

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-launch-dry-run-plan-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-launch-authorization-gate"
TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"


def _assert_passive(payload: dict) -> None:
    assert payload["launch_authorization_effective_for_execution"] is False
    assert payload["dry_run_plan_executed"] is False
    assert payload["dry_run_plan_materialized_as_process_args"] is False
    assert payload["real_subprocess_invocation_built"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_process_launch_authorized"] is False
    assert payload["launch_execution_allowed"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
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
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["executed_validation_commands"] == []


def test_l14_03_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l14_03_requires_l14_02_future_authorization_for_acceptance() -> None:
    payload = l14_03.build_edge_launch_dry_run_plan_readback(PROJECT_ROOT)
    assert payload["ok"] is False
    assert payload["patch"] == "L14.3"
    assert payload["source_patch"] == "L14.2"
    assert payload["launch_authorization_granted_for_future_stage"] is False
    _assert_passive(payload)


def test_l14_03_with_token_builds_passive_dry_run_plan_only() -> None:
    payload = l14_03.build_edge_launch_dry_run_plan_readback(
        PROJECT_ROOT,
        request_launch_authorization=True,
        operator_confirmation_token=TOKEN,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L14.3"
    assert payload["source_patch"] == "L14.2"
    assert payload["source_l13_complete"] is True
    assert payload["launch_readiness_consolidated"] is True
    assert payload["launch_authorization_gate_enforced"] is True
    assert payload["launch_authorization_granted_for_future_stage"] is True
    assert payload["dry_run_plan_readback_enforced"] is True
    assert payload["dry_run_plan_is_passive"] is True
    assert payload["dry_run_plan_steps"][-1] == "stop_before_any_process_start"
    assert all(item["execution_allowed"] is False for item in payload["dry_run_plan"])
    assert all(item["side_effect_allowed"] is False for item in payload["dry_run_plan"])
    _assert_passive(payload)
    assert payload["next_patch"] == "L14.4 Microsoft Edge dedicated profile lifecycle preflight, still no launch"


def test_l14_03_cli_compact_json_is_parseable_token_not_echoed_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--request-launch-authorization", "--operator-confirmation-token", TOKEN, "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert TOKEN not in completed.stdout
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L14.3"
    assert payload["dry_run_plan_is_passive"] is True
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l14_03_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_launch_dry_run_plan_readback.md").read_text(encoding="utf-8")
    for phrase in [
        "L14.3 Microsoft Edge supervised launch dry-run plan readback",
        COMMAND,
        SOURCE_COMMAND,
        "L14.2 authorization gate remains accepted",
        "dry-run plan readback enforced",
        "dry-run plan is passive",
        "dry-run plan executed: false",
        "dry-run plan materialized as process args: false",
        "real subprocess invocation built: false",
        "launch authorization effective for execution: false",
        "browser process launch requested: false",
        "browser process launch authorized: false",
        "launch execution allowed: false",
        "Microsoft Edge first",
        "Opera second",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no git commit or git push",
        "no localhost PatchOps server",
        "no browser extension",
        "L14.4 Microsoft Edge dedicated profile lifecycle preflight, still no launch",
    ]:
        assert phrase in text
