
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_preflight_fixtures as fixtures

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_profile_preflight_fixture_matrix_passes_without_side_effects() -> None:
    payload = fixtures.build_browser_profile_preflight_fixture_matrix(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L2"
    assert payload["patch"] == "L2.3"
    assert payload["next_patch"] == "L2.4 Live adapter browser profile preflight fixture matrix CLI/readback"
    assert payload["case_count"] == 6
    assert payload["missing_core_cases"] == []
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["base_preflight"]["ok"] is True

    required_checks = {
        "l2_profile_preflight_contract_still_passes",
        "l2_profile_fixture_matrix_has_core_cases",
        "all_profile_fixture_decisions_block_startup",
        "all_profile_fixture_decisions_create_no_browser_session",
        "all_profile_fixture_decisions_create_no_profile_directory",
        "profile_fixture_requested_side_effects_modelled_not_executed",
        "profile_fixture_invalid_browser_reported_without_side_effects",
        "profile_fixture_paths_are_modelled_only",
        "profile_fixture_matrix_json_safe",
        "no_optional_browser_dependency_imports",
        "l2_profile_fixture_matrix_did_not_load_browser_optional_modules",
    }
    assert required_checks <= set(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l2_profile_preflight_fixture_cases_cover_core_paths() -> None:
    payload = fixtures.build_browser_profile_preflight_fixture_matrix(PROJECT_ROOT)
    cases = {case["name"]: case for case in payload["cases"]}

    expected_cases = {
        "default_edge_no_acknowledgements",
        "opera_acknowledged_start_and_profile_request",
        "edge_acknowledged_profile_only_request",
        "invalid_browser_send_request",
        "custom_profile_root_and_name",
        "opera_optional_dependency_flag",
    }
    assert expected_cases == set(cases)

    assert cases["default_edge_no_acknowledgements"]["missing_acknowledgements"]
    assert cases["opera_acknowledged_start_and_profile_request"]["requested_side_effects"] == ["start_browser", "create_profile_directory"]
    assert cases["edge_acknowledged_profile_only_request"]["requested_side_effects"] == ["create_profile_directory"]
    assert cases["invalid_browser_send_request"]["invalid_fields"] == ["requested_browser"]
    assert cases["custom_profile_root_and_name"]["profile_name"] == "patchops-custom-fixture-profile"
    assert cases["opera_optional_dependency_flag"]["requested_side_effects"] == ["start_browser"]

    for case in cases.values():
        assert case["ok"] is True
        assert case["startup_allowed"] is False
        assert case["browser_started"] is False
        assert case["browser_session_created"] is False
        assert case["profile_directory_created"] is False
        assert case["side_effects_performed"] == []
        assert case["filesystem_writes_performed"] == []
        assert case["optional_browser_dependencies_required"] is False


def test_l2_profile_preflight_fixture_matrix_module_json_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures",
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
    assert payload["case_count"] == 6
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["profile_directory_created"] is False


def test_l2_profile_preflight_fixture_matrix_text_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures", "--repo-root", str(PROJECT_ROOT)],
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
    assert "Next patch : L2.4 Live adapter browser profile preflight fixture matrix CLI/readback" in stdout


def test_l2_profile_preflight_fixture_matrix_does_not_create_profile_root(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles"
    payload = fixtures.build_browser_profile_preflight_fixture_matrix(PROJECT_ROOT, profile_root=profile_root)

    assert payload["ok"] is True
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert not profile_root.exists()

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_preflight_fixtures",
            "--repo-root",
            str(PROJECT_ROOT),
            "--profile-root",
            str(profile_root),
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
    assert not profile_root.exists()


def test_l2_profile_preflight_fixture_matrix_preserves_cli_preflight_readback() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "profile-preflight",
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
    assert payload["startup_allowed"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
