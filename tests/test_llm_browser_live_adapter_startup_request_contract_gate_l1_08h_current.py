from __future__ import annotations

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate


def test_l1_08h_contract_gate_exposes_legacy_callable_check_alias() -> None:
    payload = gate.build_startup_request_contract_gate()
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert checks["legacy_callable_compatibility_methods"]["ok"] is True
