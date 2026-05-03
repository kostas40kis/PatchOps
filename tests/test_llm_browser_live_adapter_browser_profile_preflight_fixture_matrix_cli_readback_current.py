from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops import cli
from patchops.llm_browser import commands

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _parser_choices() -> set[str]:
    parser = commands.build_parser()
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    return set()


def test_profile_preflight_fixtures_command_is_registered_in_llm_browser_parser() -> None:
    choices = _parser_choices()
    assert "profile-preflight" in choices
    assert "profile-preflight-fixtures" in choices


def test_profile_preflight_fixtures_patchops_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "profile-preflight-fixtures",
            "--repo-root",
            str(PROJECT_ROOT),
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
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L2.3"
    assert payload["phase"] == "L2"
    assert payload["case_count"] == 6
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["missing_core_cases"] == []

    case_names = set(payload["case_names"])
    assert "default_edge_no_acknowledgements" in case_names
    assert "opera_acknowledged_start_and_profile_request" in case_names
    assert "edge_acknowledged_profile_only_request" in case_names
    assert "invalid_browser_send_request" in case_names
    assert "custom_profile_root_and_name" in case_names
    assert "opera_optional_dependency_flag" in case_names

    cases = {case["name"]: case for case in payload["cases"]}
    assert all(case["ok"] is True for case in cases.values())
    assert cases["invalid_browser_send_request"]["invalid_fields"] == ["requested_browser"]
    assert cases["invalid_browser_send_request"]["side_effects_performed"] == []
    assert cases["custom_profile_root_and_name"]["profile_name"] == "patchops-custom-fixture-profile"
    assert cases["opera_acknowledged_start_and_profile_request"]["requested_side_effects"] == ["start_browser", "create_profile_directory"]

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["l2_profile_preflight_contract_still_passes"]["ok"] is True
    assert checks["all_profile_fixture_decisions_block_startup"]["ok"] is True
    assert checks["all_profile_fixture_decisions_create_no_profile_directory"]["ok"] is True
    assert checks["profile_fixture_requested_side_effects_modelled_not_executed"]["ok"] is True
    assert checks["l2_profile_fixture_matrix_did_not_load_browser_optional_modules"]["ok"] is True


def test_profile_preflight_fixtures_patchops_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "profile-preflight-fixtures", "--repo-root", str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout

    assert "PatchOps LLM browser profile preflight fixture matrix" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight fixture matrix" in stdout
    assert "Status     : PASS" in stdout
    assert "Cases      : 6" in stdout
    assert "Startup    : allowed=false" in stdout
    assert "BrowserRun : not started" in stdout
    assert "Profile    : created=false" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "default_edge_no_acknowledgements" in stdout
    assert "opera_acknowledged_start_and_profile_request" in stdout
    assert "Next patch : L2.4 Live adapter browser profile preflight fixture matrix CLI/readback" in stdout


def test_profile_preflight_fixtures_cli_main_routes_without_side_effects() -> None:
    result = cli.main([
        "llm-browser",
        "profile-preflight-fixtures",
        "--repo-root",
        str(PROJECT_ROOT),
        "--json",
        "--compact",
    ])
    assert result == 0


def test_profile_preflight_fixtures_help_mentions_command_without_starting_browser() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0
    assert "profile-preflight" in completed.stdout
    assert "profile-preflight-fixtures" in completed.stdout


def test_profile_preflight_fixtures_cli_does_not_create_profiles_or_write_files(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "profile-preflight-fixtures",
            "--repo-root",
            str(PROJECT_ROOT),
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
    assert payload["filesystem_writes_performed"] == []
    assert payload["profile_directory_created"] is False
    assert payload["browser_started"] is False
    assert not profile_root.exists()
