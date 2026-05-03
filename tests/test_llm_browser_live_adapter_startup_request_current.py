from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request as request_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_request_default_is_passive_and_missing_acknowledgements() -> None:
    request = request_model.build_startup_request()
    assert request.normalized_browser() == "edge"
    assert request.requested_side_effects() == ()
    assert request.missing_acknowledgements() == request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS
    payload = request.to_payload()
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False


def test_startup_decision_remains_blocked_even_when_acknowledged_and_permissive() -> None:
    request = request_model.build_startup_request(
        browser="opera",
        acknowledgements=request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS,
        requested_operations=("start_browser", "click_download", "paste_to_composer"),
        allow_browser_start=True,
        allow_optional_browser_dependencies=True,
        allow_click_download=True,
        allow_paste_to_composer=True,
    )
    decision = request_model.evaluate_startup_request(request)
    payload = decision.to_payload()
    assert payload["ok"] is True
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["missing_acknowledgements"] == []
    assert "requested_side_effects_are_not_enabled_in_l1" in payload["blockers"]
    assert "optional_browser_dependencies_remain_disabled_in_l1_6" in payload["blockers"]


def test_startup_request_payload_round_trips_and_invalid_browser_is_reported() -> None:
    original = request_model.build_startup_request(
        browser="invalid-browser",
        acknowledgements=("operator_confirms_no_auto_send",),
        requested_operations=("send_or_submit",),
        allow_send_or_submit=True,
        operator_note="operator-visible note only",
    )
    reconstructed = request_model.LiveAdapterStartupRequest.from_payload(original.to_payload())
    assert reconstructed.to_payload()["operator_note"] == "operator-visible note only"
    decision = request_model.evaluate_startup_request(reconstructed).to_payload()
    assert decision["startup_allowed"] is False
    assert "requested_browser" in decision["invalid_fields"]
    assert "startup_request_has_invalid_fields" in decision["blockers"]


def test_request_model_readback_contract_is_json_safe() -> None:
    payload = request_model.build_request_model_readback()
    encoded = json.dumps(payload, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded["status"] == "PASSIVE_STARTUP_REQUEST_MODEL"
    assert decoded["startup_allowed"] is False
    assert decoded["browser_started"] is False
    assert decoded["browser_session_created"] is False
    assert decoded["optional_browser_dependencies_required"] is False
    assert decoded["side_effects_performed"] == []
    assert decoded["next_patch"] == "L1.7 Live adapter startup request CLI flags"


def test_request_model_does_not_import_browser_optional_dependencies() -> None:
    forbidden = set(request_model.FORBIDDEN_IMPORT_ROOTS)
    before = set(sys.modules)
    importlib.reload(request_model)
    after = set(sys.modules)
    newly_loaded_roots = {name.split(".", 1)[0] for name in (after - before)}
    assert forbidden.isdisjoint(newly_loaded_roots)


def test_request_model_module_json_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASSIVE_STARTUP_REQUEST_MODEL"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []
