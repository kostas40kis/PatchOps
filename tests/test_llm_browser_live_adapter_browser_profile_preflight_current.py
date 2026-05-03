
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_preflight as preflight

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_browser_profile_preflight_passes_without_side_effects() -> None:
    payload = preflight.build_default_browser_profile_preflight(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["request_status"] == "BLOCKED_PREFLIGHT_CONTRACT_ONLY"
    assert payload["phase"] == "L2"
    assert payload["patch"] == "L2.1"
    assert payload["next_patch"] == "L2.2 Live adapter browser profile preflight CLI/readback"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["supported_browsers"] == ["edge", "opera"]
    assert payload["normalized_browser"] == "edge"
    assert payload["manual_login_required"] is True
    assert payload["dedicated_profile_required"] is True

    required_checks = {
        "l1_final_acceptance_marker_still_passes",
        "l2_profile_preflight_models_supported_browsers",
        "l2_profile_preflight_requires_dedicated_profile",
        "l2_profile_preflight_requires_manual_login_only",
        "l2_profile_preflight_models_requested_side_effects_but_executes_none",
        "l2_profile_preflight_does_not_create_profile_or_browser",
        "l2_profile_preflight_blocks_startup",
        "l2_profile_preflight_acknowledgement_contract_reported",
        "l2_profile_preflight_payload_json_safe",
        "no_optional_browser_dependency_imports",
        "l2_profile_preflight_did_not_load_browser_optional_modules",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l2_browser_profile_preflight_models_requests_but_still_blocks() -> None:
    request = preflight.build_browser_profile_preflight_request(
        PROJECT_ROOT,
        requested_browser="opera",
        acknowledgements=preflight.REQUIRED_ACKNOWLEDGEMENTS,
        allow_browser_start=True,
        allow_profile_directory_creation=True,
        allow_optional_browser_dependencies=True,
    )
    payload = preflight.evaluate_browser_profile_preflight(request, PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["normalized_browser"] == "opera"
    assert payload["missing_acknowledgements"] == []
    assert payload["requested_side_effects"] == ["start_browser", "create_profile_directory"]
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []


def test_l2_browser_profile_preflight_references_l1_acceptance_marker() -> None:
    payload = preflight.build_default_browser_profile_preflight(PROJECT_ROOT)
    marker = payload["l1_final_acceptance_marker"]

    assert marker["patch"] == "L1.17"
    assert marker["ok"] is True
    assert marker["startup_allowed"] is False
    assert marker["browser_started"] is False
    assert marker["git_commit_executed"] is False
    assert marker["git_push_executed"] is False


def test_l2_browser_profile_preflight_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight",
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "opera",
            "--ack-all",
            "--allow-browser-start",
            "--allow-profile-directory-creation",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert payload["normalized_browser"] == "opera"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["requested_side_effects"] == ["start_browser", "create_profile_directory"]


def test_l2_browser_profile_preflight_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout

    assert "PatchOps LLM browser profile preflight contract" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight contract" in stdout
    assert "Status     : PASS" in stdout
    assert "Request    : BLOCKED_PREFLIGHT_CONTRACT_ONLY" in stdout
    assert "Profile    : mode=dedicated created=false" in stdout
    assert "Startup    : allowed=false" in stdout
    assert "BrowserRun : not started" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "Next patch : L2.2 Live adapter browser profile preflight CLI/readback" in stdout


def test_l2_browser_profile_preflight_module_exposes_alias() -> None:
    assert preflight.build_profile_preflight_contract(PROJECT_ROOT)["ok"] is True
