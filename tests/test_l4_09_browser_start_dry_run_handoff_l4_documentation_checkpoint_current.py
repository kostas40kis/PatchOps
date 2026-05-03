from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l4_09_documentation_checkpoint_payload_is_passive_and_green() -> None:
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint import (
        build_l4_browser_start_dry_run_handoff_documentation_checkpoint,
    )

    payload = build_l4_browser_start_dry_run_handoff_documentation_checkpoint(PROJECT_ROOT)
    assert payload["patch"] == "L4.9"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L4.10 Live adapter browser-start dry-run handoff L4 broad validation checkpoint"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["missing_commands"] == []
    assert payload["missing_repo_paths"] == []
    assert payload["missing_safety_phrases"] == []
    assert payload["missing_progression_phrases"] == []
    assert all(check["ok"] is True for check in payload["checks"])


def test_l4_09_documentation_checkpoint_json_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint",
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
    assert payload["patch"] == "L4.9"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["readiness_gate"]["ok"] is True
    assert payload["readiness_gate"]["browser_started"] is False
    assert payload["readiness_gate"]["profile_directory_created"] is False


def test_l4_09_documentation_checkpoint_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint",
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
    assert "L4.9 Browser Start Dry-Run Handoff Documentation Freeze Readiness Checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Startup    : authorized=False allowed=False" in stdout
    assert "Browser    : started=False" in stdout
    assert "Session    : created=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "Next patch : L4.10 Live adapter browser-start dry-run handoff L4 broad validation checkpoint" in stdout


def test_l4_09_documentation_checkpoint_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint import (
        build_l4_browser_start_dry_run_handoff_documentation_checkpoint,
    )

    payload = build_l4_browser_start_dry_run_handoff_documentation_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l4_09_documentation_checkpoint_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_dry_run_handoff_l4_documentation_freeze_readiness_checkpoint.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L4.9 Live adapter browser-start dry-run handoff L4 documentation freeze/readiness checkpoint",
        "L4.1 dry-run handoff contract",
        "L4.8 aggregate readiness gate CLI/readback",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L4.10 Live adapter browser-start dry-run handoff L4 broad validation checkpoint",
    ]
    for phrase in required:
        assert phrase in text
