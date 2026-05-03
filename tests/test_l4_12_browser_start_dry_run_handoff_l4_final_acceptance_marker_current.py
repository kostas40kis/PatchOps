from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_12_final_acceptance_marker_passes_without_side_effects() -> None:
    payload = marker.build_l4_browser_start_dry_run_handoff_final_acceptance_marker(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L4"
    assert payload["patch"] == "L4.12"
    assert payload["next_patch"] == "L5.1 Live adapter browser-start supervised launch handoff contract"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["operator_commit_recommended"] is True

    required_checks = {
        "l4_broad_validation_checkpoint_still_passes",
        "l4_broad_validation_checkpoint_remains_passive",
        "l4_cli_surfaces_remain_present",
        "l4_final_acceptance_artifacts_present",
        "l4_final_acceptance_doc_contains_passive_boundary",
        "l4_final_acceptance_command_plan_is_readback_only",
        "l4_final_acceptance_does_not_execute_planned_commands",
        "l4_final_acceptance_no_new_optional_browser_dependency_imports",
        "l4_final_acceptance_selenium_not_imported",
        "l4_final_acceptance_payload_json_safe",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l4_12_final_acceptance_references_broad_validation_and_cli_readback() -> None:
    payload = marker.build_l4_browser_start_dry_run_handoff_final_acceptance_marker(PROJECT_ROOT)

    assert payload["broad_validation_checkpoint"]["patch"] == "L4.10"
    assert payload["broad_validation_checkpoint"]["ok"] is True
    assert payload["missing_source_paths"] == []
    assert payload["missing_doc_paths"] == []
    assert payload["missing_test_paths"] == []
    assert payload["missing_commands"] == []

    command_text = "\n".join(payload["final_acceptance_commands"])
    assert "live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker" in command_text
    assert "browser-start-dry-run-handoff-l4-broad-validation" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "start_browser" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l4_12_final_acceptance_marker_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker",
            "--repo-root",
            str(PROJECT_ROOT),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L4.12"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["executed_validation_commands"] == []
    assert "selenium" not in payload["loaded_forbidden_modules"]
    assert payload["newly_loaded_forbidden_modules"] == []


def test_l4_12_final_acceptance_marker_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout

    assert "PatchOps LLM browser live adapter browser-start dry-run handoff L4 final acceptance marker" in stdout
    assert "Patch      : L4.12" in stdout
    assert "Status     : PASS" in stdout
    assert "Startup    : authorized=false allowed=false" in stdout
    assert "Browser    : started=False" in stdout
    assert "Session    : created=False" in stdout
    assert "Driver     : created=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "executed=0" in stdout
    assert "Commit     : recommended=true executed=false pushed=false" in stdout
    assert "Next patch : L5.1 Live adapter browser-start supervised launch handoff contract" in stdout


def test_l4_12_final_acceptance_marker_module_exposes_alias() -> None:
    assert marker.build_final_acceptance_marker(PROJECT_ROOT)["ok"] is True


def test_l4_12_final_acceptance_docs_are_present_and_passive() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_l4_final_acceptance_marker.md"
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    required = [
        "L4.12 Live adapter browser-start dry-run handoff L4 final acceptance marker",
        "passive-only",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "git_commit_executed: false",
        "git_push_executed: false",
        "L5.1 Live adapter browser-start supervised launch handoff contract",
    ]
    for phrase in required:
        assert phrase in text
