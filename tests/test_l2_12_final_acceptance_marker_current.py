from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_l2_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_final_acceptance_marker_passes_without_side_effects() -> None:
    payload = marker.build_l2_final_acceptance_marker(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L2"
    assert payload["patch"] == "L2.12"
    assert payload["repair_patch"] == "L2.12d"
    assert payload["next_patch"] == "L3.1 Live adapter explicit browser-start authorization contract"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["operator_commit_recommended"] is True

    required_checks = {
        "l2_broad_validation_checkpoint_still_passes",
        "l2_broad_validation_cli_readback_surface_present",
        "l2_final_acceptance_artifacts_present",
        "l2_final_acceptance_doc_contains_passive_boundary",
        "l2_runner_doc_mentions_final_acceptance_marker",
        "l2_final_acceptance_no_browser_profile_or_side_effects",
        "l2_final_acceptance_command_plan_is_passive",
        "l2_final_acceptance_does_not_execute_validation_commands",
        "l2_final_acceptance_ready_for_operator_commit",
        "no_new_optional_browser_dependency_imports",
        "selenium_not_imported_by_final_acceptance_marker",
        "l2_final_acceptance_payload_json_safe",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l2_final_acceptance_marker_references_l2_broad_validation_and_cli_readback() -> None:
    payload = marker.build_l2_final_acceptance_marker(PROJECT_ROOT)

    assert payload["broad_validation_checkpoint"]["patch"] == "L2.10"
    assert payload["broad_validation_checkpoint"]["ok"] is True
    assert payload["missing_final_doc_paths"] == []
    assert payload["missing_final_source_paths"] == []
    assert payload["missing_final_test_paths"] == []

    command_text = "\n".join(payload["final_acceptance_commands"])
    assert "live_adapter_browser_profile_l2_final_acceptance_marker" in command_text
    assert "profile-preflight-l2-broad-validation" in command_text
    assert "git status --short --branch" in command_text
    assert "run-package" not in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "start_browser" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text


def test_l2_final_acceptance_marker_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_final_acceptance_marker",
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
    assert payload["patch"] == "L2.12"
    assert payload["repair_patch"] == "L2.12d"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["executed_validation_commands"] == []
    assert "selenium" not in payload["loaded_forbidden_modules"]
    assert payload["newly_loaded_forbidden_modules"] == []


def test_l2_final_acceptance_marker_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_final_acceptance_marker",
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

    assert "PatchOps LLM browser profile preflight L2 final acceptance marker" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight L2 final acceptance marker" in stdout
    assert "Patch      : L2.12" in stdout
    assert "Repair     : L2.12d" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : not started" in stdout
    assert "Profile    : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Commands   : planned=" in stdout
    assert "executed=0" in stdout
    assert "Commit     : recommended=true executed=false pushed=false" in stdout
    assert "Next patch : L3.1 Live adapter explicit browser-start authorization contract" in stdout


def test_l2_final_acceptance_marker_module_exposes_aliases() -> None:
    assert marker.build_final_acceptance_marker(PROJECT_ROOT)["ok"] is True
    assert marker.build_profile_preflight_l2_final_acceptance_marker(PROJECT_ROOT)["ok"] is True


def test_l2_final_acceptance_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker.md"
    compat = PROJECT_ROOT / "docs" / "llm_browser_l2_12_final_acceptance_marker.md"
    runner = PROJECT_ROOT / "docs" / "llm_browser_runner.md"

    assert canonical.exists()
    assert compat.exists()
    assert runner.exists()

    required = [
        "L2.12",
        "final acceptance marker",
        "passive-only",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "git_commit_executed: false",
        "git_push_executed: false",
        "L3.1 Live adapter explicit browser-start authorization contract",
    ]
    for path in (canonical, compat):
        text = path.read_text(encoding="utf-8")
        for phrase in required:
            assert phrase in text

    runner_text = runner.read_text(encoding="utf-8")
    assert "PATCHOPS_L2_12_FINAL_ACCEPTANCE_MARKER_START" in runner_text
    assert "PATCHOPS_L2_12D_FINAL_ACCEPTANCE_VALIDATION_REPAIR_START" in runner_text
    assert "live_adapter_browser_profile_l2_final_acceptance_marker" in runner_text
    assert "L3.1 Live adapter explicit browser-start authorization contract" in runner_text
