from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_l1_broad_validation_checkpoint as checkpoint

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_broad_validation_checkpoint_passes_without_side_effects() -> None:
    payload = checkpoint.build_l1_broad_validation_checkpoint(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.16"
    assert payload["next_patch"] == "L1.17 Live adapter startup request L1 final acceptance marker"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["case_count"] == 6

    required_checks = {
        "l1_documentation_freeze_checkpoint_still_passes",
        "l1_aggregate_readiness_gate_still_passes",
        "l1_broad_validation_focused_tests_present",
        "l1_broad_validation_command_plan_is_passive",
        "l1_broad_validation_keeps_no_browser_or_side_effects",
        "l1_broad_validation_payload_json_safe",
        "no_optional_browser_dependency_imports",
        "l1_broad_validation_checkpoint_did_not_load_browser_optional_modules",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l1_broad_validation_checkpoint_command_plan_is_readback_only() -> None:
    payload = checkpoint.build_l1_broad_validation_checkpoint(PROJECT_ROOT)
    command_text = "\n".join(payload["broad_validation_commands"]).lower()

    assert "startup-request-l1-readiness" in command_text
    assert "live_adapter_startup_request_l1_documentation_checkpoint" in command_text
    assert "release-gate" in command_text
    assert "checkpoint" in command_text
    assert "py -m pytest -q" in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "run-package" not in command_text
    assert "start_browser" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l1_broad_validation_checkpoint_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_broad_validation_checkpoint",
            "--repo-root",
            str(PROJECT_ROOT),
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
    assert payload["executed_validation_commands"] == []
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []


def test_l1_broad_validation_checkpoint_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_broad_validation_checkpoint",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps LLM browser startup request L1 broad validation checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : not started" in stdout
    assert "Commands   : planned=" in stdout
    assert "executed=0" in stdout
    assert "Next patch : L1.17 Live adapter startup request L1 final acceptance marker" in stdout


def test_l1_broad_validation_checkpoint_module_exposes_alias() -> None:
    assert checkpoint.build_broad_validation_checkpoint(PROJECT_ROOT)["ok"] is True
