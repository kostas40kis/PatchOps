from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_08e_contract_gate_check_aliases_and_heading_variants() -> None:
    payload = gate.build_startup_request_contract_gate()
    assert payload["ok"] is True
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["startup_request_readback_payload"]["ok"] is True
    assert checks["readback_payload_contract"]["ok"] is True
    assert checks["required_public_api_surface"]["ok"] is True
    assert checks["requested_side_effects_modelled_not_executed"]["ok"] is True
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_l1_08e_contract_gate_json_and_text_cli_are_passive() -> None:
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

    text_completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request_contract_gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert text_completed.returncode == 0, text_completed.stderr
    assert "PatchOps LLM browser live adapter startup request contract gate" in text_completed.stdout
    assert "PatchOps LLM browser startup request contract gate" in text_completed.stdout
    assert "Browser    : not started" in text_completed.stdout
