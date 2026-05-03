from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from patchops import cli
from patchops.llm_browser import live_adapter

PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_BLOCKED = {
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
}


def test_live_adapter_readback_payload_is_passive_and_complete() -> None:
    payload = live_adapter.build_live_adapter_readback()
    assert payload["name"] == "llm_browser_live_adapter_skeleton"
    assert payload["patch"] == "L1.2"
    assert payload["ok"] is True
    assert payload["status"] == "PASSIVE_READBACK_ONLY"
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["side_effects_performed"] == []
    assert set(payload["blocked_operations"]) == EXPECTED_BLOCKED
    capabilities = {item["operation"]: item for item in payload["capabilities"]}
    for operation in EXPECTED_BLOCKED:
        assert capabilities[operation]["status"] == "blocked"
        assert capabilities[operation]["side_effect"] is True


def test_live_adapter_blocked_operations_raise_without_side_effects() -> None:
    for operation in sorted(EXPECTED_BLOCKED):
        with pytest.raises(live_adapter.LiveAdapterBlockedError) as excinfo:
            getattr(live_adapter, operation)()
        payload = excinfo.value.to_payload()
        assert payload["operation"] == operation
        assert payload["status"] == "blocked"
        assert payload["side_effect_performed"] is False
    assert live_adapter.build_live_adapter_readback()["side_effects_performed"] == []


def test_live_adapter_source_has_no_browser_dependency_imports() -> None:
    source_path = PROJECT_ROOT / "patchops" / "llm_browser" / "live_adapter.py"
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    forbidden = {"selenium", "webdriver_manager", "pyperclip", "psutil"}
    assert not (forbidden & imported_roots)


def test_live_adapter_module_cli_json_readback(capsys: pytest.CaptureFixture[str]) -> None:
    assert live_adapter.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["patch"] == "L1.2"
    assert payload["browser_started"] is False
    assert set(payload["blocked_operations"]) == EXPECTED_BLOCKED


def test_patchops_cli_live_adapter_json_readback(capsys: pytest.CaptureFixture[str]) -> None:
    try:
        result = cli.main(["llm-browser", "live-adapter", "--json"])
        code = 0 if result is None else result
    except SystemExit as exc:
        code = exc.code
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["patch"] == "L1.2"
    assert payload["optional_browser_dependencies_required"] is False
    assert payload["browser_session_created"] is False
    assert set(payload["blocked_operations"]) == EXPECTED_BLOCKED


def test_patchops_cli_live_adapter_subprocess_json_readback() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "live-adapter", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L1.2"
    assert payload["side_effects_performed"] == []
    assert set(payload["blocked_operations"]) == EXPECTED_BLOCKED
