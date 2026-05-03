from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser.live_adapter_startup_request import (
    REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS,
    StartupDecisionRequest,
    build_fully_acknowledged_startup_request,
    build_startup_request_readback,
    evaluate_startup_request,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_request_cli_flags_model_side_effect_requests_but_stays_blocked() -> None:
    request = StartupDecisionRequest(
        requested_browser="opera",
        allow_browser_start=True,
        allow_click_download=True,
        allow_run_patchops_package=True,
        allow_paste_to_composer=True,
        allow_send_or_submit=True,
        acknowledgements=REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS,
        operator_note="proof only",
    )
    payload = evaluate_startup_request(request).to_payload()
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []
    assert "requested_side_effects_are_not_enabled_in_l1" in payload["blockers"]
    assert payload["request"]["requested_browser"] == "opera"
    assert "send_or_submit" in payload["request"]["requested_side_effects"]


def test_startup_request_readback_keeps_default_and_requested_decisions_blocked() -> None:
    payload = build_startup_request_readback(
        build_fully_acknowledged_startup_request(
            allow_browser_start=True,
            allow_click_download=True,
            allow_run_patchops_package=True,
        )
    )
    assert payload["status"] == "PASSIVE_STARTUP_REQUEST_MODEL"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["default_decision"]["startup_allowed"] is False
    assert payload["requested_decision"]["startup_allowed"] is False
    assert payload["requested_decision"]["missing_acknowledgements"] == []


def test_startup_request_module_cli_json_flags_are_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request",
            "--json",
            "--compact",
            "--browser",
            "opera",
            "--allow-browser-start",
            "--allow-click-download",
            "--allow-run-patchops-package",
            "--allow-paste-to-composer",
            "--allow-send-or-submit",
            "--ack-all",
            "--operator-note",
            "passive proof",
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
    request = payload["requested_decision"]["request"]
    assert request["requested_browser"] == "opera"
    assert request["missing_acknowledgements"] == []
    assert "click_download" in request["requested_side_effects"]
    assert "send_or_submit" in request["requested_side_effects"]


def test_patchops_cli_startup_request_json_flags_are_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "startup-request",
            "--json",
            "--compact",
            "--browser",
            "opera",
            "--allow-browser-start",
            "--allow-click-download",
            "--allow-run-patchops-package",
            "--allow-paste-to-composer",
            "--allow-send-or-submit",
            "--ack-all",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L1.7"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["requested_decision"]["request"]["requested_browser"] == "opera"
    assert payload["requested_decision"]["request"]["missing_acknowledgements"] == []


def test_startup_request_text_cli_does_not_start_browser() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-request", "--allow-browser-start", "--ack-all"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup request flags" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
