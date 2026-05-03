from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request as request_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_6_public_api_names_remain_available_after_l1_7_cli_flags() -> None:
    assert callable(request_model.build_startup_request)
    assert callable(request_model.build_request_model_readback)
    assert callable(request_model.build_default_request)


def test_l1_6_startup_request_builder_still_accepts_original_kwargs() -> None:
    request = request_model.build_startup_request(
        browser="opera",
        acknowledgements=request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS,
        requested_operations=("start_browser", "click_download", "paste_to_composer"),
        allow_browser_start=True,
        allow_optional_browser_dependencies=True,
        allow_click_download=True,
        allow_paste_to_composer=True,
        operator_note="compatibility check",
    )
    payload = request.to_payload()
    assert payload["requested_browser"] == "opera"
    assert payload["missing_acknowledgements"] == []
    assert "start_browser" in payload["requested_side_effects"]
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []

    decision = request_model.decide_startup_request(request).to_payload()
    assert decision["startup_allowed"] is False
    assert decision["browser_started"] is False
    assert decision["side_effects_performed"] == []


def test_l1_6_readback_name_is_json_safe_after_l1_7_cli_flags() -> None:
    payload = request_model.build_request_model_readback()
    json.dumps(payload, sort_keys=True)
    assert payload["status"] == "PASSIVE_STARTUP_REQUEST_MODEL"
    assert payload["startup_allowed"] is False
    assert payload["default_decision"]["startup_allowed"] is False
    assert payload["fully_acknowledged_decision"]["startup_allowed"] is False


def test_startup_request_module_cli_flags_remain_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request",
            "--json",
            "--compact",
            "--browser",
            "opera",
            "--acknowledge-all",
            "--allow-browser-start",
            "--allow-optional-browser-dependencies",
            "--request-operation",
            "start_browser",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["startup_allowed"] is False
    assert payload["cli_request"]["requested_browser"] == "opera"
    assert payload["cli_decision"]["startup_allowed"] is False
    assert payload["cli_decision"]["browser_started"] is False
    assert payload["side_effects_performed"] == []
