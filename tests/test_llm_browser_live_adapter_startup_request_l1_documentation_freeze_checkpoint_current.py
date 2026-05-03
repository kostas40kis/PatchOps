from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_request_l1_documentation_checkpoint as checkpoint

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l1_documentation_freeze_checkpoint_passes_without_side_effects() -> None:
    payload = checkpoint.build_l1_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)
    checks = {check["name"]: check for check in payload["checks"]}

    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L1.15"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["aggregate_readiness_gate"]["ok"] is True
    assert payload["missing_doc_paths"] == []
    assert payload["missing_source_paths"] == []
    assert payload["missing_test_paths"] == []

    for name in [
        "l1_aggregate_readiness_gate_still_passes",
        "l1_documentation_paths_present",
        "l1_source_paths_present",
        "l1_focused_test_paths_present",
        "l1_freeze_doc_contains_passive_boundary",
        "l1_runner_doc_mentions_freeze_checkpoint",
        "l1_documentation_freeze_keeps_no_browser_or_side_effects",
        "no_optional_browser_dependency_imports",
        "l1_documentation_checkpoint_did_not_load_browser_optional_modules",
    ]:
        assert checks[name]["ok"] is True


def test_l1_documentation_freeze_checkpoint_json_cli_is_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint",
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
    assert payload["patch"] == "L1.15"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["aggregate_readiness_gate"]["ok"] is True


def test_l1_documentation_freeze_checkpoint_text_cli_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint",
            "--repo-root",
            str(PROJECT_ROOT),
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser startup request L1 documentation freeze/readiness checkpoint" in completed.stdout
    assert "PatchOps LLM browser live adapter startup request L1 documentation freeze/readiness checkpoint" in completed.stdout
    assert "Status     : PASS" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout
    assert "Docs       : required=" in completed.stdout
    assert "missing=0" in completed.stdout
    assert "Next patch : L1.16 Live adapter startup request L1 broad validation checkpoint" in completed.stdout


def test_l1_documentation_freeze_checkpoint_module_exposes_alias() -> None:
    assert checkpoint.build_documentation_freeze_readiness_checkpoint(PROJECT_ROOT)["ok"] is True
