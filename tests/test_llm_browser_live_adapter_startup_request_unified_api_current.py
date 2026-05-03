from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request as request_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_7k_public_aliases_and_payload_keys_are_stable() -> None:
    request = request_model.build_fully_acknowledged_startup_request(
        browser="opera",
        allow_browser_start=True,
        requested_operations=("start_browser",),
    )
    assert isinstance(request, request_model.StartupDecisionRequest)
    assert isinstance(request, request_model.LiveAdapterStartupRequest)
    assert request.missing_acknowledgements == ()
    assert request.normalized_browser() == "opera"

    payload = request_model.build_startup_request_readback(request)
    assert payload["startup_allowed"] is False
    assert payload["requested_decision"]["startup_allowed"] is False
    assert payload["cli_request"]["requested_browser"] == "opera"
    assert payload["side_effects_performed"] == []

    legacy = request_model.build_request_model_readback()
    assert legacy["next_patch"] == "L1.7 Live adapter startup request CLI flags"


def test_l1_7k_module_cli_aliases_remain_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_request", "--json", "--compact", "--browser", "opera", "--ack-all", "--allow-browser-start", "--request-operation", "start_browser"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["startup_allowed"] is False
    assert payload["cli_request"]["requested_browser"] == "opera"
    assert payload["requested_decision"]["startup_allowed"] is False


def test_l1_7k_patchops_cli_aliases_remain_passive() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-request", "--json", "--compact", "--ack-all", "--allow-browser-start", "--request-operation", "start_browser"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_l1_7k_patchops_cli_text_heading_is_flags() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-request", "--allow-browser-start", "--ack-all"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup request flags" in completed.stdout
    assert "not started" in completed.stdout
