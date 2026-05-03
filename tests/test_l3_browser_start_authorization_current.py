from __future__ import annotations

import importlib
import json
import sys


def _module():
    return importlib.import_module("patchops.llm_browser.live_adapter_browser_start_authorization")


def test_l3_1_default_contract_is_passive_and_json_safe():
    mod = _module()
    payload = mod.build_l3_browser_start_authorization_contract(".")
    assert payload["patch"] == "L3.1"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_authorized"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert "L3.2 Live adapter explicit browser-start authorization CLI/readback" in payload["next_patch"]
    json.dumps(payload, sort_keys=True)


def test_l3_1_acknowledged_request_is_still_modelled_only():
    mod = _module()
    request = mod.build_browser_start_authorization_request(
        browser="opera",
        ack_all=True,
        allow_browser_start=True,
        allow_profile_directory_creation=True,
        allow_live_driver_session=True,
        requested_side_effects=("start_browser", "create_profile_directory", "create_browser_session"),
    )
    decision = mod.evaluate_browser_start_authorization(request)
    payload = decision.to_payload()
    assert payload["ok"] is True
    assert payload["startup_authorized"] is False
    assert payload["authorization_state"] == "blocked_model_only"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == ()
    assert payload["filesystem_writes_performed"] == ()
    assert "live_side_effects_requested_but_modelled_only" in payload["blocked_reasons"]


def test_l3_1_invalid_browser_rejected_without_side_effects():
    mod = _module()
    request = mod.build_browser_start_authorization_request(browser="firefox", ack_all=True)
    decision = mod.evaluate_browser_start_authorization(request)
    payload = decision.to_payload()
    assert payload["ok"] is False
    assert payload["status"] == "FAIL"
    assert "requested_browser" in payload["invalid_fields"]
    assert payload["startup_authorized"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == ()


def test_l3_1_module_does_not_import_selenium_or_optional_browser_dependencies():
    before = set(sys.modules)
    mod = _module()
    payload = mod.build_l3_browser_start_authorization_contract(".")
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


def test_l3_1_command_plan_is_readback_only():
    mod = _module()
    payload = mod.build_l3_browser_start_authorization_contract(".")
    command_plan = "\n".join(payload["command_plan"]).lower()
    forbidden = (
        "git commit",
        "git push",
        "run-package",
        "llm-browser open",
        "open --browser",
        "run-once",
        "watch-downloads",
        "click_download",
        "paste_to_composer",
        "send_or_submit",
    )
    assert all(fragment not in command_plan for fragment in forbidden)
    assert payload["command_plan_passive"] is True
