from __future__ import annotations

import importlib
import json
import sys


def _module():
    return importlib.import_module(
        "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract"
    )


def test_l5_01_default_contract_is_passive_and_json_safe():
    mod = _module()
    payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(".")
    assert payload["patch"] == "L5.1"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["modelled_only"] is True
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_driver_session_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert "L5.2 Live adapter browser-start supervised launch handoff CLI/readback" in payload["next_patch"]
    json.dumps(payload, sort_keys=True)


def test_l5_01_handoff_request_is_data_only_for_edge_and_opera():
    mod = _module()
    for browser in ("edge", "opera"):
        payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(
            ".",
            browser=browser,
            operator_decision="review_only",
        )
        request = payload["handoff_request"]
        assert payload["ok"] is True
        assert request["browser"] == browser
        assert request["operator_decision"] == "review_only"
        assert request["modelled_only"] is True
        assert request["startup_allowed"] is False
        assert request["live_driver_session_allowed"] is False
        assert request["profile_directory_creation_allowed"] is False


def test_l5_01_invalid_browser_fails_without_side_effects():
    mod = _module()
    payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(
        ".",
        browser="firefox",
        operator_decision="review_only",
    )
    assert payload["ok"] is False
    assert payload["status"] == "FAIL"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_l5_01_command_plan_is_readback_only():
    mod = _module()
    payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(".")
    command_plan = "\n".join(payload["handoff_readback_commands"]).lower()
    forbidden = (
        "git commit",
        "git push",
        "run-package",
        "llm-browser open",
        "open --browser",
        "run-once",
        "watch-downloads",
        "start_browser",
        "webdriver",
        "selenium",
        "click_download",
        "paste_to_composer",
        "send_message",
        "send_or_submit",
    )
    assert all(fragment not in command_plan for fragment in forbidden)


def test_l5_01_does_not_import_selenium_or_optional_browser_dependencies():
    before = set(sys.modules)
    mod = _module()
    payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(".")
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {
        root
        for root in forbidden_roots
        if any(name == root or name.startswith(root + ".") for name in newly_loaded)
    }
    assert imported == set()
    assert payload["selenium_imported"] is False


def test_l5_01_text_render_mentions_next_patch_and_no_browser_start():
    mod = _module()
    payload = mod.build_l5_browser_start_supervised_launch_handoff_contract(".")
    text = mod.render_text(payload)
    assert "L5.2 Live adapter browser-start supervised launch handoff CLI/readback" in text
    assert "Browser Started     : False" in text
    assert "Startup Allowed     : False" in text
