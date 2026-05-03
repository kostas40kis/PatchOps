from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_03_fixture_cases_cover_edge_opera_and_rejection() -> None:
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures import fixture_cases

    cases = fixture_cases()
    case_ids = {case.case_id for case in cases}
    browsers = {case.browser.strip().lower() for case in cases}

    assert "edge_dry_run_handoff_passive" in case_ids
    assert "opera_dry_run_handoff_passive" in case_ids
    assert "unsupported_browser_rejected_without_startup" in case_ids
    assert {"edge", "opera", "firefox"}.issubset(browsers)


def test_l4_03_fixture_matrix_is_passive_and_ok() -> None:
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures import (
        build_browser_start_dry_run_handoff_fixture_matrix,
    )

    payload = build_browser_start_dry_run_handoff_fixture_matrix(PROJECT_ROOT)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.3"
    assert payload["next_patch"] == "L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback"
    assert payload["case_count"] >= 4
    assert all(case["case_ok"] for case in payload["cases"])
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


def test_l4_03_each_case_preserves_no_startup_side_effects() -> None:
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures import (
        build_browser_start_dry_run_handoff_fixture_matrix,
    )

    payload = build_browser_start_dry_run_handoff_fixture_matrix(PROJECT_ROOT)

    for case in payload["cases"]:
        result = case["result"]
        assert result["startup_allowed"] is False
        assert result["browser_started"] is False
        assert result["browser_session_created"] is False
        assert result["driver_created"] is False
        assert result["profile_directory_created"] is False
        assert result["filesystem_writes_performed"] == []
        assert result["side_effects_performed"] == []
        assert result["selenium_imported"] is False


def test_l4_03_matrix_command_plan_stays_readback_only() -> None:
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures import (
        build_browser_start_dry_run_handoff_fixture_matrix,
    )

    payload = build_browser_start_dry_run_handoff_fixture_matrix(PROJECT_ROOT)
    command_text = "\n".join(payload["readback_commands"]).lower()

    assert "live_adapter_browser_start_dry_run_handoff_fixtures" in command_text
    assert "--browser edge" in command_text
    assert "--browser opera" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "selenium" not in command_text
    assert "webdriver" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l4_03_json_main_is_compact_and_passive(capsys) -> None:
    from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_fixtures as matrix

    before = set(sys.modules)
    rc = matrix.main(["--repo-root", str(PROJECT_ROOT), "--json", "--compact"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    after = set(sys.modules)

    assert rc == 0
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.3"
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported"] is False

    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "playwright", "pyppeteer"}
    assert not any(name == root or name.startswith(root + ".") for root in forbidden_roots for name in newly_loaded)


def test_l4_03_docs_state_next_patch_and_boundary() -> None:
    doc = PROJECT_ROOT / "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix.md"
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "L4.3 Live adapter browser-start dry-run handoff fixture matrix" in text
    assert "fixture matrix" in text
    assert "dry-run-only" in text
    assert "L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback" in text
    assert "no Selenium import" in text
    assert "no browser start" in text
    assert "no profile directory creation" in text
    assert "no adapter filesystem writes" in text
    assert "no click/download/paste/send/package-run side effect" in text
