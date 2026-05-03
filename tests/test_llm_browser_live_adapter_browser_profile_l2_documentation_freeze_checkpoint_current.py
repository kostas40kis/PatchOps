from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_browser_profile_l2_documentation_checkpoint as checkpoint

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l2_documentation_freeze_checkpoint_passes_without_side_effects() -> None:
    payload = checkpoint.build_l2_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L2.9"
    assert payload["phase"] == "L2"
    assert payload["next_patch"] == "L2.10 Live adapter browser profile preflight L2 broad validation checkpoint"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["aggregate_readiness_gate"]["ok"] is True
    assert payload["aggregate_readiness_gate"]["patch"] == "L2.7"
    assert payload["missing_doc_paths"] == []
    assert payload["missing_source_paths"] == []
    assert payload["missing_test_paths"] == []
    assert payload["case_count"] == 6

    for name in [
        "l2_profile_l2_aggregate_readiness_gate_still_passes",
        "l2_documentation_paths_present",
        "l2_source_paths_present",
        "l2_focused_test_paths_present",
        "l2_freeze_doc_contains_passive_boundary",
        "l2_runner_doc_mentions_freeze_checkpoint",
        "l2_documentation_freeze_keeps_no_browser_profile_or_side_effects",
        "l2_documentation_checkpoint_payload_json_safe",
        "no_optional_browser_dependency_imports",
        "l2_documentation_checkpoint_did_not_load_browser_optional_modules",
    ]:
        assert checks[name]["ok"] is True


def test_l2_documentation_freeze_checkpoint_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_documentation_checkpoint",
            "--repo-root",
            str(PROJECT_ROOT),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L2.9"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["aggregate_readiness_gate"]["ok"] is True


def test_l2_documentation_freeze_checkpoint_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_profile_l2_documentation_checkpoint",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "PatchOps LLM browser profile preflight L2 documentation freeze/readiness checkpoint" in stdout
    assert "PatchOps LLM browser live adapter browser profile preflight L2 documentation freeze/readiness checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Patch      : L2.9" in stdout
    assert "Startup    : allowed=False" in stdout
    assert "Browser    : not started" in stdout
    assert "Profile    : created=False" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "SideEffects: []" in stdout
    assert "Docs       : required=" in stdout
    assert "missing=0" in stdout
    assert "Cases      : 6" in stdout
    assert "l2_documentation_freeze_keeps_no_browser_profile_or_side_effects: PASS" in stdout
    assert "Next patch : L2.10 Live adapter browser profile preflight L2 broad validation checkpoint" in stdout


def test_l2_documentation_freeze_checkpoint_aliases_are_available() -> None:
    assert checkpoint.build_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)["ok"] is True
    assert checkpoint.build_profile_preflight_l2_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)["ok"] is True


def test_l2_documentation_freeze_checkpoint_imports_no_browser_optional_modules() -> None:
    before = set(sys.modules)
    payload = checkpoint.build_l2_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    assert payload["ok"] is True
    assert not any(name.split(".", 1)[0] in forbidden_roots for name in newly_loaded)
    assert "selenium" not in sys.modules
