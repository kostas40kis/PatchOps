from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l5_10_broad_validation_checkpoint_payload_is_passive_and_green() -> None:
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint import (
        build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint,
    )

    payload = build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint(PROJECT_ROOT)
    assert payload["patch"] == "L5.10"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_driver_session_allowed"] is False
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
    assert payload["executed_validation_commands"] == []
    assert all(check["ok"] is True for check in payload["checks"])


def test_l5_10_broad_validation_checkpoint_json_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint",
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
    assert payload["patch"] == "L5.10"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["readiness_gate"]["ok"] is True
    assert payload["documentation_checkpoint"]["ok"] is True
    assert payload["browser_started"] is False
    assert payload["profile_directory_created"] is False


def test_l5_10_broad_validation_checkpoint_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint",
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
    assert "L5.10 Browser Start Supervised Launch Handoff L5 Broad Validation Checkpoint" in stdout
    assert "Status          : PASS" in stdout
    assert "Startup Allowed : False" in stdout
    assert "Browser Started : False" in stdout
    assert "Session Created : False" in stdout
    assert "Driver Created  : False" in stdout
    assert "Profile Created : False" in stdout
    assert "SideEffects     : []" in stdout
    assert "Filesystem      : writes=[]" in stdout
    assert "Next Patch      : L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback" in stdout


def test_l5_10_broad_validation_checkpoint_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint import (
        build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint,
    )

    payload = build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l5_10_broad_validation_checkpoint_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.md"
    assert canonical.exists()
    text = canonical.read_text(encoding="utf-8")
    required = [
        "L5.10 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint",
        "L5.1 supervised-launch handoff contract",
        "L5.9 documentation freeze/readiness checkpoint",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no adapter filesystem writes",
        "no click/download/paste/send/package-run side effect",
        "L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback",
    ]
    for phrase in required:
        assert phrase in text
