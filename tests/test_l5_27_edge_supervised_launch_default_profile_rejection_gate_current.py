from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_supervised_launch_default_profile_rejection_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-live-start-profile-gate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l5_27_pytest_candidate_should_not_be_created"


def _commands():
    return importlib.import_module("patchops.llm_browser.commands")


def _subcommands(parser: argparse.ArgumentParser) -> set[str]:
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    raise AssertionError("llm-browser parser did not expose subcommands")


def test_l5_27_default_profile_candidate_is_rejected() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.27"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["edge_first"] is True
    assert payload["browser_priority"] == ["edge", "opera"]
    assert payload["next_patch"] == "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract"

    assert payload["explicit_operator_authorization_required"] is True
    assert payload["explicit_operator_authorization_present"] is True
    assert payload["authorization_flag_required"] == "--allow-live-start"
    assert payload["profile_dir_argument_required"] == "--profile-dir"
    assert payload["profile_dir_argument_present"] is True
    assert payload["default_profile_forbidden"] is True
    assert payload["default_profile_rejection_gate_enforced"] is True
    assert payload["default_profile_path_forbidden"] is True
    assert payload["default_microsoft_edge_profile_forbidden"] is True
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"

    assert payload["startup_authorized"] is True
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is True
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

    required_checks = {
        "l5_26_edge_profile_gate_still_passes",
        "l5_26_edge_profile_gate_remains_passive",
        "l5_26_source_command_still_registered",
        "l5_27_default_profile_rejection_command_registered",
        "edge_l5_required_command_set_registered",
        "edge_l5_required_source_docs_tests_present",
        "edge_l5_docs_contain_default_profile_rejection_boundary",
        "l5_27_command_plan_is_readback_only",
        "adapter_logic_executes_no_validation_commands",
        "default_profile_rejection_gate_is_enforced",
        "default_profile_candidate_is_detected_when_supplied",
        "default_profile_path_is_rejected",
        "dedicated_non_default_profile_remains_passive_blocked",
        "edge_remains_first_supported_live_browser",
        "opera_remains_second_supported_live_browser",
        "selenium_not_imported_by_default_profile_rejection_gate",
        "no_browser_profile_or_adapter_side_effects",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l5_27_dedicated_non_default_profile_is_not_rejected_but_remains_passive() -> None:
    if DEDICATED_PROFILE.exists():
        raise AssertionError(f"test profile marker unexpectedly exists before readback: {DEDICATED_PROFILE}")

    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    rejection = payload["default_profile_rejection_gate"]

    assert payload["ok"] is True
    assert payload["profile_dir_argument_present"] is True
    assert payload["default_profile_candidate_detected"] is False
    assert payload["default_profile_path_rejected"] is False
    assert payload["dedicated_non_default_profile_present"] is True
    assert payload["dedicated_non_default_profile_remains_passive_blocked"] is True
    assert payload["default_profile_rejection_gate_status"] == "AUTHORIZED_NON_DEFAULT_PROFILE_PRESENT_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE"
    assert rejection["phase_allows_live_start"] is False

    assert payload["startup_authorized"] is True
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is True
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert not DEDICATED_PROFILE.exists()


def test_l5_27_missing_authorization_or_profile_still_blocks_before_launch() -> None:
    no_auth = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_profile = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )

    assert no_auth["ok"] is True
    assert no_auth["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert no_auth["startup_allowed"] is False
    assert no_auth["browser_started"] is False
    assert no_auth["profile_directory_created"] is False

    assert missing_profile["ok"] is True
    assert missing_profile["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
    assert missing_profile["profile_dir_argument_present"] is False
    assert missing_profile["startup_allowed"] is False
    assert missing_profile["browser_started"] is False
    assert missing_profile["profile_directory_created"] is False


def test_l5_27_wraps_accepted_l5_26_profile_gate() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    summary = payload["l5_26_summary"]
    source = payload["l5_26_edge_profile_gate"]

    assert summary["ok"] is True
    assert summary["status"] == "PASS"
    assert summary["patch"] == "L5.26"
    assert summary["command_name"] == SOURCE_COMMAND
    assert summary["authorization_flag_required"] == "--allow-live-start"
    assert summary["profile_dir_argument_required"] == "--profile-dir"
    assert summary["dedicated_profile_argument_gate_enforced"] is True
    assert summary["default_profile_forbidden"] is True
    assert summary["default_profile_path_rejected"] is True
    assert summary["profile_gate_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
    assert summary["browser_started"] is False
    assert summary["edge_process_started"] is False
    assert summary["browser_session_created"] is False
    assert summary["profile_directory_created"] is False
    assert summary["filesystem_writes_performed"] == []
    assert summary["adapter_filesystem_writes_performed"] == []
    assert summary["side_effects_performed"] == []
    assert source["ok"] is True
    assert source["status"] == "PASS"
    assert source["patch"] == "L5.26"


def test_l5_27_required_command_set_is_registered_in_llm_browser_cli() -> None:
    commands = _commands()
    names = set(commands.llm_browser_command_names())
    subcommands = _subcommands(commands.build_parser())
    for command in gate.REQUIRED_COMMANDS:
        assert command in names
        assert command in subcommands


def test_l5_27_command_plan_is_readback_only() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(PROJECT_ROOT)
    state = payload["command_plan_state"]
    plan = payload["command_plan"]

    assert state["ok"] is True
    assert state["forbidden_present"] == []
    assert state["missing_fragments"] == []
    assert state["executed_by_adapter_logic"] == []
    assert payload["executed_validation_commands"] == []
    assert len(plan) == 6
    assert any("compileall patchops/llm_browser tests" in command for command in plan)
    assert any("test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py" in command for command in plan)
    assert any("test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py" in command for command in plan)
    assert any("live_adapter_edge_supervised_launch_default_profile_rejection_gate" in command for command in plan)
    assert any(COMMAND in command for command in plan)
    assert any("--allow-live-start" in command for command in plan)
    assert any("--profile-dir" in command for command in plan)
    assert any("Microsoft\\Edge\\User Data\\Default" in command for command in plan)
    assert any("git status --short --branch" in command for command in plan)


def test_l5_27_main_cli_default_profile_rejected_json() -> None:
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
            DEFAULT_PROFILE,
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L5.27"
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
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
    assert payload["selenium_imported_by_readback"] is False


def test_l5_27_module_cli_text_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_edge_supervised_launch_default_profile_rejection_gate",
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
            "--profile-dir",
            DEFAULT_PROFILE,
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=240,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps L5.27 Microsoft Edge supervised-launch default profile rejection gate" in stdout
    assert "Status            : PASS" in stdout
    assert "Command           : browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate" in stdout
    assert "Source Command    : browser-start-supervised-launch-edge-live-start-profile-gate" in stdout
    assert "Default Forbidden : True" in stdout
    assert "Default Detected  : True" in stdout
    assert "Default Rejected  : True" in stdout
    assert "Gate Status       : BLOCKED_DEFAULT_PROFILE_FORBIDDEN" in stdout
    assert "Startup Allowed   : False" in stdout
    assert "Live Performed    : False" in stdout
    assert "Browser Started   : False" in stdout
    assert "Edge Started      : False" in stdout
    assert "Session Created   : False" in stdout
    assert "Driver Created    : False" in stdout
    assert "Profile Created   : False" in stdout
    assert "SideEffects       : []" in stdout
    assert "Selenium Import   : False" in stdout
    assert "Next Patch        : L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract" in stdout


def test_l5_27_readback_does_not_import_selenium() -> None:
    before = set(sys.modules)
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    assert not any(name == "selenium" or name.startswith("selenium.") for name in newly_loaded)


def test_l5_27_docs_are_present_and_passive() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(PROJECT_ROOT)
    doc_state = payload["doc_state"]
    assert doc_state["ok"] is True
    assert doc_state["missing_docs"] == []
    assert doc_state["missing_phrases"] == {}

    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.27 Microsoft Edge supervised launch default profile rejection gate",
        "browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate",
        "browser-start-supervised-launch-edge-live-start-profile-gate",
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "--profile-dir",
        "default profile rejection gate enforced",
        "default Microsoft Edge profile forbidden",
        "default profile candidate detected",
        "default profile path rejected",
        "dedicated non-default profile remains passive-blocked",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract",
    ]
    for phrase in required:
        assert phrase in text


def test_l5_27a_missing_auth_and_missing_profile_readbacks_are_healthy_and_passive() -> None:
    no_auth = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_profile = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )

    assert no_auth["ok"] is True
    assert no_auth["status"] == "PASS"
    assert no_auth["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert no_auth["startup_allowed"] is False
    assert no_auth["live_start_performed"] is False
    assert no_auth["browser_started"] is False
    assert no_auth["edge_process_started"] is False
    assert no_auth["browser_session_created"] is False
    assert no_auth["driver_created"] is False
    assert no_auth["profile_directory_created"] is False
    assert no_auth["filesystem_writes_performed"] == []
    assert no_auth["adapter_filesystem_writes_performed"] == []
    assert no_auth["side_effects_performed"] == []
    assert no_auth["selenium_imported_by_readback"] is False

    l5_26_no_auth = no_auth["l5_26_summary"]
    # L5.27 deliberately feeds L5.26 a default Edge profile here. L5.26 may
    # report the expected default-profile refusal, but it must remain passive.
    assert l5_26_no_auth["patch"] == "L5.26"
    assert l5_26_no_auth["command_name"] == SOURCE_COMMAND
    assert l5_26_no_auth["default_profile_forbidden"] is True
    assert l5_26_no_auth["default_profile_path_rejected"] is True
    assert l5_26_no_auth["status"] in {"PASS", "FAIL"}
    assert l5_26_no_auth["startup_allowed"] is False
    assert l5_26_no_auth["live_start_performed"] is False
    assert l5_26_no_auth["browser_started"] is False
    assert l5_26_no_auth["profile_directory_created"] is False
    assert l5_26_no_auth["filesystem_writes_performed"] == []
    assert l5_26_no_auth["adapter_filesystem_writes_performed"] == []
    assert l5_26_no_auth["side_effects_performed"] == []
    assert l5_26_no_auth["selenium_imported_by_readback"] is False

    assert missing_profile["ok"] is True
    assert missing_profile["status"] == "PASS"
    assert missing_profile["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
    assert missing_profile["profile_dir_argument_present"] is False
    assert missing_profile["startup_allowed"] is False
    assert missing_profile["live_start_performed"] is False
    assert missing_profile["browser_started"] is False
    assert missing_profile["edge_process_started"] is False
    assert missing_profile["browser_session_created"] is False
    assert missing_profile["driver_created"] is False
    assert missing_profile["profile_directory_created"] is False
    assert missing_profile["filesystem_writes_performed"] == []
    assert missing_profile["adapter_filesystem_writes_performed"] == []
    assert missing_profile["side_effects_performed"] == []
    assert missing_profile["selenium_imported_by_readback"] is False

    l5_26_missing_profile = missing_profile["l5_26_summary"]
    assert l5_26_missing_profile["ok"] is True
    assert l5_26_missing_profile["status"] == "PASS"
    assert l5_26_missing_profile["patch"] == "L5.26"
    assert l5_26_missing_profile["startup_allowed"] is False
    assert l5_26_missing_profile["live_start_performed"] is False
    assert l5_26_missing_profile["browser_started"] is False
    assert l5_26_missing_profile["profile_directory_created"] is False
    assert l5_26_missing_profile["filesystem_writes_performed"] == []
    assert l5_26_missing_profile["adapter_filesystem_writes_performed"] == []
    assert l5_26_missing_profile["side_effects_performed"] == []
    assert l5_26_missing_profile["selenium_imported_by_readback"] is False


def test_l5_27b_no_auth_with_malformed_separator_path_still_blocks_without_side_effects() -> None:
    malformed_default_profile = "C:" + "\x1f".join(
        ["Users", "kostas", "AppData", "Local", "Microsoft", "Edge", "User Data", "Default"]
    )
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=malformed_default_profile,
    )

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert payload["explicit_operator_authorization_present"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is False
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
    assert payload["selenium_imported_by_readback"] is False

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["dedicated_non_default_profile_remains_passive_blocked"]["ok"] is True
    assert checks["no_browser_profile_or_adapter_side_effects"]["ok"] is True


def test_l5_27c_no_auth_real_default_profile_accepts_wrapped_l5_26_default_refusal() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEFAULT_PROFILE,
    )
    checks = {check["name"]: check for check in payload["checks"]}
    wrapped = payload["l5_26_summary"]

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
    assert payload["explicit_operator_authorization_present"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is False
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
    assert payload["selenium_imported_by_readback"] is False

    # L5.26 may reject this deliberately supplied default profile, but it must
    # remain fully passive and safe.
    assert wrapped["patch"] == "L5.26"
    assert wrapped["command_name"] == SOURCE_COMMAND
    assert wrapped["default_profile_forbidden"] is True
    assert wrapped["default_profile_path_rejected"] is True
    assert wrapped["startup_allowed"] is False
    assert wrapped["live_start_performed"] is False
    assert wrapped["browser_started"] is False
    assert wrapped["edge_process_started"] is False
    assert wrapped["browser_session_created"] is False
    assert wrapped["driver_created"] is False
    assert wrapped["profile_directory_created"] is False
    assert wrapped["filesystem_writes_performed"] == []
    assert wrapped["adapter_filesystem_writes_performed"] == []
    assert wrapped["side_effects_performed"] == []
    assert wrapped["selenium_imported_by_readback"] is False

    assert checks["l5_26_edge_profile_gate_still_passes"]["ok"] is True
    assert checks["l5_26_edge_profile_gate_remains_passive"]["ok"] is True
    assert checks["default_profile_path_is_rejected"]["ok"] is True
    assert checks["no_browser_profile_or_adapter_side_effects"]["ok"] is True


def test_l5_27c_authorized_default_profile_still_rejected_without_browser_side_effects() -> None:
    payload = gate.build_edge_supervised_launch_default_profile_rejection_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["explicit_operator_authorization_present"] is True
    assert payload["default_profile_candidate_detected"] is True
    assert payload["default_profile_path_rejected"] is True
    assert payload["default_profile_rejection_gate_status"] == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
    assert payload["startup_allowed"] is False
    assert payload["live_start_requested"] is True
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert checks["l5_26_edge_profile_gate_still_passes"]["ok"] is True
    assert checks["l5_26_edge_profile_gate_remains_passive"]["ok"] is True
    assert checks["default_profile_path_is_rejected"]["ok"] is True

