from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import patchops.llm_browser.live_adapter_startup_request as request_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_7p_requested_side_effects_are_derived_from_allow_flags() -> None:
    request = request_model.StartupDecisionRequest(
        requested_browser="opera",
        allow_browser_start=True,
        allow_click_download=True,
        allow_run_patchops_package=True,
        allow_paste_to_composer=True,
        allow_send_or_submit=True,
        acknowledgements=request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS,
    )
    payload = request.to_payload()
    for expected in ("start_browser", "click_download", "run_patchops_package", "paste_to_composer", "send_or_submit"):
        assert expected in payload["requested_side_effects"]
    decision = request_model.evaluate_startup_request(request).to_payload()
    assert decision["startup_allowed"] is False
    assert decision["browser_started"] is False
    assert decision["side_effects_performed"] == []


def test_l1_7p_readback_has_fully_acknowledged_decision() -> None:
    payload = request_model.build_request_model_readback()
    assert payload["fully_acknowledged_decision"]["startup_allowed"] is False
    flags_payload = request_model.build_startup_request_readback(
        request_model.build_fully_acknowledged_startup_request(allow_click_download=True)
    )
    assert flags_payload["patch"] == "L1.7"
    assert flags_payload["requested_decision"]["startup_allowed"] is False
    assert flags_payload["cli_decision"]["startup_allowed"] is False


def test_l1_7p_cli_json_and_text_contracts() -> None:
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
            "--allow-click-download",
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
    assert "click_download" in payload["requested_decision"]["request"]["requested_side_effects"]
    assert "send_or_submit" in payload["requested_decision"]["request"]["requested_side_effects"]

    text_completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-request", "--allow-browser-start", "--ack-all"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert text_completed.returncode == 0, text_completed.stderr
    assert "PatchOps LLM browser live adapter startup request flags" in text_completed.stdout
    assert "Browser    : not started" in text_completed.stdout
