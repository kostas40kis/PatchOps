from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops import cli
from patchops.llm_browser import commands

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "profile-preflight-l2-broad-validation"


def _parser_choices() -> set[str]:
    parser = commands.build_parser()
    for action in getattr(parser, "_actions", []):
        if action.__class__.__name__ == "_SubParsersAction":
            return set(getattr(action, "choices", {}).keys())
    return set()


def test_profile_preflight_l2_broad_validation_command_is_registered_in_llm_browser_parser() -> None:
    choices = _parser_choices()
    assert "profile-preflight-l2-readiness" in choices
    assert COMMAND in choices
    assert COMMAND in commands.llm_browser_command_names()


def test_profile_preflight_l2_broad_validation_patchops_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
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
    assert payload["patch"] == "L2.10"
    assert payload["phase"] == "L2"
    assert payload["next_patch"] == "L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["missing_l2_doc_paths"] == []
    assert payload["missing_l2_source_paths"] == []
    assert payload["missing_l2_test_paths"] == []

    checks = {check["name"]: check for check in payload["checks"]}
    required_checks = {
        "l2_documentation_checkpoint_still_passes",
        "l2_aggregate_readiness_gate_still_passes",
        "l1_final_acceptance_marker_still_passes",
        "l2_required_docs_sources_tests_present",
        "l1_accepted_surfaces_still_present",
        "l2_broad_validation_command_plan_is_passive",
        "l2_broad_validation_does_not_execute_validation_commands",
        "l2_broad_validation_keeps_no_browser_profile_or_side_effects",
        "l2_source_files_do_not_import_browser_optional_dependencies",
        "no_optional_browser_dependency_imports",
        "l2_broad_validation_checkpoint_did_not_load_browser_optional_modules",
    }
    assert required_checks.issubset(checks)
    assert all(checks[name]["ok"] is True for name in required_checks)


def test_profile_preflight_l2_broad_validation_patchops_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
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

    assert "PatchOps LLM browser profile preflight L2 broad validation checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Patch      : L2.10" in stdout
    assert "Startup    : allowed=False" in stdout
    assert "Browser    : not started" in stdout
    assert "Profile    : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Commands   : planned=" in stdout
    assert "executed=0" in stdout
    assert "Next patch : L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback" in stdout


def test_profile_preflight_l2_broad_validation_cli_main_routes_without_side_effects() -> None:
    result = cli.main([
        "llm-browser",
        COMMAND,
        "--repo-root",
        str(PROJECT_ROOT),
        "--json",
        "--compact",
    ])
    assert result == 0


def test_profile_preflight_l2_broad_validation_help_mentions_command_without_starting_browser() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0
    assert "profile-preflight-l2-readiness" in completed.stdout
    assert COMMAND in completed.stdout


def test_profile_preflight_l2_broad_validation_cli_does_not_create_profiles_or_write_files(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
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
    assert payload["filesystem_writes_performed"] == []
    assert payload["profile_directory_created"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["executed_validation_commands"] == []
    assert not profile_root.exists()


def test_profile_preflight_l2_broad_validation_module_json_matches_patchops_cli_json() -> None:
    module_completed = subprocess.run(
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
        timeout=120,
    )
    cli_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
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
    assert module_completed.returncode == 0, module_completed.stderr
    assert cli_completed.returncode == 0, cli_completed.stderr
    module_payload = json.loads(module_completed.stdout)
    cli_payload = json.loads(cli_completed.stdout)
    assert cli_payload["name"] == module_payload["name"]
    assert cli_payload["patch"] == module_payload["patch"]
    assert cli_payload["status"] == module_payload["status"]
    assert cli_payload["broad_validation_commands"] == module_payload["broad_validation_commands"]
    assert cli_payload["side_effects_performed"] == module_payload["side_effects_performed"]


def test_l2_11_cli_readback_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_profile_l2_broad_validation_cli_readback.md"
    compat = PROJECT_ROOT / "docs" / "llm_browser_l2_11_broad_validation_cli_readback.md"
    runner = PROJECT_ROOT / "docs" / "llm_browser_runner.md"

    assert canonical.exists()
    assert compat.exists()
    canonical_text = canonical.read_text(encoding="utf-8")
    compat_text = compat.read_text(encoding="utf-8")
    runner_text = runner.read_text(encoding="utf-8")

    required = [
        "profile-preflight-l2-broad-validation",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L2.12 Live adapter browser profile preflight L2 final acceptance marker",
    ]
    for phrase in required:
        assert phrase in canonical_text
        assert phrase in compat_text

    assert "PATCHOPS_L2_11_BROAD_VALIDATION_CLI_READBACK_START" in runner_text
    assert "profile-preflight-l2-broad-validation" in runner_text
