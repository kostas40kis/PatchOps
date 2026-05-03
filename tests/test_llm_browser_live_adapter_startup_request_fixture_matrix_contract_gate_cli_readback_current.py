from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops import cli
from patchops.llm_browser import commands

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _parser_choices() -> set[str]:
    parser = commands.build_parser()
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    return set()


def test_startup_request_fixture_gate_command_is_registered() -> None:
    choices = _parser_choices()
    assert "startup-request-fixture-gate" in choices


def test_startup_request_fixture_gate_patchops_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "startup-request-fixture-gate",
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
    assert payload["patch"] == "L1.11"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["case_count"] >= 6
    assert payload["matrix"]["ok"] is True
    assert payload["upstream_contract_gate"]["ok"] is True
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["fixture_matrix_payload_contract"]["ok"] is True
    assert checks["fixture_matrix_has_core_cases"]["ok"] is True
    assert checks["fixture_gate_did_not_load_browser_optional_modules"]["ok"] is True


def test_startup_request_fixture_gate_patchops_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-request-fixture-gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser startup request fixture matrix contract gate" in completed.stdout
    assert "PatchOps LLM browser live adapter startup request fixture matrix contract gate" in completed.stdout
    assert "Status     : PASS" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout
    assert "Next patch : L1.12 Live adapter startup request fixture matrix contract gate CLI/readback" in completed.stdout


def test_startup_request_fixture_gate_cli_main_routes_without_side_effects() -> None:
    result = cli.main(["llm-browser", "startup-request-fixture-gate", "--json", "--compact"])
    assert result == 0


def test_startup_request_fixture_gate_help_mentions_command_without_starting_browser() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0
    assert "startup-request-fixture-gate" in completed.stdout
