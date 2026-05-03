from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_contract_gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_BLOCKED = {
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
}


def test_live_adapter_passive_contract_gate_passes_without_side_effects() -> None:
    payload = live_adapter_contract_gate.evaluate_live_adapter_passive_contract()

    assert payload["name"] == "llm_browser_live_adapter_passive_contract_gate"
    assert payload["patch"] == "L1.3"
    assert payload["status"] == "PASS"
    assert payload["ok"] is True
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []
    assert set(payload["required_blocked_operations"]) == EXPECTED_BLOCKED
    assert payload["next_patch"] == "L1.4 Live adapter explicit startup gate scaffold"

    checks = {check["name"]: check for check in payload["checks"]}
    required_checks = {
        "live_adapter_readback_payload",
        "blocked_capability_consistency",
        "no_optional_browser_dependency_imports",
        "module_level_operations_blocked",
        "skeleton_methods_blocked",
        "gate_did_not_load_browser_optional_modules",
    }
    assert required_checks <= set(checks)
    assert all(check["status"] == "PASS" for check in checks.values())


def test_live_adapter_passive_contract_gate_json_is_parseable() -> None:
    payload = json.loads(live_adapter_contract_gate.contract_gate_json(indent=None))
    assert payload["ok"] is True
    assert payload["patch"] == "L1.3"
    assert set(payload["required_blocked_operations"]) == EXPECTED_BLOCKED


def test_live_adapter_passive_contract_gate_subprocess_json() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_contract_gate", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == "PASS"
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []
