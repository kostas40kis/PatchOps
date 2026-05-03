from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_launch_authorization_gate as l14_02

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-launch-authorization-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-launch-readiness-consolidation"
TOKEN = "EDGE_LAUNCH_AUTH_REVIEWED_NO_EXECUTION"


def _assert_passive(payload: dict) -> None:
    assert payload["launch_authorization_effective_for_execution"] is False
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


def test_l14_02_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l14_02_default_is_not_requested_not_granted_and_passive() -> None:
    payload = l14_02.build_edge_launch_authorization_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["patch"] == "L14.2"
    assert payload["source_patch"] == "L14.1"
    assert payload["source_l13_complete"] is True
    assert payload["launch_readiness_consolidated"] is True
    assert payload["launch_authorization_gate_enforced"] is True
    assert payload["request_launch_authorization_observed"] is False
    assert payload["operator_confirmation_token_valid"] is False
    assert payload["launch_authorization_granted_for_future_stage"] is False
    assert payload["launch_authorization_denied_reason"] == "launch_authorization_not_requested"
    _assert_passive(payload)


def test_l14_02_requested_without_token_is_denied_and_passive() -> None:
    payload = l14_02.build_edge_launch_authorization_gate(PROJECT_ROOT, request_launch_authorization=True)
    assert payload["ok"] is True
    assert payload["request_launch_authorization_observed"] is True
    assert payload["operator_confirmation_token_valid"] is False
    assert payload["launch_authorization_granted_for_future_stage"] is False
    assert payload["launch_authorization_denied_reason"] == "missing_or_invalid_operator_confirmation_token"
    _assert_passive(payload)


def test_l14_02_requested_with_token_grants_future_stage_only_and_stays_passive() -> None:
    payload = l14_02.build_edge_launch_authorization_gate(PROJECT_ROOT, request_launch_authorization=True, operator_confirmation_token=TOKEN)
    assert payload["ok"] is True
    assert payload["request_launch_authorization_observed"] is True
    assert payload["operator_confirmation_token_required"] is True
    assert payload["operator_confirmation_token_valid"] is True
    assert payload["authorization_token_echoed"] is False
    assert payload["launch_authorization_granted_for_future_stage"] is True
    assert payload["launch_authorization_denied_reason"] is None
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)
    assert payload["next_patch"] == "L14.3 Microsoft Edge supervised launch dry-run plan readback, still no launch"


def test_l14_02_cli_compact_json_is_parseable_and_token_is_not_echoed() -> None:
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
    assert payload["patch"] == "L14.2"
    assert payload["launch_authorization_granted_for_future_stage"] is True
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l14_02_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_launch_authorization_gate.md").read_text(encoding="utf-8")
    for phrase in [
        "L14.2 Microsoft Edge supervised launch authorization gate",
        COMMAND,
        SOURCE_COMMAND,
        "L14.1 launch-readiness consolidation remains accepted",
        "supervised launch authorization gate enforced",
        "authorization token is not echoed",
        "authorization can be granted only for a future stage",
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
        "L14.3 Microsoft Edge supervised launch dry-run plan readback, still no launch",
    ]:
        assert phrase in text
