from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_l1_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_final_acceptance_marker_passes_without_side_effects() -> None:
    payload = marker.build_l1_final_acceptance_marker(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.17"
    assert payload["next_patch"] == "L2.1 Live adapter browser profile preflight contract"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["case_count"] == 6

    required_checks = {
        "l1_broad_validation_checkpoint_still_passes",
        "l1_documentation_freeze_checkpoint_still_passes",
        "l1_aggregate_readiness_gate_still_passes",
        "l1_final_acceptance_required_l1_artifacts_present",
        "l1_final_acceptance_no_browser_or_side_effects",
        "l1_final_acceptance_does_not_execute_validation_commands",
        "l1_final_acceptance_payload_json_safe",
        "l1_final_acceptance_ready_for_operator_commit",
        "no_optional_browser_dependency_imports",
        "l1_final_acceptance_marker_did_not_load_browser_optional_modules",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l1_final_acceptance_marker_references_l1_stack() -> None:
    payload = marker.build_l1_final_acceptance_marker(PROJECT_ROOT)

    assert payload["broad_validation_checkpoint"]["patch"] == "L1.16"
    assert payload["documentation_checkpoint"]["patch"] == "L1.15"
    assert payload["aggregate_readiness_gate"]["patch"] == "L1.13"
    assert payload["missing_doc_paths"] == []
    assert payload["missing_source_paths"] == []
    assert payload["missing_test_paths"] == []

    command_text = "\n".join(payload["broad_validation_commands"])
    assert "py -m pytest -q" in command_text
    assert "run-package" not in command_text
    assert "start_browser" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l1_final_acceptance_marker_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_final_acceptance_marker",
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
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["executed_validation_commands"] == []
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False


def test_l1_final_acceptance_marker_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_final_acceptance_marker",
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

    assert "PatchOps LLM browser startup request L1 final acceptance marker" in stdout
    assert "PatchOps LLM browser live adapter startup request L1 final acceptance marker" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : not started" in stdout
    assert "SideEffects: []" in stdout
    assert "Commit     : recommended=true executed=false pushed=false" in stdout
    assert "Next patch : L2.1 Live adapter browser profile preflight contract" in stdout


def test_l1_final_acceptance_marker_module_exposes_alias() -> None:
    assert marker.build_final_acceptance_marker(PROJECT_ROOT)["ok"] is True
