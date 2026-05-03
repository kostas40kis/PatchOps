from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate


def test_l1_08k_contract_gate_stable_pass_all_public_aliases() -> None:
    payload = gate.build_startup_request_contract_gate()
    checks = {check["name"]: check for check in payload["checks"]}
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    for name in [
        "required_public_api_surface",
        "startup_request_readback_payload",
        "readback_payload_contract",
        "requested_side_effects_modelled_not_executed",
        "requested_side_effects_are_modelled_but_blocked",
        "legacy_callable_compatibility_methods",
        "cli_alias_argument_model",
        "no_optional_browser_dependency_imports",
        "gate_did_not_load_browser_optional_modules",
    ]:
        assert checks[name]["ok"] is True
