from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_08f_contract_gate_preserves_all_public_check_aliases() -> None:
    payload = gate.build_startup_request_contract_gate()
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    checks = {check["name"]: check for check in payload["checks"]}
    required = {
        "required_public_api_surface",
        "startup_request_readback_payload",
        "readback_payload_contract",
        "requested_side_effects_modelled_not_executed",
        "requested_side_effects_are_modelled_but_blocked",
        "no_optional_browser_dependency_imports",
        "gate_did_not_load_browser_optional_modules",
    }
    assert required.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required)


def test_l1_08f_contract_gate_text_includes_both_heading_variants() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup request contract gate" in completed.stdout
    assert "PatchOps LLM browser startup request contract gate" in completed.stdout
    assert "gate_did_not_load_browser_optional_modules: PASS" in completed.stdout


def test_l1_08f_contract_gate_json_exits_zero_and_is_passive() -> None:
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
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
