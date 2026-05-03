from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import l2_10_broad_validation as checkpoint

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_broad_validation_checkpoint_passes_without_side_effects() -> None:
    payload = checkpoint.build_l2_broad_validation_checkpoint(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L2"
    assert payload["patch"] == "L2.10"
    assert payload["next_patch"] == "L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["case_count"] == 6

    required_checks = {
        "l2_documentation_checkpoint_still_passes",
        "l2_aggregate_readiness_gate_still_passes",
        "l1_final_acceptance_marker_still_passes",
        "l2_required_docs_sources_tests_present",
        "l1_accepted_surfaces_still_present",
        "l2_broad_validation_focused_tests_present",
        "l2_broad_validation_command_plan_is_passive",
        "l2_broad_validation_does_not_execute_validation_commands",
        "l2_broad_validation_keeps_no_browser_profile_or_side_effects",
        "l2_source_files_do_not_import_browser_optional_dependencies",
        "no_optional_browser_dependency_imports",
        "l2_broad_validation_checkpoint_did_not_load_browser_optional_modules",
        "l2_broad_validation_payload_json_safe",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_l2_broad_validation_checkpoint_command_plan_is_readback_only() -> None:
    payload = checkpoint.build_l2_broad_validation_checkpoint(PROJECT_ROOT)
    command_text = "\n".join(payload["broad_validation_commands"]).lower()

    assert "profile-preflight-l2-readiness" in command_text
    assert "live_adapter_browser_profile_l2_readiness_gate" in command_text
    assert "live_adapter_browser_profile_l2_documentation_checkpoint" in command_text
    assert "live_adapter_startup_request_l1_final_acceptance_marker" in command_text
    assert "patchops.llm_browser.l2_10_broad_validation" in command_text
    assert "py -m pytest -q" in command_text
    assert "git status --short --branch" in command_text
    assert "git commit" not in command_text
    assert "git push" not in command_text
    assert "run-package" not in command_text
    assert "start_browser" not in command_text
    assert "click_download" not in command_text
    assert "paste_to_composer" not in command_text
    assert "send_or_submit" not in command_text
    assert payload["executed_validation_commands"] == []


def test_l2_broad_validation_checkpoint_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.l2_10_broad_validation",
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
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []


def test_l2_broad_validation_checkpoint_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.l2_10_broad_validation",
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
    assert "PatchOps LLM browser profile preflight L2 broad validation checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Browser    : not started" in stdout
    assert "Profile    : created=False" in stdout
    assert "Commands   : planned=" in stdout
    assert "executed=0" in stdout
    assert "Next patch : L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback" in stdout


def test_l2_broad_validation_checkpoint_module_exposes_aliases() -> None:
    assert checkpoint.build_broad_validation_checkpoint(PROJECT_ROOT)["ok"] is True
    assert checkpoint.build_profile_preflight_l2_broad_validation_checkpoint(PROJECT_ROOT)["ok"] is True


def test_l2_broad_validation_checkpoint_docs_exist_and_lock_boundary() -> None:
    doc_paths = [
        PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_profile_l2_broad_validation_checkpoint.md",
        PROJECT_ROOT / "docs" / "llm_browser_l2_10_broad_validation.md",
    ]
    required = [
        "L2.10",
        "passive broad-validation checkpoint",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "planned command list",
        "not executed by the module",
        "L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback",
    ]
    for doc_path in doc_paths:
        assert doc_path.exists()
        text = doc_path.read_text(encoding="utf-8")
        for fragment in required:
            assert fragment in text
