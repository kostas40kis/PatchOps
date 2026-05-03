from __future__ import annotations

import json

from patchops.llm_browser import live_adapter_startup_request as request_model
from patchops.llm_browser.live_adapter_startup_request import (
    StartupDecisionRequest,
    build_default_request,
    build_fully_acknowledged_startup_request,
    build_request_model_readback,
    build_startup_request,
)


def test_startup_request_public_api_surface_is_backward_compatible() -> None:
    default_request = build_default_request()
    legacy_request = build_startup_request()
    permissive_request = build_fully_acknowledged_startup_request()

    assert isinstance(default_request, StartupDecisionRequest)
    assert isinstance(legacy_request, StartupDecisionRequest)
    assert isinstance(permissive_request, StartupDecisionRequest)
    assert default_request.requested_browser == "edge"
    assert legacy_request.requested_browser == "edge"
    assert permissive_request.missing_acknowledgements == ()


def test_startup_request_readback_stays_json_safe_and_blocked() -> None:
    payload = build_request_model_readback()
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert decoded["status"] == "PASSIVE_STARTUP_REQUEST_MODEL"
    assert decoded["startup_allowed"] is False
    assert decoded["browser_started"] is False
    assert decoded["browser_session_created"] is False
    assert decoded["optional_browser_dependencies_required"] is False
    assert decoded["side_effects_performed"] == []


def test_fully_acknowledged_request_still_evaluates_blocked() -> None:
    request = build_fully_acknowledged_startup_request(
        requested_operations=("start_browser", "click_download", "paste_to_composer"),
        allow_click_download=True,
        allow_paste_to_composer=True,
    )
    decision = request_model.evaluate_startup_request(request).to_payload()

    assert decision["startup_allowed"] is False
    assert decision["browser_started"] is False
    assert decision["side_effects_performed"] == []
    assert "requested_side_effects_are_not_enabled_in_l1" in decision["blockers"]
