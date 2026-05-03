from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_contract as contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_01_dry_run_handoff_contract_passes_without_side_effects() -> None:
    payload = contract.build_browser_start_dry_run_handoff_contract(PROJECT_ROOT, browser="edge")
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L4"
    assert payload["patch"] == "L4.1"
    assert payload["next_patch"] == "L4.2 Live adapter browser-start dry-run handoff CLI/readback"
    assert payload["browser"] == "edge"
    assert payload["dry_run_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False

    required_checks = {
        "l4_01_browser_target_is_modelled_only",
        "l4_01_prior_l3_final_acceptance_artifacts_present",
        "l4_01_contract_artifacts_present",
        "l4_01_doc_contains_dry_run_boundary",
        "l4_01_handoff_request_is_dry_run_only",
        "l4_01_startup_remains_not_allowed",
        "l4_01_no_browser_session_is_created",
        "l4_01_no_profile_directory_is_created",
        "l4_01_command_plan_is_readback_only",
        "l4_01_no_new_optional_browser_dependency_imports",
        "l4_01_payload_json_safe",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l4_01_handoff_models_edge_and_opera_without_starting_browser() -> None:
    edge_payload = contract.build_browser_start_dry_run_handoff_contract(PROJECT_ROOT, browser="edge")
    opera_payload = contract.build_browser_start_dry_run_handoff_contract(PROJECT_ROOT, browser="opera")

    for payload in (edge_payload, opera_payload):
        request = payload["handoff_request"]
        assert payload["ok"] is True
        assert request["kind"] == "browser_start_dry_run_handoff"
        assert request["dry_run_only"] is True
        assert request["startup_authorization_required"] is True
        assert request["startup_authorized"] is False
        assert request["startup_allowed"] is False
        assert request["profile_preflight_required"] is True
        assert request["browser_profile_preflight_phase"] == "L2 accepted"
        assert request["browser_start_authorization_phase"] == "L3 accepted"
        assert request["live_browser_start_phase"] == "not reached"
        assert "edge" in request["allowed_browsers"]
        assert "opera" in request["allowed_browsers"]
        assert "browser_start" in request["blocked_side_effects"]
        assert "selenium_import" in request["blocked_side_effects"]


def test_l4_01_rejects_unmodelled_browser_target() -> None:
    payload = contract.build_browser_start_dry_run_handoff_contract(PROJECT_ROOT, browser="firefox")
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is False
    assert payload["status"] == "FAIL"
    assert payload["browser"] == "firefox"
    assert checks["l4_01_browser_target_is_modelled_only"]["ok"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False


def test_l4_01_module_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract",
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "edge",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["browser"] == "edge"
    assert payload["dry_run_only"] is True
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["executed_validation_commands"] == []
    assert payload["selenium_imported"] is False
    assert "selenium" not in completed.stderr.lower()


def test_l4_01_command_plan_stays_readback_only() -> None:
    payload = contract.build_browser_start_dry_run_handoff_contract(PROJECT_ROOT, browser="edge")
    command_text = "\n".join(payload["handoff_readback_commands"])

    assert "live_adapter_browser_start_dry_run_handoff_contract" in command_text
    assert "--browser edge" in command_text
    assert "--browser opera" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "selenium" not in command_text.lower()
    assert "webdriver" not in command_text.lower()
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text
