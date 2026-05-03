from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l3_10_broad_validation_checkpoint_payload_is_passive_and_green() -> None:
    from patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint import (
        build_l3_browser_start_authorization_broad_validation_checkpoint,
    )

    payload = build_l3_browser_start_authorization_broad_validation_checkpoint(PROJECT_ROOT)
    assert payload["patch"] == "L3.10"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback"
    assert payload["startup_authorized"] is False
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["executed_validation_commands"] == []
    assert payload["missing_commands"] == []
    assert payload["missing_l1_l2_paths"] == []
    assert payload["missing_l3_paths"] == []
    assert payload["missing_safety_phrases"] == []
    assert payload["missing_progression_phrases"] == []
    assert payload["readiness_gate"]["ok"] is True
    assert payload["documentation_checkpoint"]["ok"] is True
    assert all(check["ok"] is True for check in payload["checks"])


def test_l3_10_broad_validation_checkpoint_json_smoke() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint",
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
    assert payload["patch"] == "L3.10"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["readiness_gate"]["ok"] is True
    assert payload["documentation_checkpoint"]["ok"] is True
    assert payload["browser_started"] is False


def test_l3_10_broad_validation_checkpoint_text_readback_is_operator_safe() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint",
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
    assert "L3 broad validation checkpoint" in stdout
    assert "Status     : PASS" in stdout
    assert "Startup    : authorized=false allowed=false" in stdout
    assert "Browser    : started=False" in stdout
    assert "Session    : created=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "executed=0" in stdout
    assert "Next patch : L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback" in stdout


def test_l3_10_broad_validation_checkpoint_does_not_import_selenium_or_optional_browser_dependencies() -> None:
    before = set(sys.modules)
    from patchops.llm_browser.live_adapter_browser_start_authorization_l3_broad_validation_checkpoint import (
        build_l3_browser_start_authorization_broad_validation_checkpoint,
    )

    payload = build_l3_browser_start_authorization_broad_validation_checkpoint(PROJECT_ROOT)
    assert payload["ok"] is True
    newly_loaded = set(sys.modules) - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l3_10_broad_validation_checkpoint_docs_are_present_and_passive() -> None:
    path = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    required = [
        "L3.10 Live adapter browser-start authorization L3 broad validation checkpoint",
        "L3.1 explicit browser-start authorization contract",
        "L3.8 aggregate readiness gate CLI/readback",
        "L3.9 documentation freeze/readiness checkpoint",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L3.11 Live adapter browser-start authorization L3 broad validation checkpoint CLI/readback",
    ]
    for phrase in required:
        assert phrase in text
