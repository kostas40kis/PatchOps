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


def test_profile_preflight_command_is_registered() -> None:
    choices = _parser_choices()
    assert "profile-preflight" in choices


def test_profile_preflight_patchops_cli_json_readback_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "profile-preflight",
            "--repo-root",
            str(PROJECT_ROOT),
            "--browser",
            "opera",
            "--ack-all",
            "--allow-browser-start",
            "--allow-profile-directory-creation",
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
    assert payload["patch"] == "L2.1"
    assert payload["phase"] == "L2"
    assert payload["request_status"] == "BLOCKED_PREFLIGHT_CONTRACT_ONLY"
    assert payload["normalized_browser"] == "opera"
    assert payload["missing_acknowledgements"] == []
    assert payload["requested_side_effects"] == ["start_browser", "create_profile_directory"]
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["filesystem_writes_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["l1_final_acceptance_marker"]["ok"] is True

    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["l1_final_acceptance_marker_still_passes"]["ok"] is True
    assert checks["l2_profile_preflight_models_requested_side_effects_but_executes_none"]["ok"] is True
    assert checks["l2_profile_preflight_does_not_create_profile_or_browser"]["ok"] is True
    assert checks["l2_profile_preflight_did_not_load_browser_optional_modules"]["ok"] is True


def test_profile_preflight_patchops_cli_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "profile-preflight", "--repo-root", str(PROJECT_ROOT)],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout

    assert "PatchOps LLM browser profile preflight contract" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight contract" in stdout
    assert "Status     : PASS" in stdout
    assert "Request    : BLOCKED_PREFLIGHT_CONTRACT_ONLY" in stdout
    assert "Browser    : edge" in stdout
    assert "Profile    : mode=dedicated created=false" in stdout
    assert "Startup    : allowed=false" in stdout
    assert "BrowserRun : not started" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "Next patch : L2.2 Live adapter browser profile preflight CLI/readback" in stdout


def test_profile_preflight_cli_main_routes_without_side_effects() -> None:
    result = cli.main([
        "llm-browser",
        "profile-preflight",
        "--repo-root",
        str(PROJECT_ROOT),
        "--browser",
        "opera",
        "--ack-all",
        "--allow-browser-start",
        "--allow-profile-directory-creation",
        "--json",
        "--compact",
    ])
    assert result == 0


def test_profile_preflight_help_mentions_command_without_starting_browser() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0
    assert "profile-preflight" in completed.stdout


def test_profile_preflight_cli_does_not_create_profile_directory(tmp_path: Path) -> None:
    profile_root = tmp_path / "profiles"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            "profile-preflight",
            "--repo-root",
            str(PROJECT_ROOT),
            "--profile-root",
            str(profile_root),
            "--ack-all",
            "--allow-profile-directory-creation",
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
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert not profile_root.exists()
