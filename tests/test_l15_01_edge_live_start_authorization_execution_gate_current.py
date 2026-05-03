from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate as l15_01

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"
TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"


def _assert_passive(payload: dict) -> None:
    assert payload["launch_execution_allowed"] is False
    assert payload["first_real_edge_start_allowed_in_l15_1"] is False
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


def test_l15_01_no_authorization_is_ok_but_execution_blocked() -> None:
    payload = l15_01.build_edge_live_start_authorization_execution_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L15.1"
    assert payload["phase"] == "L15"
    assert payload["source_patch"] == "L14.9"
    assert payload["source_l14_09_final_marker_accepted"] is True
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["active_browser"] == "edge"
    assert payload["opera_active_implementation_target"] is False
    assert payload["explicit_live_start_authorization_flag_required"] is True
    assert payload["explicit_live_start_authorization_token_required"] is True
    assert payload["explicit_live_start_authorization_flag_present"] is False
    assert payload["explicit_live_start_authorization_token_present"] is False
    assert payload["live_start_operator_authorization_complete"] is False
    assert payload["authorization_missing_keeps_execution_blocked"] is True
    assert payload["dedicated_profile_candidate_inherited_from_l14_09"] is True
    assert payload["default_edge_profile_rejected"] is True
    assert payload["default_profile_use_allowed"] is False
    assert payload["live_start_execution_gate_enforced"] is True
    assert payload["live_start_execution_gate_truthful"] is True
    assert payload["live_start_execution_gate_passive"] is True
    assert payload["l15_1_complete"] is True
    assert payload["remaining_l15_1_patches"] == []
    assert payload["required_repo_paths"]["ok"] is True
    assert payload["missing_doc_phrases"] == []
    _assert_passive(payload)


def test_l15_01_authorized_readback_still_does_not_start_edge() -> None:
    payload = l15_01.build_edge_live_start_authorization_execution_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        authorization_token=TOKEN,
    )
    assert payload["ok"] is True
    assert payload["explicit_live_start_authorization_flag_present"] is True
    assert payload["explicit_live_start_authorization_token_present"] is True
    assert payload["live_start_operator_authorization_complete"] is True
    assert payload["authorization_present_is_readback_only_in_l15_1"] is True
    assert payload["browser_process_launch_authorized"] is True
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l15_01_wrong_token_keeps_authorization_incomplete_and_blocked() -> None:
    payload = l15_01.build_edge_live_start_authorization_execution_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        authorization_token="WRONG",
    )
    assert payload["ok"] is True
    assert payload["explicit_live_start_authorization_flag_present"] is True
    assert payload["explicit_live_start_authorization_token_present"] is False
    assert payload["live_start_operator_authorization_complete"] is False
    assert payload["authorization_missing_keeps_execution_blocked"] is True
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l15_01_rejects_default_profile_path_and_stays_passive() -> None:
    payload = l15_01.build_edge_live_start_authorization_execution_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        authorization_token=TOKEN,
        profile_relative_path="Microsoft/Edge/User Data/Default",
    )
    assert payload["ok"] is False
    assert payload["default_edge_profile_requested"] is True
    assert payload["default_edge_profile_rejected"] is False
    assert payload["default_profile_use_allowed"] is False
    assert payload["launch_execution_allowed"] is False
    _assert_passive(payload)


def test_l15_01_opera_is_not_active_target_yet_and_stays_passive() -> None:
    payload = l15_01.build_edge_live_start_authorization_execution_gate(PROJECT_ROOT, browser="opera")
    assert payload["ok"] is False
    assert payload["browser"] == "opera"
    assert payload["microsoft_edge_first"] is True
    assert payload["opera_second"] is True
    assert payload["active_browser"] == "edge"
    assert payload["opera_active_implementation_target"] is False
    _assert_passive(payload)


def test_l15_01_command_is_registered() -> None:
    from patchops.llm_browser import commands

    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l15_01_cli_compact_json_is_parseable_and_passive_without_authorization() -> None:
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
    assert payload["patch"] == "L15.1"
    assert payload["explicit_live_start_authorization_flag_present"] is False
    assert payload["explicit_live_start_authorization_token_present"] is False
    assert payload["live_start_operator_authorization_complete"] is False
    _assert_passive(payload)


def test_l15_01_cli_compact_json_authorized_readback_is_still_passive() -> None:
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
            "--authorization-token",
            TOKEN,
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["live_start_operator_authorization_complete"] is True
    assert payload["authorization_present_is_readback_only_in_l15_1"] is True
    _assert_passive(payload)


def test_l15_01_doc_mentions_required_boundaries() -> None:
    text = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_live_start_authorization_execution_gate.md").read_text(encoding="utf-8")
    for phrase in [
        "L15.1 Microsoft Edge live-start authorization/execution gate",
        COMMAND,
        SOURCE_COMMAND,
        "Microsoft Edge first",
        "Opera second",
        "explicit live-start authorization flag required",
        "explicit live-start authorization token required",
        "dedicated profile candidate inherited from L14.9",
        "default Microsoft Edge profile rejected",
        "launch execution allowed: false",
        "L15.1 is passive",
        "auto-send remains false by default",
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
        "L15.2 Microsoft Edge live-start authorization/execution gate CLI readback",
    ]:
        assert phrase in text
