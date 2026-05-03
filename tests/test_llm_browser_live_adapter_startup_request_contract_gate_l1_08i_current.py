from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_contract_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_08i_contract_gate_exposes_cli_alias_argument_model() -> None:
    payload = gate.build_startup_request_contract_gate()
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert checks["cli_alias_argument_model"]["ok"] is True
    assert checks["legacy_callable_compatibility_methods"]["ok"] is True
    assert checks["gate_did_not_load_browser_optional_modules"]["ok"] is True


def test_l1_08i_contract_gate_json_and_text_still_exit_zero() -> None:
    json_completed = subprocess.run(
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
    assert json_completed.returncode == 0, json_completed.stderr
    payload = json.loads(json_completed.stdout)
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["cli_alias_argument_model"]["ok"] is True
    assert payload["ok"] is True

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
    assert "- cli_alias_argument_model: PASS" in text_completed.stdout
