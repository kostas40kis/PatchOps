from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops import cli
from patchops.llm_browser import commands


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _llm_browser_choices() -> set[str]:
    parser = commands.build_parser()
    subparsers = [
        action
        for action in parser._actions
        if action.__class__.__name__ == "_SubParsersAction"
    ]
    assert len(subparsers) == 1
    return set(subparsers[0].choices.keys())


def test_startup_gate_llm_browser_parser_surface_is_registered() -> None:
    choices = _llm_browser_choices()
    assert "startup-gate" in choices
    assert "live-adapter" in choices


def test_patchops_cli_startup_gate_json_readback(capsys) -> None:
    try:
        result = cli.main(["llm-browser", "startup-gate", "--json", "--compact"])
        code = 0 if result is None else result
    except SystemExit as exc:
        code = int(exc.code or 0)
    assert code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["patch"] == "L1.4"
    assert payload["status"] == "PASSIVE_STARTUP_GATE_SCAFFOLD"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []
    assert payload["optional_browser_dependencies_required"] is False


def test_patchops_cli_startup_gate_subprocess_json_readback() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-gate", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["patch"] == "L1.4"
    assert payload["status"] == "PASSIVE_STARTUP_GATE_SCAFFOLD"
    assert payload["startup_allowed"] is False
    assert payload["browser_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["side_effects_performed"] == []


def test_patchops_cli_startup_gate_text_readback() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-gate"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "PatchOps LLM browser live adapter startup gate scaffold" in completed.stdout
    assert "Startup    : allowed=False" in completed.stdout
    assert "Browser    : not started" in completed.stdout
    assert "SideEffects: []" in completed.stdout


def test_startup_gate_cli_surface_does_not_enable_browser_side_effects() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", "startup-gate", "--json", "--compact"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    payload = json.loads(completed.stdout)
    assert payload["forbidden_import_roots"] == [
        "selenium",
        "webdriver_manager",
        "pyperclip",
        "psutil",
    ]
    assert payload["required_explicit_acknowledgements"] == [
        "operator_confirms_dedicated_browser_profile",
        "operator_confirms_manual_login_only",
        "operator_confirms_no_auto_send",
        "operator_confirms_visible_artifact_only",
        "operator_confirms_patchops_remains_source_of_truth",
    ]
