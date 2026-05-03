from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_08a_contract_gate_treats_blocked_startup_as_passive_success() -> None:
    payload = gate.build_startup_request_contract_gate()

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.8"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["startup_request_readback_payload"]["ok"] is True
    assert checks["requested_side_effects_modelled_not_executed"]["ok"] is True
    assert checks["no_optional_browser_dependency_imports"]["ok"] is True
    assert checks["gate_did_not_load_browser_optional_modules"]["ok"] is True


def test_l1_08a_contract_gate_json_cli_exits_zero() -> None:
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
    assert payload["startup_allowed"] is False


def test_l1_08a_contract_gate_text_cli_exits_zero_and_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser startup request contract gate" in completed.stdout
    assert "Status     : PASS" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
