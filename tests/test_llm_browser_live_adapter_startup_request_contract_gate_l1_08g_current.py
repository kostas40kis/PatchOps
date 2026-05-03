from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_08g_contract_gate_is_stable_pass_and_preserves_aliases() -> None:
    payload = gate.build_startup_request_contract_gate()
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    checks = {check["name"]: check for check in payload["checks"]}
    for name in (
        "required_public_api_surface",
        "readback_payload_contract",
        "startup_request_readback_payload",
        "requested_side_effects_are_modelled_but_blocked",
        "requested_side_effects_modelled_not_executed",
        "no_optional_browser_dependency_imports",
        "gate_did_not_load_browser_optional_modules",
    ):
        assert checks[name]["ok"] is True


def test_l1_08g_contract_gate_json_and_text_cli_exit_zero() -> None:
    json_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert json_completed.returncode == 0, json_completed.stderr
    payload = json.loads(json_completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"

    text_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert text_completed.returncode == 0, text_completed.stderr
    assert "PatchOps LLM browser startup request contract gate" in text_completed.stdout
    assert "PatchOps LLM browser live adapter startup request contract gate" in text_completed.stdout
    assert "Browser    : not started" in text_completed.stdout
