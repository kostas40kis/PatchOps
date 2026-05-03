from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_startup_gate as gate

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_startup_gate_readback_is_passive_and_blocks_startup() -> None:
    payload = gate.build_startup_gate_readback()
    assert payload["ok"] is True
    assert payload["status"] == gate.GATE_STATUS
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []
    assert payload["existing_live_adapter_status"] == "PASSIVE_READBACK_ONLY"
    assert set(gate.SIDE_EFFECT_OPERATION_NAMES).issubset(set(payload["existing_live_adapter_blocked_operations"]))


def test_startup_gate_requires_explicit_acknowledgements_but_still_blocks_in_l1_4() -> None:
    default_decision = gate.evaluate_startup_request()
    assert default_decision["startup_allowed"] is False
    assert default_decision["status"] == gate.DECISION_STATUS_BLOCKED
    assert set(default_decision["missing_acknowledgements"]) == set(gate.REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS)
    assert default_decision["side_effects_performed"] == []

    permissive_decision = gate.evaluate_startup_request(
        gate.LiveAdapterStartupRequest(
            browser="edge",
            requested=True,
            operator_confirms_dedicated_browser_profile=True,
            operator_confirms_manual_login_only=True,
            operator_confirms_no_auto_send=True,
            operator_confirms_visible_artifact_only=True,
            operator_confirms_patchops_remains_source_of_truth=True,
            allow_start_browser=True,
            allow_read_page=True,
            allow_click_download=True,
            allow_patchops_run=True,
            allow_paste_to_composer=True,
            allow_send_submit=True,
        )
    )
    assert permissive_decision["missing_acknowledgements"] == []
    assert permissive_decision["startup_allowed"] is False
    assert permissive_decision["browser_started"] is False
    assert permissive_decision["browser_session_created"] is False
    assert permissive_decision["side_effects_performed"] == []
    assert "l1_4_scaffold_does_not_start_browsers" in permissive_decision["blockers"]


def test_startup_gate_has_no_optional_browser_dependency_imports() -> None:
    source = Path(gate.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert not (set(gate.FORBIDDEN_IMPORT_ROOTS) & imported_roots)


def test_assert_startup_gate_safe_returns_true() -> None:
    assert gate.assert_startup_gate_safe() is True


def test_startup_gate_module_json_cli_smoke() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.llm_browser.live_adapter_startup_gate", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["status"] == gate.GATE_STATUS
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["side_effects_performed"] == []
    assert payload["next_patch"] == gate.NEXT_PATCH


def test_startup_gate_docs_contract() -> None:
    doc = (PROJECT_ROOT / "docs" / "llm_browser_live_adapter_startup_gate.md").read_text(encoding="utf-8")
    required = [
        "L1.4 Live adapter explicit startup gate scaffold",
        "startup_allowed: false",
        "no Selenium import",
        "no browser starts",
        "manual login only",
        "no auto-send",
        "PatchOps remains the source of truth",
        "L1.5 Live adapter startup gate CLI/readback",
    ]
    missing = [phrase for phrase in required if phrase not in doc]
    assert not missing
