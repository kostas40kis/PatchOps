from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_request_contract_gate_passes_without_side_effects() -> None:
    payload = gate.build_startup_request_contract_gate()

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.8"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["required_public_api_surface"]["ok"] is True
    assert checks["readback_payload_contract"]["ok"] is True
    assert checks["requested_side_effects_are_modelled_but_blocked"]["ok"] is True
    assert checks["legacy_callable_compatibility_methods"]["ok"] is True
    assert checks["cli_alias_argument_model"]["ok"] is True
    assert checks["no_optional_browser_dependency_imports"]["ok"] is True


def test_startup_request_contract_gate_module_json_cli_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_contract_gate",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_startup_request_contract_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup request contract gate" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout
