from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_fixtures as fixtures

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_request_fixture_matrix_is_passive_and_json_safe() -> None:
    payload = fixtures.build_startup_request_fixture_matrix()

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.9"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["case_count"] >= 6

    encoded = json.dumps(payload, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded["name"] == "llm_browser_live_adapter_startup_request_fixture_matrix"


def test_startup_request_fixture_matrix_covers_expected_cases_and_blocks_all() -> None:
    payload = fixtures.build_startup_request_fixture_matrix()
    case_names = set(payload["case_names"])

    assert "default_edge_no_acknowledgements" in case_names
    assert "opera_all_side_effect_flags" in case_names
    assert "invalid_browser_send_request" in case_names
    assert "readback_only_operations" in case_names

    for case in payload["cases"]:
        assert case["startup_allowed"] is False
        assert case["browser_started"] is False
        assert case["browser_session_created"] is False
        assert case["side_effects_performed"] == []

    requested = {
        effect
        for case in payload["cases"]
        for effect in case["requested_side_effects"]
    }
    assert "start_browser" in requested
    assert "click_download" in requested
    assert "send_or_submit" in requested
    assert "read_page" in requested
    assert "detect_latest_assistant_reply" in requested


def test_startup_request_fixture_matrix_checks_are_named_and_green() -> None:
    payload = fixtures.build_startup_request_fixture_matrix()
    checks = {check["name"]: check for check in payload["checks"]}

    assert checks["fixture_matrix_has_core_cases"]["ok"] is True
    assert checks["all_fixture_decisions_block_startup"]["ok"] is True
    assert checks["all_fixture_decisions_create_no_browser_session"]["ok"] is True
    assert checks["requested_side_effects_modelled_not_executed"]["ok"] is True
    assert checks["invalid_browser_fixture_reported_without_side_effects"]["ok"] is True
    assert checks["fixture_matrix_json_safe"]["ok"] is True
    assert checks["no_optional_browser_dependency_imports"]["ok"] is True
    assert checks["fixture_gate_did_not_load_browser_optional_modules"]["ok"] is True


def test_startup_request_fixture_matrix_module_json_and_text_cli_are_passive() -> None:
    json_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_fixtures",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert json_completed.returncode == 0, json_completed.stderr
    payload = json.loads(json_completed.stdout)
    assert payload["ok"] is True
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []

    text_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_fixtures"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert text_completed.returncode == 0, text_completed.stderr
    assert "PatchOps LLM browser startup request fixture matrix" in text_completed.stdout
    assert "PatchOps LLM browser live adapter startup request fixture matrix" in text_completed.stdout
    assert "Browser    : not started" in text_completed.stdout
    assert "SideEffects: []" in text_completed.stdout
    assert "Next patch : L1.10 Live adapter startup request fixture matrix CLI/readback" in text_completed.stdout
