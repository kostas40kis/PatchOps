from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l5_03_fixture_cases_cover_edge_opera_and_rejections() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures import fixture_cases

    cases = fixture_cases()
    case_ids = {case.case_id for case in cases}
    browsers = {case.browser.strip().lower() for case in cases}
    decisions = {case.operator_decision.strip().lower() for case in cases}

    assert "edge_review_only_passive" in case_ids
    assert "opera_prepare_only_passive" in case_ids
    assert "unsupported_browser_rejected_without_startup" in case_ids
    assert "invalid_operator_decision_rejected_without_startup" in case_ids
    assert {"edge", "opera", "firefox"}.issubset(browsers)
    assert {"review_only", "prepare_only", "launch_now"}.issubset(decisions)


def test_l5_03_fixture_matrix_is_passive_and_ok() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures import (
        build_supervised_launch_handoff_fixture_matrix,
    )

    payload = build_supervised_launch_handoff_fixture_matrix(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L5.3"
    assert payload["next_patch"] == "L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback"
    assert payload["case_count"] >= 5
    assert all(case["case_ok"] for case in payload["cases"])
    assert payload["modelled_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_driver_session_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []
    json.dumps(payload, sort_keys=True)


def test_l5_03_each_case_preserves_no_startup_side_effects() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures import (
        build_supervised_launch_handoff_fixture_matrix,
    )

    payload = build_supervised_launch_handoff_fixture_matrix(PROJECT_ROOT)

    for case in payload["cases"]:
        result = case["result"]
        assert result["startup_authorized"] is False
        assert result["startup_allowed"] is False
        assert result["live_driver_session_allowed"] is False
        assert result["browser_started"] is False
        assert result["browser_session_created"] is False
        assert result["driver_created"] is False
        assert result["profile_directory_created"] is False
        assert result["filesystem_writes_performed"] == []
        assert result["side_effects_performed"] == []
        assert result["optional_browser_dependencies_required"] is False
        assert result["selenium_imported"] is False
        assert result["executed_validation_commands"] == []


def test_l5_03_expected_rejections_are_explicit_and_side_effect_free() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures import (
        build_supervised_launch_handoff_fixture_matrix,
    )

    payload = build_supervised_launch_handoff_fixture_matrix(PROJECT_ROOT)
    by_id = {case["case_id"]: case for case in payload["cases"]}

    unsupported = by_id["unsupported_browser_rejected_without_startup"]
    assert unsupported["expected_ok"] is False
    assert unsupported["result"]["ok"] is False
    assert unsupported["result"]["status"] == "FAIL"
    assert unsupported["result"]["browser"] == "firefox"
    assert unsupported["result"]["browser_started"] is False

    invalid_decision = by_id["invalid_operator_decision_rejected_without_startup"]
    assert invalid_decision["expected_ok"] is False
    assert invalid_decision["result"]["ok"] is False
    assert invalid_decision["result"]["operator_decision"] == "launch_now"
    assert invalid_decision["result"]["startup_allowed"] is False


def test_l5_03_module_cli_json_smoke_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures",
            "--repo-root",
            str(PROJECT_ROOT),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L5.3"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported"] is False


def test_l5_03_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L5.3 Browser Start Supervised Launch Handoff Fixture Matrix" in stdout
    assert "Status              : PASS" in stdout
    assert "Browser Started     : False" in stdout
    assert "Selenium Imported   : False" in stdout
    assert "Next Patch          : L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback" in stdout


def test_l5_03_readback_command_plan_has_no_live_or_git_side_effects() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures import (
        build_supervised_launch_handoff_fixture_matrix,
    )

    payload = build_supervised_launch_handoff_fixture_matrix(PROJECT_ROOT)
    plan = "\n".join(payload["readback_commands"]).lower()
    forbidden_fragments = (
        "git commit",
        "git push",
        "run-package",
        "llm-browser open",
        "open --browser",
        "run-once",
        "watch-downloads",
        "selenium",
        "webdriver",
        "click_download",
        "paste_to_composer",
        "send_or_submit",
    )
    assert all(fragment not in plan for fragment in forbidden_fragments)
