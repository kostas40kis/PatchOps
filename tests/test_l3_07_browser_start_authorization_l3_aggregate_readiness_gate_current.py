from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_l3_7_aggregate_readiness_gate_payload_is_passive_and_green() -> None:
    from patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate import (
        build_l3_browser_start_authorization_aggregate_readiness_gate,
    )
    payload = build_l3_browser_start_authorization_aggregate_readiness_gate(PROJECT_ROOT)
    assert payload["patch"] == "L3.7"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["next_patch"] == "L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback"
    assert payload["startup_authorized"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["selenium_imported"] is False
    assert payload["missing_fixture_case_ids"] == []
    assert payload["missing_cli_commands"] == []
    assert payload["missing_repo_paths"] == []
    assert all(check["ok"] is True for check in payload["checks"])


def test_l3_7_aggregate_readiness_gate_json_smoke() -> None:
    completed = subprocess.run([sys.executable, "-m", "patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate", "--repo-root", str(PROJECT_ROOT), "--json", "--compact"], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=120)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L3.7"
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["baseline_decision"]["startup_authorized"] is False
    assert payload["fixture_matrix"]["ok"] is True
    assert payload["contract_gate"]["ok"] is True


def test_l3_7_aggregate_readiness_gate_text_readback_is_operator_safe() -> None:
    completed = subprocess.run([sys.executable, "-m", "patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate", "--repo-root", str(PROJECT_ROOT)], cwd=PROJECT_ROOT, text=True, capture_output=True, timeout=120)
    assert completed.returncode == 0, completed.stderr
    stdout = completed.stdout
    assert "L3.7 Browser Start Authorization Aggregate Readiness Gate" in stdout
    assert "Status     : PASS" in stdout
    assert "Startup    : authorized=false" in stdout
    assert "Browser    : started=False" in stdout
    assert "Session    : created=False" in stdout
    assert "ProfileDir : created=False" in stdout
    assert "SideEffects: []" in stdout
    assert "Filesystem : writes=[]" in stdout
    assert "Next patch : L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback" in stdout


def test_l3_7_aggregate_readiness_gate_does_not_import_selenium_or_browser_optional_dependencies() -> None:
    before = set(sys.modules)
    from patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate import (
        build_l3_browser_start_authorization_aggregate_readiness_gate,
    )
    payload = build_l3_browser_start_authorization_aggregate_readiness_gate(PROJECT_ROOT)
    assert payload["ok"] is True
    after = set(sys.modules)
    newly_loaded = after - before
    forbidden_roots = {"selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer"}
    imported = {root for root in forbidden_roots if any(name == root or name.startswith(root + ".") for name in newly_loaded)}
    assert imported == set()


def test_l3_7_aggregate_readiness_docs_are_present_and_passive() -> None:
    canonical = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.md"
    runner = PROJECT_ROOT / "docs" / "llm_browser_runner.md"
    assert canonical.exists()
    assert runner.exists()
    canonical_text = canonical.read_text(encoding="utf-8")
    runner_text = runner.read_text(encoding="utf-8")
    required = [
        "L3.7 Live adapter browser-start authorization L3 aggregate readiness gate",
        "no Selenium import",
        "no browser start",
        "no browser session creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback",
    ]
    for phrase in required:
        assert phrase in canonical_text
    assert "PATCHOPS_L3_07_BROWSER_START_AUTHORIZATION_AGGREGATE_READINESS_GATE_START" in runner_text
    assert "L3.7 Live adapter browser-start authorization L3 aggregate readiness gate" in runner_text
