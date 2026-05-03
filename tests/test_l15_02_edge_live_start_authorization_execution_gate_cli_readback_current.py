from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate_cli_readback as l15_02

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
L14_SOURCE_COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"


def _assert_passive(payload: dict) -> None:
    assert payload["launch_execution_allowed"] is False
    assert payload["browser_process_launch_requested"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["selenium_required"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["profile_directory_creation_allowed"] is False
    assert payload["profile_directory_mutation_allowed"] is False
    assert payload["profile_directory_created"] is False
    assert payload["profile_directory_mutated"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["localhost_patchops_server_started"] is False
    assert payload["browser_extension_used"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["auto_send_allowed"] is False


def test_l15_02_payload_proves_l15_1_cli_readbacks_and_stays_passive() -> None:
    payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L15.2"
    assert payload["phase"] == "L15"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l14_source_command_name"] == L14_SOURCE_COMMAND
    assert payload["source_patch"] == "L15.1"
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["opera_active_implementation_target"] is False
    assert payload["cli_readback_only"] is True
    assert payload["compact_json_readback"] is True
    assert payload["no_authorization_readback_ok"] is True
    assert payload["authorized_readback_ok"] is True
    assert payload["authorization_is_readback_only_in_l15_2"] is True
    assert payload["l15_2_complete"] is True
    assert payload["remaining_l15_2_patches"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_doc_phrases"] == []
    assert payload["required_repo_paths"]["ok"] is True
    _assert_passive(payload)


def test_l15_02_no_auth_and_authorized_source_summaries_are_truthful() -> None:
    payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(PROJECT_ROOT)
    no_auth = payload["no_auth_readback"]
    authorized = payload["authorized_readback"]

    assert no_auth["patch"] == "L15.1"
    assert no_auth["ok"] is True
    assert no_auth["live_start_operator_authorization_complete"] is False
    assert no_auth["authorization_missing_keeps_execution_blocked"] is True
    assert no_auth["authorization_present_is_readback_only_in_l15_1"] is False
    assert no_auth["browser_process_launch_authorized"] is False
    assert no_auth["launch_execution_allowed"] is False

    assert authorized["patch"] == "L15.1"
    assert authorized["ok"] is True
    assert authorized["live_start_operator_authorization_complete"] is True
    assert authorized["authorization_missing_keeps_execution_blocked"] is False
    assert authorized["authorization_present_is_readback_only_in_l15_1"] is True
    assert authorized["browser_process_launch_authorized"] is True
    assert authorized["launch_execution_allowed"] is False
    assert authorized["browser_started"] is False
    assert authorized["edge_process_started"] is False
    assert authorized["selenium_imported_by_readback"] is False


def test_l15_02_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert SOURCE_COMMAND in names
    assert COMMAND in names


def test_l15_02_cli_compact_json_is_parseable_and_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", COMMAND, "--repo-root", str(PROJECT_ROOT), "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L15.2"
    assert payload["no_authorization_readback_ok"] is True
    assert payload["authorized_readback_ok"] is True
    assert payload["authorization_is_readback_only_in_l15_2"] is True
    _assert_passive(payload)


def test_l15_02_does_not_import_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l15_02_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_live_start_authorization_execution_gate_cli_readback.md").read_text(encoding="utf-8")
    for phrase in [
        "L15.2 Microsoft Edge live-start authorization/execution gate CLI readback",
        COMMAND,
        SOURCE_COMMAND,
        L14_SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "compact JSON readback",
        "no-authorization readback",
        "explicitly-authorized readback",
        "authorization is readback-only in L15.2",
        "launch execution allowed: false",
        "L15.2 is passive",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no profile directory mutation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "no git commit or git push",
        "L15.3 first controlled Microsoft Edge open proof using dedicated profile only",
    ]:
        assert phrase in text
