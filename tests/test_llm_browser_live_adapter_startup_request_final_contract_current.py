import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request as request_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_07l_request_object_keeps_legacy_callable_side_effects() -> None:
    request = request_model.build_startup_request()
    assert request.normalized_browser() == "edge"
    assert request.requested_side_effects() == ()
    assert request.missing_acknowledgements == request_model.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS


def test_l1_07l_cli_json_contains_cli_decision_and_browser_stays_blocked() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request",
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
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["startup_allowed"] is False
    assert payload["cli_request"]["requested_browser"] == "opera"
    assert payload["cli_decision"]["startup_allowed"] is False
    assert payload["requested_decision"]["browser_started"] is False


def test_l1_07l_patchops_cli_text_mentions_browser_not_started() -> None:
    completed = subprocess.run(
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
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup request flags" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
