from __future__ import annotations

import json
import sys


def _matrix():
    from patchops.llm_browser import live_adapter_browser_start_authorization_fixtures as matrix

    return matrix


def test_l3_3_fixture_matrix_contains_expected_cases():
    matrix = _matrix()
    payload = matrix.build_l3_browser_start_authorization_fixture_matrix(repo_root=".")
    assert payload["patch"] == "L3.3"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L3.4 Live adapter browser-start authorization fixture matrix CLI/readback"
    assert set(payload["case_ids"]) == {
        "edge_default_missing_acknowledgements",
        "opera_ack_all_permission_flags_modelled_only",
        "unsupported_browser_rejected",
        "shared_profile_rejected",
        "download_paste_send_side_effects_blocked",
    }


def test_l3_3_fixture_cases_remain_passive_and_side_effect_free():
    matrix = _matrix()
    payload = matrix.build_l3_browser_start_authorization_fixture_matrix(repo_root=".")
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    for case in payload["cases"]:
        assert case["startup_authorized"] is False
        assert case["browser_started"] is False
        assert case["browser_session_created"] is False
        assert case["profile_directory_created"] is False
        assert case["side_effects_performed"] == []
        assert case["filesystem_writes_performed"] == []
        assert case["optional_browser_dependencies_required"] is False
        assert case["expectations_met"] is True


def test_l3_3_fixture_matrix_expected_rejections_are_explicit():
    matrix = _matrix()
    payload = matrix.build_l3_browser_start_authorization_fixture_matrix(repo_root=".")
    by_id = {case["case_id"]: case for case in payload["cases"]}
    assert by_id["unsupported_browser_rejected"]["ok"] is False
    assert "requested_browser" in by_id["unsupported_browser_rejected"]["invalid_fields"]
    assert "unsupported_browser" in by_id["unsupported_browser_rejected"]["blocked_reasons"]
    assert by_id["shared_profile_rejected"]["ok"] is False
    assert "requested_profile_mode" in by_id["shared_profile_rejected"]["invalid_fields"]
    assert "default_or_shared_profile_not_allowed" in by_id["shared_profile_rejected"]["blocked_reasons"]
    assert by_id["opera_ack_all_permission_flags_modelled_only"]["ok"] is True
    assert "live_side_effects_requested_but_modelled_only" in by_id["opera_ack_all_permission_flags_modelled_only"]["blocked_reasons"]


def test_l3_3_fixture_matrix_does_not_import_selenium_or_optional_browser_dependencies():
    before = set(sys.modules)
    matrix = _matrix()
    payload = matrix.build_l3_browser_start_authorization_fixture_matrix(repo_root=".")
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {
        root
        for root in forbidden_roots
        if any(name == root or name.startswith(root + ".") for name in newly_loaded)
    }
    assert imported == set()
    assert payload["forbidden_optional_browser_imports_loaded"] == []


def test_l3_3_fixture_matrix_module_json_smoke(capsys):
    matrix = _matrix()
    exit_code = matrix.main(["--repo-root", ".", "--json", "--compact"])
    captured = capsys.readouterr()
    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["patch"] == "L3.3"
    assert payload["ok"] is True
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
