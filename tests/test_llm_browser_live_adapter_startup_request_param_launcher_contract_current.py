from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request as request_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_request_patch_l17_and_callable_missing_acknowledgements() -> None:
    request = request_model.build_startup_request()
    assert request.normalized_browser() == "edge"
    assert request.requested_side_effects() == ()
    assert request.missing_acknowledgements() == request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS

    payload = request_model.build_startup_request_readback(
        request_model.build_fully_acknowledged_startup_request(
            browser="opera",
            allow_browser_start=True,
            requested_operations=("start_browser",),
        )
    )
    assert payload["patch"] == "L1.7"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["cli_decision"]["startup_allowed"] is False
    assert payload["requested_decision"]["startup_allowed"] is False


def test_startup_request_cli_aliases_and_text_are_passive() -> None:
    json_completed = subprocess.run(
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
            "--ack-all",
            "--allow-browser-start",
            "--request-operation",
            "start_browser",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert json_completed.returncode == 0, json_completed.stderr
    payload = json.loads(json_completed.stdout)
    assert payload["patch"] == "L1.7"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["cli_request"]["requested_browser"] == "opera"
    assert payload["cli_decision"]["startup_allowed"] is False

    text_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "startup-request",
            "--allow-browser-start",
            "--ack-all",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert text_completed.returncode == 0, text_completed.stderr
    assert "PatchOps LLM browser live adapter startup request flags" in text_completed.stdout
    assert "Startup    : allowed=False" in text_completed.stdout
    assert "Browser    : not started" in text_completed.stdout
